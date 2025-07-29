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

from geminiteacher import (
    create_course, 
    configure_gemini_llm, 
    Course,
    generate_toc,
    generate_chapter,
    generate_summary
)
from geminiteacher.parallel import parallel_generate_chapters


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
    logger = logging.getLogger("geminiteacher.app")
    
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
    if not os.path.exists(config_path):
        # If the config file doesn't exist and it's the default config.yaml, return empty dict
        if config_path == "config.yaml":
            return {}
        else:
            # If a specific config file was requested but doesn't exist, that's an error
            print(f"Error: Config file '{config_path}' not found")
            sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config if config else {}
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
    
    # Create chapter filename with chapter number and title
    chapter_title_safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in chapter.title)
    chapter_title_safe = chapter_title_safe.replace(" ", "_")
    chapter_filename = f"{safe_title}_chapter_{chapter_index+1:02d}_{chapter_title_safe}.md"
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


def save_course_to_files(course_title: str, course_content: Course, output_dir: str) -> None:
    """
    Save course content to files.
    
    Parameters
    ----------
    course_title : str
        Title of the course
    course_content : Course
        Course content object
    output_dir : str
        Directory to save the course files
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Sanitize course title for filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in course_title)
    safe_title = safe_title.replace(" ", "_")
    
    # Save each chapter to a separate file
    for i, chapter in enumerate(course_content.chapters):
        save_chapter_to_file(safe_title, chapter, i, output_dir)
    
    # Save course summary
    summary_filename = f"{safe_title}_summary.md"
    summary_path = output_path / summary_filename
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# {course_title} - Course Summary\n\n")
        f.write(f"{course_content.summary}\n\n")
        f.write("## Chapters\n\n")
        
        for i, chapter in enumerate(course_content.chapters):
            f.write(f"{i+1}. {chapter.title}\n")


def create_course_with_progressive_save(
    content: str,
    course_title: str,
    output_dir: str,
    llm=None,
    model_name: str = "gemini-1.5-pro",
    temperature: float = 0.0,
    verbose: bool = False,
    max_chapters: int = 10,
    fixed_chapter_count: bool = False,
    custom_prompt: Optional[str] = None,
    max_workers: Optional[int] = None,
    delay_range: tuple = (0.1, 0.5),
    max_retries: int = 3,
    logger=None
) -> Course:
    """
    Generate a course with progressive saving of chapters.

    This function handles the entire workflow:
    1. Reads content and prompt files if paths are provided.
    2. Configures the LLM.
    3. Generates the table of contents.
    4. Generates chapters (sequentially or in parallel).
    5. Saves each chapter to a file as it's completed.
    6. Generates and saves the final course summary.
    
    Parameters
    ----------
    content : str
        The raw content for the course, or a path to the content file.
    course_title : str
        Title of the course.
    output_dir : str
        Directory to save the course files.
    llm : optional
        Pre-configured LLM instance. If None, one will be created.
    model_name : str, optional
        Name of the Gemini model to use if `llm` is not provided.
    temperature : float, optional
        Temperature for generation.
    verbose : bool, optional
        Enable verbose logging.
    max_chapters : int, optional
        Maximum number of chapters.
    fixed_chapter_count : bool, optional
        Generate exactly `max_chapters`.
    custom_prompt : str, optional
        Custom prompt instructions, or a path to the prompt file.
    max_workers : int, optional
        Number of parallel workers. If > 1, enables parallel mode.
    delay_range : tuple, optional
        Min/max delay for parallel requests.
    max_retries : int, optional
        Max retries for failed API calls.
    logger : logging.Logger, optional
        Logger instance.

    Returns
    -------
    Course
        The generated course object.
    """
    # Configure logger if not provided
    if logger is None:
        logger = logging.getLogger("geminiteacher.app")

    # If content is a file path, read it
    if os.path.exists(content):
        logger.info(f"Reading content from file: {content}")
        content = read_input_content(content)

    # If custom_prompt is a file path, read it
    if custom_prompt and os.path.exists(custom_prompt):
        logger.info(f"Reading custom prompt from file: {custom_prompt}")
        custom_prompt = read_custom_prompt(custom_prompt)

    # Configure LLM if not provided
    if llm is None:
        logger.info(f"Configuring model: {model_name}")
        llm = configure_gemini_llm(temperature=temperature, model_name=model_name)

    # Generate table of contents
    logger.info("Generating table of contents...")
    try:
        chapter_titles = generate_toc(content, llm=llm, max_chapters=max_chapters, fixed_chapter_count=fixed_chapter_count)
        
        # Decide on parallel or sequential processing
        if max_workers and max_workers > 1:
            # Parallel processing
            logger.info(f"Starting parallel chapter generation with {max_workers} workers.")
            chapters = parallel_generate_chapters(
                chapter_titles=chapter_titles,
                content=content,
                llm=llm,
                course_title=course_title,
                output_dir=output_dir,
                max_workers=max_workers,
                delay_range=delay_range,
                max_retries=max_retries,
                # Do NOT pass the logger here, as it may contain un-picklable GUI handlers.
                # The worker processes will configure their own logging.
            )
        else:
            # Sequential processing
            logger.info("Starting sequential chapter generation.")
            chapters = []
            for i, title in enumerate(chapter_titles):
                logger.info(f"Generating chapter {i+1}/{len(chapter_titles)}: {title}")
                chapter = generate_chapter(title, content, llm, custom_prompt)
                save_chapter_to_file(course_title, chapter, i, output_dir)
                chapters.append(chapter)

        # Generate final summary
        logger.info("Generating final course summary...")
        summary = generate_summary(content, chapters, llm)
        
        # Save summary
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in course_title).replace(" ", "_")
        summary_filename = f"{safe_title}_summary.md"
        summary_path = Path(output_dir) / summary_filename
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# {course_title} - Course Summary\n\n")
            f.write(f"{summary}\n\n")

        return Course(summary=summary, chapters=chapters, content=content)

    except Exception as e:
        logger.error(f"Error during course generation pipeline: {e}")
        # Re-raise the exception to be caught by the GUI worker if needed
        raise

def main():
    """
    Main function for the command-line application.
    """
    parser = argparse.ArgumentParser(description="Course Generator using GeminiTeacher")
    
    # Configuration and Input
    parser.add_argument("-c", "--config", help="Path to configuration file", default="config.yaml")
    parser.add_argument("-i", "--input", help="Path to input content file")
    parser.add_argument("-o", "--output-dir", help="Directory to save generated course files")
    parser.add_argument("-t", "--title", help="Course title")
    parser.add_argument("-p", "--custom-prompt", help="Path to custom prompt instructions file")
    
    # Model and Generation Settings
    parser.add_argument("--model-name", help="Name of the Gemini model to use (e.g., 'gemini-1.5-pro')")
    parser.add_argument("--temperature", type=float, help="Temperature for generation (0.0-1.0)")
    parser.add_argument("--max-chapters", type=int, help="Maximum number of chapters")
    parser.add_argument("--fixed-chapter-count", action="store_true", help="Generate exactly max-chapters")
    
    # Parallel Processing Settings
    parser.add_argument("--parallel", action="store_true", help="Use parallel processing")
    parser.add_argument("--max-workers", type=int, help="Maximum number of worker processes")
    parser.add_argument("--delay-min", type=float, help="Minimum delay between parallel requests")
    parser.add_argument("--delay-max", type=float, help="Maximum delay between parallel requests")
    parser.add_argument("--max-retries", type=int, help="Maximum number of retries for a failed request")
    
    # Other
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--log-file", help="Path to log file")
    
    args = parser.parse_args()
    
    # --- Configuration Loading and Merging ---
    
    # Load config from file
    config = load_config(args.config)
    
    # Merge command-line arguments into config, overriding file values
    cli_args = {
        'input': {'path': args.input},
        'output': {'directory': args.output_dir},
        'course': {'title': args.title, 'custom_prompt': args.custom_prompt},
        'api': {'model_name': args.model_name},
        'generation': {
            'temperature': args.temperature,
            'max_chapters': args.max_chapters,
            'fixed_chapter_count': args.fixed_chapter_count
        },
        'parallel': {
            'enabled': args.parallel,
            'max_workers': args.max_workers,
            'delay_min': args.delay_min,
            'delay_max': args.delay_max,
            'max_retries': args.max_retries
        },
        'logging': {
            'verbose': args.verbose,
            'log_file': args.log_file
        }
    }
    
    # Deep merge CLI arguments into the loaded config
    for key, value in cli_args.items():
        if key not in config:
            config[key] = {}
        for sub_key, sub_value in value.items():
            if sub_value is not None:
                config[key][sub_key] = sub_value
    
    # --- Parameter Extraction ---
    
    # Extract parameters with fallbacks
    api_config = config.get('api', {})
    input_config = config.get('input', {})
    output_config = config.get('output', {})
    course_config = config.get('course', {})
    gen_config = config.get('generation', {})
    parallel_config = config.get('parallel', {})
    log_config = config.get('logging', {})

    # Setup environment (e.g., API key)
    setup_environment(config)
    
    # Configure logging
    logger = configure_logging(
        log_file=log_config.get('log_file'), 
        verbose=log_config.get('verbose', False)
    )

    # Validate required parameters
    input_path = input_config.get('path')
    output_dir = output_config.get('directory')
    course_title = course_config.get('title')
    
    if not all([input_path, output_dir, course_title]):
        logger.error("Error: --input, --output-dir, and --title are required parameters.")
        sys.exit(1)
        
    # --- Course Creation ---
    
    logger.info(f"Starting course generation for '{course_title}'")
    
    # Determine max_workers based on parallel flag
    max_workers_val = parallel_config.get('max_workers') if parallel_config.get('enabled') else None
    
    create_course_with_progressive_save(
        content=input_path,
        course_title=course_title,
        output_dir=output_dir,
        model_name=api_config.get('model_name', 'gemini-1.5-pro'),
        temperature=gen_config.get('temperature', 0.2),
        verbose=log_config.get('verbose', False),
        max_chapters=gen_config.get('max_chapters', 10),
        fixed_chapter_count=gen_config.get('fixed_chapter_count', False),
        custom_prompt=course_config.get('custom_prompt'),
        max_workers=max_workers_val,
        delay_range=(parallel_config.get('delay_min', 0.2), parallel_config.get('delay_max', 0.8)),
        max_retries=parallel_config.get('max_retries', 3),
        logger=logger
    )

    logger.info(f"Course '{course_title}' generated successfully in '{output_dir}'")


if __name__ == "__main__":
    main() 