#!/usr/bin/env python3
"""
Course Generator App

This script uses the GeminiTeacher coursemaker module to generate structured courses
from input content, using configuration from a YAML file.
"""

import argparse
import os
import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from geminiteacher.coursemaker import create_course, configure_gemini_llm
from geminiteacher.converter import convert_to_markdown


def configure_logging(log_file=None, verbose=False):
    """
    Configure logging for the application.
    
    Parameters
    ----------
    log_file : str, optional
        Path to the log file
    verbose : bool, optional
        Whether to use verbose (DEBUG) logging
    
    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Console handler
        ]
    )
    
    # Create a logger for this application
    logger = logging.getLogger("generate_course")
    
    # Add file handler if log_file is provided
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
        
        # Add the file handler to the logger
        logger.addHandler(file_handler)
        
        # Also add the file handler to the geminiteacher loggers
        for module in ["geminiteacher", "geminiteacher.coursemaker", "geminiteacher.parallel"]:
            module_logger = logging.getLogger(module)
            module_logger.addHandler(file_handler)
            module_logger.setLevel(log_level)
    
    # Set environment variable with log level for worker processes
    os.environ["GeminiTeacher_LOG_LEVEL"] = str(log_level)
    
    return logger


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Parameters
    ----------
    config_path : str
        Path to the YAML configuration file
        
    Returns
    -------
    Dict[str, Any]
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def setup_environment(config: Dict[str, Any]) -> None:
    """
    Set up environment variables from configuration.
    
    Parameters
    ----------
    config : Dict[str, Any]
        Configuration dictionary
    """
    # Set Google API key as environment variable
    if 'api' in config and 'google_api_key' in config['api']:
        os.environ['GOOGLE_API_KEY'] = config['api']['google_api_key']
    else:
        print("Warning: Google API key not found in configuration")


def read_input_content(input_path: str) -> str:
    """
    Read content from an input file.
    
    Parameters
    ----------
    input_path : str
        Path to the input file
        
    Returns
    -------
    str
        Content of the input file
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)


def read_custom_prompt(file_path: str) -> str:
    """
    Read custom prompt instructions from a file.
    
    Parameters
    ----------
    file_path : str
        Path to the file containing custom prompt instructions
        
    Returns
    -------
    str
        Content of the custom prompt file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            custom_prompt = f.read().strip()
        return custom_prompt
    except Exception as e:
        print(f"Error reading custom prompt file: {e}")
        sys.exit(1)


def save_chapter_to_file(course_title: str, chapter: Any, chapter_index: int, output_dir: str) -> str:
    """
    Save a single chapter to a file.
    
    Parameters
    ----------
    course_title : str
        Title of the course
    chapter : Any
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
    
    # Sanitize course title for filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in course_title)
    safe_title = safe_title.replace(" ", "_")
    
    # Create chapter filename
    chapter_filename = f"{safe_title}_chapter_{chapter_index+1:02d}.md"
    chapter_path = output_path / chapter_filename
    
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


def save_course_to_files(course_title: str, course_content: Dict[str, Any], output_dir: str) -> None:
    """
    Save generated course to files.
    
    Parameters
    ----------
    course_title : str
        Title of the course
    course_content : Dict[str, Any]
        Course content dictionary
    output_dir : str
        Directory to save the course files
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Sanitize course title for filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in course_title)
    safe_title = safe_title.replace(" ", "_")
    
    # Save course summary
    with open(output_path / f"{safe_title}_summary.md", 'w', encoding='utf-8') as f:
        f.write(f"# {course_title}\n\n")
        f.write(course_content.summary)
    
    # Save each chapter
    for i, chapter in enumerate(course_content.chapters):
        save_chapter_to_file(course_title, chapter, i, output_dir)


def create_course_with_progressive_save(
    content: str,
    course_title: str,
    output_dir: str,
    llm=None,
    temperature: float = 0.0,
    verbose: bool = False,
    max_chapters: int = 10,
    fixed_chapter_count: bool = False,
    custom_prompt: Optional[str] = None,
    logger=None
) -> Any: # Changed return type hint to Any as Course is not imported here
    """
    Create a course and save each chapter as it's generated.
    
    This function wraps the create_course function from geminiteacher.coursemaker
    but saves each chapter to disk immediately after it's generated.
    
    Parameters
    ----------
    content : str
        The raw content to transform into a course
    course_title : str
        Title of the course
    output_dir : str
        Directory to save the course files
    llm : BaseLanguageModel, optional
        Language model to use
    temperature : float, optional
        Temperature for generation
    verbose : bool, optional
        Whether to print progress messages
    max_chapters : int, optional
        Maximum number of chapters
    fixed_chapter_count : bool, optional
        Whether to use fixed chapter count
    custom_prompt : Optional[str], optional
        Custom prompt instructions
    logger : logging.Logger, optional
        Logger for messages
    
    Returns
    -------
    Course
        The generated course object
    """
    from geminiteacher.coursemaker import Course, ChapterContent, generate_toc, generate_chapter, generate_summary
    
    # Initialize the course with the original content
    course = Course(content=content)
    
    # If no LLM is provided, configure Gemini
    if llm is None:
        if verbose:
            print("Configuring default Gemini LLM...")
        from geminiteacher.coursemaker import get_default_llm
        llm = get_default_llm(temperature)
    
    # Step 1: Generate the table of contents
    if verbose:
        print(f"Generating table of contents (max {max_chapters} chapters)...")
        if fixed_chapter_count:
            print(f"Using fixed chapter count mode: exactly {max_chapters} chapters")
        if custom_prompt:
            print("Using custom prompt for chapter generation")
    
    chapter_titles = generate_toc(
        content, 
        llm=llm, 
        temperature=temperature, 
        max_chapters=max_chapters,
        fixed_chapter_count=fixed_chapter_count
    )
    
    if verbose:
        print(f"Generated {len(chapter_titles)} chapter titles")
    
    # Step 2: Generate content for each chapter and save progressively
    chapters = []
    for i, title in enumerate(chapter_titles):
        if verbose:
            print(f"Generating chapter {i+1}/{len(chapter_titles)}: {title}")
        if logger:
            logger.info(f"Generating chapter {i+1}/{len(chapter_titles)}: {title}")
        
        # Generate the chapter
        chapter = generate_chapter(
            title, 
            content, 
            llm=llm, 
            temperature=temperature,
            custom_prompt=custom_prompt
        )
        chapters.append(chapter)
        
        # Save the chapter immediately
        chapter_path = save_chapter_to_file(course_title, chapter, i, output_dir)
        if logger:
            logger.info(f"Saved chapter {i+1} to {chapter_path}")
        if verbose:
            print(f"Saved chapter {i+1} to {chapter_path}")
    
    course.chapters = chapters
    
    # Step 3: Generate the course summary
    if chapters:
        if verbose:
            print("Generating course summary...")
        if logger:
            logger.info("Generating course summary...")
            
        course.summary = generate_summary(content, chapters, llm=llm, temperature=temperature)
        
        # Save the summary
        output_path = Path(output_dir)
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in course_title)
        safe_title = safe_title.replace(" ", "_")
        summary_path = output_path / f"{safe_title}_summary.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# {course_title}\n\n")
            f.write(course.summary)
            
        if logger:
            logger.info(f"Saved course summary to {summary_path}")
        if verbose:
            print(f"Saved course summary to {summary_path}")
            print("Course generation complete!")
    
    return course


def main():
    """Main function to run the course generator."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate a structured course from input content")
    parser.add_argument("input", help="Path to the input content file")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--title", default="Generated Course", help="Title of the course")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--max-chapters", type=int, default=10, help="Maximum number of chapters to generate")
    parser.add_argument("--fixed-chapters", action="store_true", 
                      help="If set, generates exactly --max-chapters chapters instead of adapting based on content complexity")
    parser.add_argument("--custom-prompt", help="Path to a file containing custom instructions for chapter generation")
    parser.add_argument("--log-file", help="Path to log file (default: output/generation_log.txt)")
    parser.add_argument("--parallel", action="store_true", help="Use parallel processing for chapter generation")
    parser.add_argument("--max-workers", type=int, help="Maximum number of worker processes for parallel generation")
    parser.add_argument("--min-delay", type=float, default=0.1, help="Minimum delay between API requests in seconds (default: 0.1)")
    parser.add_argument("--max-delay", type=float, default=0.5, help="Maximum delay between API requests in seconds (default: 0.5)")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum number of retry attempts per chapter (default: 3)")
    args = parser.parse_args()
    
    # Get absolute path to config file (relative to script location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, args.config)
    
    # Load configuration
    config = load_config(config_path)
    
    # Get output directory
    output_dir = config.get('course', {}).get('output_dir', 'output')
    output_dir = os.path.join(script_dir, output_dir)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up logging
    log_file = args.log_file if args.log_file else os.path.join(output_dir, f"generation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    logger = configure_logging(log_file, args.verbose)
    
    logger.info(f"Starting course generation with config: {config_path}")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Mode: {'Fixed' if args.fixed_chapters else 'Adaptive'} chapter count (max: {args.max_chapters})")
    
    if args.parallel:
        logger.info(f"Using parallel processing with max_workers={args.max_workers or 'auto'}")
        logger.info(f"API request delay range: {args.min_delay}s - {args.max_delay}s")
        logger.info(f"Max retries per chapter: {args.max_retries}")
    
    # Read custom prompt if provided
    custom_prompt = None
    if args.custom_prompt:
        try:
            custom_prompt = read_custom_prompt(args.custom_prompt)
            logger.info(f"Using custom prompt from: {args.custom_prompt}")
        except Exception as e:
            logger.error(f"Error reading custom prompt file: {e}", exc_info=True)
            sys.exit(1)
    
    # Get API key from configuration
    api_key = config.get('api', {}).get('google_api_key')
    if not api_key:
        logger.error("Google API key not found in configuration")
        sys.exit(1)
    
    # Set up environment variables (for backward compatibility)
    setup_environment(config)
    
    # Define text-based extensions that do not need conversion
    text_extensions = {".txt", ".md"}
    input_path = Path(args.input)

    # Convert non-text files to Markdown before processing
    if input_path.suffix.lower() not in text_extensions:
        logger.info(f"Input file is not plain text. Converting {args.input} to Markdown...")
        try:
            content = convert_to_markdown(input_path, output_dir=output_dir)
            logger.info(f"Conversion successful. Markdown saved to {output_dir}/{input_path.stem}.md")
        except Exception as e:
            logger.error(f"Error converting file to Markdown: {e}", exc_info=True)
            sys.exit(1)
    else:
        # Read input content directly for text files
        content = read_input_content(args.input)
    
    # Configure the LLM
    model_name = config.get('model', {}).get('name', 'gemini-1.5-pro')
    temperature = config.get('model', {}).get('temperature', 0.0)
    
    logger.info(f"Configuring LLM with model: {model_name} (temperature: {temperature})")
    
    try:
        # Pass the API key directly to avoid authentication issues
        from geminiteacher.coursemaker import configure_gemini_llm
        llm = configure_gemini_llm(
            api_key=api_key,
            model_name=model_name, 
            temperature=temperature
        )
        
        # Generate the course with verbose logging
        logger.info(f"Generating course: {args.title}")
        if args.fixed_chapters:
            logger.info(f"Mode: Fixed chapter count (exactly {args.max_chapters} chapters)")
        else:
            logger.info(f"Mode: Adaptive chapter count (1-{args.max_chapters} chapters based on content)")
        
        if custom_prompt:
            logger.info("Using custom prompt for chapter generation")
        
        if args.parallel:
            # Use parallel processing for chapter generation
            from geminiteacher.coursemaker import create_course_parallel
            
            try:
                course = create_course_parallel(
                    content, 
                    llm=llm, 
                    temperature=temperature,
                    verbose=args.verbose,
                    max_chapters=args.max_chapters,
                    fixed_chapter_count=args.fixed_chapters,
                    custom_prompt=custom_prompt,
                    max_workers=args.max_workers,
                    delay_range=(args.min_delay, args.max_delay),
                    max_retries=args.max_retries,
                    course_title=args.title,
                    output_dir=output_dir
                )
                
                # Save the course summary (chapters are already saved during generation)
                # Create the course directory if it doesn't exist
                safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in args.title)
                safe_title = safe_title.replace(" ", "_")
                course_dir = Path(output_dir) / safe_title
                course_dir.mkdir(parents=True, exist_ok=True)
                
                # Save the course summary
                with open(course_dir / "summary.md", 'w', encoding='utf-8') as f:
                    f.write(f"# {args.title}\n\n")
                    f.write(course.summary)
                
                logger.info(f"Successfully generated course with {len(course.chapters)} chapters in parallel mode")
                logger.info(f"Output saved to: {course_dir}")
            except Exception as e:
                logger.error(f"Parallel course generation failed: {str(e)}", exc_info=True)
                logger.error("Try running again with sequential mode (without --parallel)")
                sys.exit(1)
        else:
            # Use the progressive save version instead of the original create_course
            course = create_course_with_progressive_save(
                content, 
                args.title,
                output_dir,
                llm=llm, 
                temperature=temperature,
                verbose=args.verbose,
                max_chapters=args.max_chapters,
                fixed_chapter_count=args.fixed_chapters,
                custom_prompt=custom_prompt,
                logger=logger
            )
            
            logger.info(f"Course generated with {len(course.chapters)} chapters")
            logger.info(f"Output saved to: {output_dir}")
        
        logger.info(f"Log file: {log_file}")
        
        print(f"Course generated with {len(course.chapters)} chapters")
        print(f"Output saved to: {output_dir}/{safe_title if args.parallel else ''}")
        print(f"Log file: {log_file}")
        
    except Exception as e:
        logger.error(f"Error generating course: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 