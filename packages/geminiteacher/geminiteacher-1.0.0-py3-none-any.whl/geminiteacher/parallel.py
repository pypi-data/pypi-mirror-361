"""Parallel processing utilities for the GeminiTeacher coursemaker module."""
import random
import time
import logging
import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import List, Optional, Callable, Any, TypeVar, Dict, Tuple
from pathlib import Path

from langchain_core.language_models import BaseLanguageModel

from geminiteacher.coursemaker import ChapterContent, generate_chapter

# Type variable for generic return type
T = TypeVar('T')

# Set up a process-safe logger configuration
def _configure_worker_logger():
    """Configure a logger for worker processes."""
    logger = logging.getLogger("geminiteacher.parallel")
    # Check if handlers are already configured to avoid duplicate logs
    if not logger.handlers:
        # Get the log level from the parent process if possible
        log_level = os.environ.get("GeminiTeacher_LOG_LEVEL", "INFO")
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(numeric_level)
        
        # Create a handler that writes to stderr
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(processName)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def generate_chapter_with_retry(
    chapter_title: str, 
    content: str, 
    llm: Optional[BaseLanguageModel] = None,
    temperature: float = 0.0,
    custom_prompt: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> ChapterContent:
    """
    Generate a chapter with retry logic for handling API failures.
    
    This function wraps the generate_chapter function with retry logic to handle
    transient API errors, timeouts, or empty responses.
    
    Parameters
    ----------
    chapter_title : str
        The title of the chapter to generate.
    content : str
        The raw content to use for generating the chapter.
    llm : Optional[BaseLanguageModel], optional
        The language model to use. If None, a default model will be configured.
    temperature : float, optional
        The temperature setting for generation. Default is 0.0.
    custom_prompt : Optional[str], optional
        Custom instructions to append to the chapter generation prompt.
    max_retries : int, optional
        Maximum number of retry attempts. Default is 3.
    retry_delay : float, optional
        Base delay between retries in seconds. Default is 1.0.
        
    Returns
    -------
    ChapterContent
        The generated chapter content.
        
    Notes
    -----
    This function implements an exponential backoff strategy for retries,
    with each retry attempt waiting longer than the previous one.
    """
    logger = logging.getLogger("geminiteacher.parallel")
    
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Generating chapter '{chapter_title}' (attempt {attempt + 1}/{max_retries + 1})")
            chapter = generate_chapter(
                chapter_title=chapter_title,
                content=content,
                llm=llm,
                temperature=temperature,
                custom_prompt=custom_prompt
            )
            
            # Check if we got a valid response (non-empty explanation)
            if chapter.explanation.strip():
                logger.info(f"Successfully generated chapter '{chapter_title}' (length: {len(chapter.explanation)} chars)")
                return chapter
            else:
                raise ValueError("Empty chapter explanation received")
                
        except Exception as e:
            if attempt < max_retries:
                # Calculate backoff with jitter
                backoff = retry_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Chapter generation failed for '{chapter_title}' "
                    f"(attempt {attempt + 1}/{max_retries + 1}): {str(e)}. "
                    f"Retrying in {backoff:.2f}s..."
                )
                time.sleep(backoff)
            else:
                logger.error(
                    f"All retry attempts failed for chapter '{chapter_title}'. "
                    f"Last error: {str(e)}"
                )
                # Return a basic chapter with error information
                return ChapterContent(
                    title=chapter_title,
                    summary="Error: Failed to generate chapter content after multiple attempts.",
                    explanation=f"The chapter generation process encountered repeated errors: {str(e)}",
                    extension="Please try regenerating this chapter or check your API configuration."
                )


def parallel_map_with_delay(
    func: Callable[..., T],
    items: List[Any],
    max_workers: Optional[int] = None,
    delay_range: tuple = (0.1, 0.5),
    **kwargs
) -> List[T]:
    """
    Execute a function on multiple items in parallel with a delay between submissions.
    
    This function uses ProcessPoolExecutor to parallelize the execution of a function
    across multiple items, while introducing a random delay between task submissions
    to avoid overwhelming external APIs with simultaneous requests.
    
    Parameters
    ----------
    func : Callable[..., T]
        The function to execute in parallel.
    items : List[Any]
        The list of items to process.
    max_workers : Optional[int], optional
        Maximum number of worker processes. If None, uses the default
        (typically the number of CPU cores).
    delay_range : tuple, optional
        Range (min, max) in seconds for the random delay between task submissions.
        Default is (0.1, 0.5).
    **kwargs
        Additional keyword arguments to pass to the function.
        
    Returns
    -------
    List[T]
        List of results in the same order as the input items.
        
    Examples
    --------
    >>> def process_item(item, factor=1):
    ...     return item * factor
    >>> items = [1, 2, 3, 4, 5]
    >>> results = parallel_map_with_delay(process_item, items, factor=2)
    >>> print(results)
    [2, 4, 6, 8, 10]
    """
    logger = logging.getLogger("geminiteacher.parallel")
    results = []
    total_items = len(items)
    
    # Export the current log level to the environment for worker processes
    os.environ["GeminiTeacher_LOG_LEVEL"] = logger.getEffectiveLevel().__str__()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks with a delay between submissions
        futures = []
        for i, item in enumerate(items):
            # Add a small random delay to avoid overwhelming the API
            delay = random.uniform(delay_range[0], delay_range[1])
            logger.debug(f"Submitting task {i+1}/{total_items} with delay: {delay:.2f}s")
            time.sleep(delay)
            
            # Submit the task to the process pool
            future = executor.submit(func, item, **kwargs)
            futures.append(future)
            logger.info(f"Submitted task {i+1}/{total_items}")
        
        # Collect results in the original order
        for i, future in enumerate(futures):
            try:
                logger.info(f"Waiting for task {i+1}/{total_items} to complete")
                result = future.result()
                results.append(result)
                logger.info(f"Completed task {i+1}/{total_items}")
            except Exception as e:
                logger.error(f"Task {i+1}/{total_items} failed: {str(e)}")
                # Re-raise the exception to maintain the expected behavior
                raise
    
    return results


def _worker_generate_chapter(
    chapter_item: tuple,
    content: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-1.5-pro",
    temperature: float = 0.0,
    custom_prompt: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> ChapterContent:
    """
    Worker function to generate a chapter with its own LLM instance.
    
    This function initializes a new LLM instance within the worker process,
    avoiding the need to pickle and pass LLM objects between processes.
    
    Parameters
    ----------
    chapter_item : tuple
        Tuple containing (index, chapter_title)
    content : str
        The raw content to use for generating the chapter.
    api_key : Optional[str], optional
        The Google API key for LLM access. If None, uses environment variable.
    model_name : str, optional
        The name of the LLM model to use. Default is "gemini-1.5-pro".
    temperature : float, optional
        The temperature setting for generation. Default is 0.0.
    custom_prompt : Optional[str], optional
        Custom instructions to append to the chapter generation prompt.
    max_retries : int, optional
        Maximum number of retry attempts. Default is 3.
    retry_delay : float, optional
        Base delay between retries in seconds. Default is 1.0.
        
    Returns
    -------
    ChapterContent
        The generated chapter content.
    """
    # Configure a process-specific logger
    logger = _configure_worker_logger()
    
    # Unpack the chapter item
    idx, chapter_title = chapter_item
    
    logger.info(f"Worker process starting on chapter {idx+1}: '{chapter_title}'")
    
    try:
        # Import here to avoid circular imports and ensure imports happen in the worker process
        from geminiteacher.coursemaker import configure_gemini_llm
        
        # Initialize a new LLM instance within this worker process
        logger.info(f"Configuring LLM for chapter {idx+1}: '{chapter_title}'")
        llm = configure_gemini_llm(
            api_key=api_key,
            model_name=model_name,
            temperature=temperature
        )
        
        # Generate the chapter with retry logic
        logger.info(f"Starting generation of chapter {idx+1}: '{chapter_title}'")
        chapter = generate_chapter_with_retry(
            chapter_title=chapter_title,
            content=content,
            llm=llm,
            temperature=temperature,
            custom_prompt=custom_prompt,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        logger.info(f"Completed generation of chapter {idx+1}: '{chapter_title}'")
        return chapter
    
    except Exception as e:
        logger.error(f"Failed to generate chapter {idx+1}: '{chapter_title}' - Error: {str(e)}")
        # Return a basic error chapter rather than propagating the exception
        return ChapterContent(
            title=chapter_title,
            summary=f"Error: Failed to generate chapter {idx+1}",
            explanation=f"The chapter generation process encountered an error: {str(e)}",
            extension="Please try regenerating this chapter or check your API configuration."
        )


def save_chapter_to_file(course_title: str, chapter: ChapterContent, chapter_index: int, output_dir: str) -> str:
    """
    Save a single chapter to a file.
    
    Parameters
    ----------
    course_title : str
        Title of the course
    chapter : ChapterContent
        Chapter content object
    chapter_index : int
        Index of the chapter (0-based)
    output_dir : str
        Directory to save the chapter file
        
    Returns
    -------
    str
        Path to the saved chapter file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create course-specific directory
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in course_title)
    safe_title = safe_title.replace(" ", "_")
    course_dir = output_path / safe_title
    course_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize chapter title for filename
    chapter_title_safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in chapter.title)
    chapter_title_safe = chapter_title_safe.replace(" ", "_")
    
    # Create chapter filename with chapter number and title
    chapter_filename = f"chapter_{chapter_index+1:02d}_{chapter_title_safe}.md"
    chapter_path = course_dir / chapter_filename
    
    # Save chapter content
    with open(chapter_path, 'w', encoding='utf-8') as f:
        f.write(f"# {chapter.title}\n\n")
        f.write("## Summary\n\n")
        f.write(f"{chapter.summary}\n\n")
        f.write("## Explanation\n\n")
        f.write(f"{chapter.explanation}\n\n")
        f.write("## Extension\n\n")
        f.write(f"{chapter.extension}\n")
    
    return str(chapter_path)


def _worker_generate_and_save_chapter(
    chapter_item: tuple,
    content: str,
    course_title: str,
    output_dir: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-1.5-pro",
    temperature: float = 0.0,
    custom_prompt: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Tuple[int, ChapterContent, str]:
    """
    Worker function to generate a chapter and save it to disk.
    
    Parameters
    ----------
    chapter_item : tuple
        Tuple containing (index, chapter_title)
    content : str
        The raw content to use for generating the chapter.
    course_title : str
        Title of the course
    output_dir : str
        Directory to save the chapter file
    api_key : Optional[str], optional
        The Google API key for LLM access. If None, uses environment variable.
    model_name : str, optional
        The name of the LLM model to use. Default is "gemini-1.5-pro".
    temperature : float, optional
        The temperature setting for generation. Default is 0.0.
    custom_prompt : Optional[str], optional
        Custom instructions to append to the chapter generation prompt.
    max_retries : int, optional
        Maximum number of retry attempts. Default is 3.
    retry_delay : float, optional
        Base delay between retries in seconds. Default is 1.0.
        
    Returns
    -------
    Tuple[int, ChapterContent, str]
        Tuple containing (chapter_index, chapter_content, file_path)
    """
    logger = _configure_worker_logger()
    
    # Unpack the chapter item
    idx, chapter_title = chapter_item
    
    # Generate the chapter
    chapter = _worker_generate_chapter(
        chapter_item,
        content,
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        custom_prompt=custom_prompt,
        max_retries=max_retries,
        retry_delay=retry_delay
    )
    
    # Save the chapter to disk
    try:
        file_path = save_chapter_to_file(course_title, chapter, idx, output_dir)
        logger.info(f"Saved chapter {idx+1}: '{chapter_title}' to {file_path}")
        return (idx, chapter, file_path)
    except Exception as e:
        logger.error(f"Failed to save chapter {idx+1}: '{chapter_title}' - Error: {str(e)}")
        return (idx, chapter, "")


def parallel_generate_chapters(
    chapter_titles: List[str],
    content: str,
    llm: Optional[BaseLanguageModel] = None,
    temperature: float = 0.0,
    custom_prompt: Optional[str] = None,
    max_workers: Optional[int] = None,
    delay_range: tuple = (0.1, 0.5),
    max_retries: int = 3,
    course_title: str = "course",
    output_dir: str = "output"
) -> List[ChapterContent]:
    """
    Generate multiple chapters in parallel with retry logic and rate limiting.
    
    This function orchestrates the parallel generation of multiple chapters,
    handling API rate limits and retrying failed requests. Each chapter is
    saved to disk as soon as it's generated.
    
    Parameters
    ----------
    chapter_titles : List[str]
        List of chapter titles to generate.
    content : str
        The raw content to use for generating chapters.
    llm : Optional[BaseLanguageModel], optional
        The language model to use. If None, a default model will be configured.
    temperature : float, optional
        The temperature setting for generation. Default is 0.0.
    custom_prompt : Optional[str], optional
        Custom instructions to append to the chapter generation prompt.
    max_workers : Optional[int], optional
        Maximum number of worker processes. If None, uses the default.
    delay_range : tuple, optional
        Range (min, max) in seconds for the random delay between task submissions.
        Default is (0.1, 0.5).
    max_retries : int, optional
        Maximum number of retry attempts per chapter. Default is 3.
    course_title : str, optional
        Title of the course for saving files. Default is "course".
    output_dir : str, optional
        Directory to save the chapter files. Default is "output".
        
    Returns
    -------
    List[ChapterContent]
        List of generated chapter contents in the same order as the input titles.
    """
    logger = logging.getLogger("geminiteacher.parallel")
    logger.info(f"Starting parallel generation of {len(chapter_titles)} chapters with {max_workers or multiprocessing.cpu_count()} workers")
    
    # Get API key from the LLM if provided or environment
    api_key = None
    model_name = "gemini-1.5-pro"
    
    if llm is not None:
        # Try to extract API key and model name from the provided LLM
        try:
            # This assumes LLM is a ChatGoogleGenerativeAI instance
            api_key = getattr(llm, "google_api_key", None)
            model_name = getattr(llm, "model", model_name)
            logger.info(f"Using model: {model_name}")
        except Exception:
            logger.warning("Could not extract API key from provided LLM, will use environment variables")
    
    # Create a list of (index, chapter_title) tuples to preserve order
    indexed_titles = list(enumerate(chapter_titles))
    
    logger.info(f"Using delay range: {delay_range[0]}-{delay_range[1]}s between tasks")
    logger.info(f"Saving chapters progressively to {output_dir}/{course_title}/")
    
    # Generate chapters in parallel with delay between submissions and save each one as it completes
    results = parallel_map_with_delay(
        _worker_generate_and_save_chapter,
        indexed_titles,
        max_workers=max_workers,
        delay_range=delay_range,
        content=content,
        course_title=course_title,
        output_dir=output_dir,
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        custom_prompt=custom_prompt,
        max_retries=max_retries,
        retry_delay=1.0
    )
    
    # Extract just the chapter content from the results (idx, chapter, file_path)
    chapters = [result[1] for result in results]
    
    logger.info(f"Completed parallel generation of {len(chapters)} chapters")
    return chapters 