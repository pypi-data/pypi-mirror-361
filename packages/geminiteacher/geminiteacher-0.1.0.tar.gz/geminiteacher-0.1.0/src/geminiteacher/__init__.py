"""
GeminiTeacher - An educational content generation toolkit powered by Google's Gemini LLM.

This package transforms raw text content into structured, well-organized educational courses
with minimal effort. Perfect for educators, content creators, and anyone looking to quickly
create high-quality learning materials.
"""

__version__ = "0.1.0"

# Import main components for top-level access
from geminiteacher.coursemaker import (
    create_course,
    create_course_parallel,
    generate_toc,
    generate_chapter,
    generate_summary,
    configure_gemini_llm,
    Course,
    ChapterContent,
)

from geminiteacher.parallel import (
    parallel_generate_chapters,
    generate_chapter_with_retry,
    parallel_map_with_delay,
)

# Import app components
import geminiteacher.app

# Define __all__ to specify what's available for "from geminiteacher import *"
__all__ = [
    # Core functionality
    "create_course",
    "create_course_parallel",
    "generate_toc",
    "generate_chapter",
    "generate_summary",
    "configure_gemini_llm",
    "Course",
    "ChapterContent",
    
    # Parallel processing
    "parallel_generate_chapters",
    "generate_chapter_with_retry",
    "parallel_map_with_delay",
    
    # App submodule
    "app",
]
