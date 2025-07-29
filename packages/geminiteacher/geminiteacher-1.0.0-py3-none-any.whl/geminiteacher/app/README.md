# GeminiTeacher Command-line Application

This submodule provides a command-line interface for the GeminiTeacher package, allowing you to generate courses from text content using simple commands.

## Installation

The command-line application is installed automatically when you install the GeminiTeacher package:

```bash
pip install geminiteacher
```

## Usage

### Command-line Usage

After installation, you can use the `geminiteacher` command directly:

```bash
# Basic usage with config file
geminiteacher --config config.yaml

# Specify input file and output directory
geminiteacher --input content.txt --output-dir courses

# Set course title and use parallel processing
geminiteacher --input content.txt --title "Machine Learning Basics" --parallel

# Use custom prompt file
geminiteacher --input content.txt --custom-prompt custom_instructions.txt

# Enable verbose output and specify log file
geminiteacher --input content.txt --verbose --log-file generation.log
```

### Configuration File

Create a `config.yaml` file to specify settings (you can copy from the provided `config.yaml.example`):

```yaml
# API Configuration
api:
  google_api_key: "your_gemini_api_key_here"
  model_name: "gemini-1.5-pro"

# Input/Output Settings
input:
  path: "input/content.txt"

output:
  directory: "output"

# Course Settings
course:
  title: "My Course"
  custom_prompt: "custom_instructions.txt"

# Generation Settings
generation:
  temperature: 0.2
  max_chapters: 10
  fixed_chapter_count: false

# Parallel Processing Settings
parallel:
  enabled: true
  max_workers: 4
  delay_min: 0.2
  delay_max: 0.8
  max_retries: 3
```

### Custom Prompt File

You can create a custom prompt file with instructions for the chapter generation:

```
Focus on practical examples and include code snippets where relevant.
Each concept should be explained with a real-world application.
Include exercises at the end of each explanation section.
```

## Programmatic Usage

You can also use the app module programmatically in your Python code:

```python
from geminiteacher.app import create_course_with_progressive_save, configure_logging

# Configure logging
logger = configure_logging(log_file="generation.log", verbose=True)

# Generate a course
course = create_course_with_progressive_save(
    content="Your content here...",
    course_title="Python Programming",
    output_dir="courses",
    temperature=0.2,
    max_chapters=5,
    fixed_chapter_count=True,
    custom_prompt="Focus on practical examples",
    verbose=True,
    logger=logger
)

# Access the generated course
print(f"Generated {len(course.chapters)} chapters")
for i, chapter in enumerate(course.chapters):
    print(f"Chapter {i+1}: {chapter.title}")
```

## Output Structure

The application generates the following files in the output directory:

- `{course_title}_chapter_{nn}_{chapter_title}.md` - Individual chapter files
- `{course_title}_summary.md` - Course summary file

Each chapter file contains:
- Title
- Summary
- Detailed explanation
- Extension thoughts 