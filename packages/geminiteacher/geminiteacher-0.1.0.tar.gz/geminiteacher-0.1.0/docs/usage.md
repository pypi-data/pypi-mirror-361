# Usage Guide

This guide provides a complete walkthrough for using GeminiTeacher, from installation to advanced usage.

## 1. Installation & Setup

First, let's get the application installed and configured.

### Installing GeminiTeacher

#### For Users (from PyPI)

Install GeminiTeacher directly from the Python Package Index (PyPI). This is the simplest and recommended method for most users.

```bash
# Using pip (standard Python package manager)
pip install geminiteacher

# Or if you prefer uv (faster package manager)
uv pip install geminiteacher
```

#### For Developers (from Source)

If you want to contribute to the project or need the very latest (unreleased) version, you should install from source.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/supersheepbear/GeminiTeacher.git
    cd GeminiTeacher
    ```

2.  **Install dependencies:**
    ```bash
    # Using uv (recommended for development)
    uv pip install -e .
    
    # Or install with all development dependencies
    uv pip install -e ".[dev]"
    ```

### Set Up Your Google API Key

GeminiTeacher requires a Google API key with access to the Gemini family of models. You can provide this key in two ways:

1.  **In the GUI**: The graphical interface has a dedicated field for your API key.
2.  **As an Environment Variable (for CLI/API use)**: This is the recommended way for command-line or programmatic use.

```bash
# For Linux/macOS
export GOOGLE_API_KEY="your-api-key-here"

# For Windows (PowerShell)
$env:GOOGLE_API_KEY="your-api-key-here"

# For Windows (Command Prompt)
set GOOGLE_API_KEY=your-api-key-here
```

---

## 2. GUI Usage (Recommended)

The graphical user interface is the easiest way to use GeminiTeacher.

### Launching the GUI

After installation, run the following command in your terminal:

```bash
# If installed via pip
geminiteacher-gui

# If that doesn't work, try the more reliable method
python -m geminiteacher.gui.app
```

### Using the Interface

The GUI provides simple fields for all options:
- **API Key & Model**: Paste your API key and specify the Gemini model to use (defaults to `gemini-2.5-flash`).
- **File Paths**: Use the "Browse..." buttons to select your input file and output directory.
- **Settings Caching**: Your settings are automatically saved when you close the app and reloaded next time.
- **Real-time Logging**: A log window shows you the real-time progress of the generation.

---

## 3. Command-Line (CLI) Usage

For power users and automation, the CLI provides full control over the generation process.

**A Note on Input Files**: The input file can be any text-based format that Python can read. This includes `.txt`, `.md`, `.rst`, code files like `.py`, or any other file containing plain text.

### Method 1: Using a `config.yaml` File (Best Practice)

Create a `config.yaml` to define your settings, then run:
```bash
# Most reliable method
python -m geminiteacher.app.generate_course --config config.yaml

# If the package is properly installed in your PATH
geminiteacher --config config.yaml
```

This is the recommended approach as it keeps your settings organized and version-controllable. Any command-line flag you use will override the settings in the `config.yaml` file.

Here is a comprehensive `config.yaml` example with all available options explained.

```yaml
# =======================================================
# Comprehensive GeminiTeacher Configuration
# =======================================================

# --- Input/Output Settings ---
input:
  # Required. Path to your raw content file. This can be any text-based format
  # that Python can read, such as .txt, .md, .rst, .py, etc.
  path: "input/my_raw_notes.txt"

output:
  # Required. Directory where the generated course files will be saved.
  directory: "output/MyAwesomeCourse"
  # Optional. If provided, all logs will be saved to this file.
  log_file: "logs/course_generation.log"

# --- Course Settings ---
course:
  # Required. The title of your course.
  title: "Advanced Python Programming"
  # Optional. Path to a file with custom instructions for the AI.
  # This is very useful for guiding the tone, style, and content focus.
  custom_prompt: "prompts/formal_academic_prompt.txt"

# --- Generation Settings ---
generation:
  # The specific Gemini model to use (e.g., 'gemini-1.5-pro', 'gemini-2.5-flash').
  # Default: 'gemini-1.5-pro'
  model_name: 'gemini-1.5-pro-latest'
  # Controls the "creativity" of the AI. Lower is more predictable. (0.0 - 1.0)
  # Default: 0.2
  temperature: 0.25
  # The target number of chapters for the course.
  # Default: 10
  max_chapters: 15
  # If true, the AI will generate exactly `max_chapters`. If false, the AI
  # may choose to generate fewer chapters if it deems it appropriate.
  # Default: false
  fixed_chapter_count: false

# --- Performance & Reliability Settings ---
parallel:
  # Enable parallel processing to generate chapters simultaneously.
  # This provides a major speed boost for large documents.
  # Default: false
  enabled: true
  # Number of parallel processes to run.
  # Default: The number of CPU cores on your machine.
  max_workers: 8
  # The minimum random delay (in seconds) between parallel API requests
  # to avoid rate limiting. Default: 0.2
  delay_min: 0.5
  # The maximum random delay (in seconds). Default: 0.8
  delay_max: 1.5
  # The maximum number of times to retry a failed API call for a chapter.
  # Default: 3
  max_retries: 5

# --- General Settings ---
# Enable verbose output for detailed real-time progress logging.
# This is very helpful for debugging.
# Default: false
verbose: true
```

### Method 2: Using Command-Line Flags

Pass arguments directly for one-off tasks.

```bash
# Example for a large, important document
python -m geminiteacher.app.generate_course \
  --input "input/xianxingdaishu.md" \
  --output-dir "output/linear_algebra_course" \
  --title "Linear Algebra Fundamentals" \
  --parallel \
  --max-workers 14 \
  --verbose
```

---

### All Command-Line Options

Here is the full list of available command-line options.

*   **`--config`** (Alias: **`-c`**)  
    *Type*: `PATH`  
    Path to the YAML configuration file. If used, all other options can be defined here.

*   **`--input`** (Alias: **`-i`**)  
    *Type*: `PATH`  
    **Required.** Path to the input content file (e.g., `.txt`, `.md`).

*   **`--output-dir`** (Alias: **`-o`**)  
    *Type*: `PATH`  
    **Required.** Directory where the generated course files will be saved.

*   **`--title`** (Alias: **`-t`**)  
    *Type*: `TEXT`  
    **Required.** The title of your course.

*   **`--custom-prompt`** (Alias: **`-p`**)  
    *Type*: `PATH`  
    Optional path to a file containing custom instructions for the AI to follow during generation.

*   **`--model-name`**  
    *Type*: `TEXT`  
    The specific Gemini model to use (e.g., `gemini-1.5-pro`, `gemini-2.5-flash`). Default: `gemini-1.5-pro`.

*   **`--temperature`**  
    *Type*: `FLOAT`  
    Controls the "creativity" or randomness of the AI's output. A value from `0.0` (most predictable) to `1.0` (most creative). Default: `0.2`.

*   **`--max-chapters`**  
    *Type*: `INTEGER`  
    The target number of chapters for the course. The final number may be less if the AI deems it appropriate. Default: `10`.

*   **`--fixed-chapter-count`**  
    *Type*: `FLAG`  
    If set, forces the AI to generate exactly the number of chapters specified by `--max-chapters`.

*   **`--parallel`**  
    *Type*: `FLAG`  
    If set, enables parallel processing to generate chapters simultaneously for a significant speed boost.

*   **`--max-workers`**  
    *Type*: `INTEGER`  
    When using `--parallel`, this sets the number of concurrent processes. Defaults to the number of CPU cores on your machine.

*   **`--delay-min`**  
    *Type*: `FLOAT`  
    The minimum random delay (in seconds) between parallel API requests to avoid rate limiting. Default: `0.2`.

*   **`--delay-max`**  
    *Type*: `FLOAT`  
    The maximum random delay (in seconds) between parallel API requests. Default: `0.8`.

*   **`--max-retries`**  
    *Type*: `INTEGER`  
    The maximum number of times to retry a failed API call for a chapter before giving up. Default: `3`.

*   **`--verbose`** (Alias: **`-v`**)  
    *Type*: `FLAG`  
    Enable verbose output for detailed real-time progress logging, which is very helpful for debugging.

*   **`--log-file`**  
    *Type*: `PATH`  
    Optional path to a file where all log output will be saved.

---

## 4. Python API Usage

You can also use GeminiTeacher programmatically in your own Python scripts.

```python
import geminiteacher as gt

# Generate a course with parallel processing
course = gt.create_course_parallel(
    content="path/to/your/content.txt",
    course_title="My Programmatic Course",
    output_dir="courses_output",
    max_chapters=10,
    max_workers=4
)

print(f"Generated {len(course.chapters)} chapters in parallel.")
```

--- 