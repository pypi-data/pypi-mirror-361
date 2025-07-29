# GeminiTeacher Modules

GeminiTeacher consists of several modules that work together to provide a complete course generation solution.

## Core Modules

### CourseGenerator (`geminiteacher.coursemaker`)

The main module responsible for generating course content.

```python
from geminiteacher import create_course, configure_gemini_llm

# Configure the language model
llm = configure_gemini_llm(temperature=0.2)

# Generate a course
course = create_course(
    content="Your content here...",
    llm=llm,
    max_chapters=5
)

# Access the generated course
print(f"Course summary: {course.summary}")
for chapter in course.chapters:
    print(f"Chapter: {chapter.title}")
    print(f"Summary: {chapter.summary}")
```

### Parallel Processing (`geminiteacher.parallel`)

Provides parallel processing capabilities for faster course generation.

```python
from geminiteacher import parallel_generate_chapters, configure_gemini_llm
from geminiteacher import Course, ChapterContent

# Configure the language model
llm = configure_gemini_llm(temperature=0.2)

# Generate chapters in parallel
chapter_titles = ["Introduction", "Basic Concepts", "Advanced Topics"]
chapters = parallel_generate_chapters(
    content="Your content here...",
    chapter_titles=chapter_titles,
    llm=llm,
    max_workers=3,
    course_title="My Course",
    output_dir="output"
)

# Create a course with the generated chapters
course = Course(
    summary="Course summary",
    chapters=chapters
)
```

## Command-line Application (`geminiteacher.app`)

A full-featured command-line application for generating courses.

### Command-line Usage

After installation, you can use the `geminiteacher` command directly:

```bash
# Basic usage with config file
geminiteacher --config config.yaml

# Specify input file and output directory
geminiteacher --input content.txt --output-dir courses

# Set course title and use parallel processing
geminiteacher --input content.txt --title "Machine Learning Basics" --parallel
```

### Programmatic Usage

You can also use the app module programmatically:

```python
from geminiteacher.app import create_course_with_progressive_save, configure_logging

# Configure logging
logger = configure_logging(log_file="generation.log", verbose=True)

# Generate a course with progressive saving
course = create_course_with_progressive_save(
    content="Your content here...",
    course_title="Python Programming",
    output_dir="courses",
    temperature=0.2,
    max_chapters=5,
    verbose=True,
    logger=logger
)
```

## Data Models

GeminiTeacher uses the following data models:

### Course

```python
class Course:
    """
    Represents a complete course with summary and chapters.
    """
    summary: str
    chapters: List[ChapterContent]
```

### ChapterContent

```python
class ChapterContent:
    """
    Represents a single chapter in a course.
    """
    title: str
    summary: str
    explanation: str
    extension: str
```
