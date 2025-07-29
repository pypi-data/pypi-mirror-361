# Course Generator App

This application uses the GeminiTeacher coursemaker module to generate structured educational courses from raw text content.

## Features

- Generate structured courses with chapters, explanations, and summaries
- **Process various file formats** including PDF, DOCX, PPTX, and more, by automatically converting them to Markdown
- Two chapter generation modes: adaptive (based on content complexity) or fixed count
- **Progressive saving**: Each chapter is saved as soon as it's generated, allowing you to review content while generation continues
- **Parallel processing**: Generate multiple chapters concurrently to significantly reduce overall processing time
- **Robust error handling**: Automatically retry failed API calls with exponential backoff
- Configure API keys and model settings via YAML configuration
- Output course content as Markdown files
- Customize model parameters like temperature

## Setup

1.  **Install Dependencies**: This project uses `uv` for package management. To install all required dependencies, run the following command from the project's root directory:

    ```bash
    uv sync
    ```

2.  **Configure API Key**: Copy the `app/config.yaml_example` file to `app/config.yaml` and replace the placeholder with your actual Google Gemini API key.

    ```yaml
    # app/config.yaml
    api:
      google_api_key: "your_gemini_api_key_here"
    ```

## Supported Input Formats

Thanks to the integration of the `markitdown` library, this application can accept a wide variety of input file formats beyond plain text. The script will automatically detect the file type and convert it to Markdown before generating the course.

Supported formats include, but are not limited to:
-   PDF (`.pdf`)
-   Microsoft Word (`.docx`)
-   Microsoft PowerPoint (`.pptx`)
-   Microsoft Excel (`.xlsx`, `.xls`)
-   HTML (`.html`)
-   EPub (`.epub`)
-   And many other text-based formats.

For a full list of supported formats, please refer to the [markitdown documentation](https://github.com/microsoft/markitdown).

## Usage

To run the course generator, use the `uv run` command from the project root, followed by the path to the script and any desired arguments.

**Example with a PDF file:**
```bash
uv run python app/generate_course.py app/sample.pdf --title "My PDF Course"
```

**Example with a text file:**
```bash
uv run python app/generate_course.py app/sample_input.txt --title "AI Fundamentals"
```

**Example with parallel processing:**
```bash
uv run python app/generate_course.py app/sample_input.txt --title "AI Fundamentals" --parallel --max-workers 4
```

### Command Line Arguments

- `input`: Path to the input content file (required)
- `--config`: Path to configuration file (default: `app/config.yaml`)
- `--title`: Title of the course (default: "Generated Course")
- `--verbose`, `-v`: Enable verbose output
- `--max-chapters`: Maximum number of chapters to generate (default: 10)
- `--fixed-chapters`: If set, generates exactly `--max-chapters` chapters instead of adapting based on content complexity.
- `--custom-prompt`: Path to a file containing custom instructions for chapter generation.

#### Parallel Processing Arguments

- `--parallel`: Enable parallel processing for chapter generation
- `--max-workers`: Maximum number of worker processes (default: auto-detected based on CPU cores)
- `--min-delay`: Minimum delay between API requests in seconds (default: 0.1)
- `--max-delay`: Maximum delay between API requests in seconds (default: 0.5)
- `--max-retries`: Maximum number of retry attempts per chapter (default: 3)

### Chapter Generation Modes

The application supports two modes for chapter generation:

1.  **Adaptive Mode (Default)**: The AI analyzes the content and determines the optimal number of chapters (between 1 and `--max-chapters`) based on its complexity.

2.  **Fixed Mode**: The AI generates exactly the number of chapters specified by `--max-chapters`.

### Processing Modes

The application supports two processing modes:

1. **Sequential Processing (Default)**: Chapters are generated one after another. This mode uses less memory but takes longer.

2. **Parallel Processing**: Multiple chapters are generated concurrently, significantly reducing overall processing time. Enable with the `--parallel` flag.

### Custom Prompt Instructions

You can customize how the AI generates chapter explanations by providing a file with custom instructions. These instructions will be appended to the "系统性讲解" (Systematic Explanation) section of each chapter's prompt.

This feature is useful when you want to:
- Focus on specific aspects of the content
- Request more code examples or practical applications
- Adjust the teaching style or depth of explanations
- Add domain-specific guidance for the AI

To use custom prompts, create a text file with your instructions and use the `--custom-prompt` flag:

```bash
# Example custom prompt file (my_instructions.txt):
# 请特别关注实际应用案例，并提供更多代码示例。每个概念至少提供一个Python代码示例。

uv run python app/generate_course.py app/sample_input.txt --title "Python Programming" --custom-prompt my_instructions.txt
```

### Examples

```bash
# Adaptive mode (default) - generates between 1-10 chapters based on content complexity
uv run python app/generate_course.py app/sample_input.txt --title "Introduction to AI" --max-chapters 10

# Fixed mode - generates exactly 5 chapters
uv run python app/generate_course.py app/sample_input.txt --title "Introduction to AI" --max-chapters 5 --fixed-chapters

# Using custom prompt instructions
uv run python app/generate_course.py app/sample_input.txt --title "Machine Learning" --custom-prompt custom_instructions.txt

# Parallel processing with custom settings
uv run python app/generate_course.py app/sample_input.txt --title "Machine Learning" --parallel --max-workers 4 --min-delay 0.2 --max-delay 1.0 --max-retries 3
```

## Output

The generated course will be saved in the `app/output` directory (configurable in `config.yaml`) with the following structure:

- `{course_title}_summary.md`: Overall course summary
- `{course_title}_chapter_01.md`, `{course_title}_chapter_02.md`, etc.: Individual chapter files

Each chapter file includes:
- Chapter title
- Summary
- Detailed explanation
- Extension thoughts

**Note**: With progressive saving enabled, each chapter is saved to disk immediately after it's generated, rather than waiting for the entire course to complete. This allows you to start reviewing content while the AI continues generating additional chapters.

## Configuration

You can customize the behavior by editing `app/config.yaml`:

```yaml
# Gemini API Configuration
api:
  google_api_key: "your_gemini_api_key_here"

# Model Settings
model:
  name: "gemini-1.5-pro"  # Model name
  temperature: 0.2        # Controls randomness (0.0 to 1.0)

# Course Generation Settings
course:
  output_dir: "output"    # Directory to save generated courses
``` 