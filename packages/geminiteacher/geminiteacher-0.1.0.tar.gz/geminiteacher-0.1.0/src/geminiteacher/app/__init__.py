"""
Command-line application for GeminiTeacher.

This submodule provides a command-line interface and utility functions for generating
courses using the GeminiTeacher package.
"""

from geminiteacher.app.generate_course import (
    main,
    configure_logging,
    load_config,
    read_input_content,
    read_custom_prompt,
    create_course_with_progressive_save,
)

__all__ = [
    "main",
    "configure_logging",
    "load_config",
    "read_input_content",
    "read_custom_prompt",
    "create_course_with_progressive_save",
] 