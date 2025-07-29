# Parallel Processing

The `parallel` module provides tools for parallel execution of tasks with controlled API rate limiting and robust error handling. This module is particularly useful for accelerating the chapter generation process while respecting API rate limits.

## Overview

The parallel processing capabilities include:

1. **Controlled Parallel Execution**: Execute tasks in parallel with configurable workers
2. **Rate Limit Management**: Add randomized delays between API requests to avoid rate limits
3. **Robust Error Handling**: Automatically retry failed requests with exponential backoff
4. **Ordered Results**: Ensure outputs are returned in the same order as inputs, regardless of completion time
5. **Progressive File Saving**: Each chapter is saved to disk as soon as it's generated, preventing data loss

## Key Functions

### parallel_generate_chapters

The main orchestration function that handles parallel generation of course chapters:

```python
import geminiteacher as gt
from geminiteacher.parallel import parallel_generate_chapters

# Define chapter titles to generate
chapter_titles = [
    "Introduction to Machine Learning",
    "Supervised Learning Algorithms",
    "Unsupervised Learning Techniques"
]

# Generate chapters in parallel
chapters = parallel_generate_chapters(
    chapter_titles=chapter_titles,
    content="Your raw content here",
    max_workers=4,              # Number of parallel workers (processes)
    delay_range=(0.2, 0.8),     # Random delay between API requests in seconds
    max_retries=3,              # Number of retry attempts for failed requests
    course_title="ML_Course",   # Title for saved files
    output_dir="courses"        # Directory to save generated chapters
)

# Process the generated chapters
for i, chapter in enumerate(chapters):
    print(f"Chapter {i+1}: {chapter.title}")
```

### generate_chapter_with_retry

A robust wrapper around the standard `generate_chapter` function that adds retry logic:

```python
import geminiteacher as gt
from geminiteacher.parallel import generate_chapter_with_retry

# Generate a single chapter with retry logic
chapter = generate_chapter_with_retry(
    chapter_title="Introduction to Neural Networks",
    content="Your raw content here",
    max_retries=3,              # Maximum number of retry attempts
    retry_delay=1.0             # Base delay between retries (will increase exponentially)
)

print(f"Chapter title: {chapter.title}")
print(f"Summary: {chapter.summary[:100]}...")
```

### parallel_map_with_delay

A generic function for applying any function to a list of items in parallel with controlled delays:

```python
from geminiteacher.parallel import parallel_map_with_delay
import time

# Define a function to execute in parallel
def process_item(item, prefix="Item"):
    # Simulate some work
    time.sleep(0.5)
    return f"{prefix}: {item}"

# Items to process
items = ["apple", "banana", "cherry", "date", "elderberry"]

# Process items in parallel with controlled delays
results = parallel_map_with_delay(
    func=process_item,
    items=items,
    max_workers=3,              # Number of parallel workers
    delay_range=(0.1, 0.5),     # Random delay between task submissions
    prefix="Processed"          # Additional parameter passed to process_item
)

# Results are in the same order as the input items
for item, result in zip(items, results):
    print(f"Original: {item} → Result: {result}")
```

## Progressive File Saving

A key feature of the parallel processing module is its ability to save chapters to disk as they are generated. This provides several benefits:

1. **Data Safety**: Even if the process is interrupted, completed chapters are already saved
2. **Progress Tracking**: You can monitor progress by watching files appear in the output directory
3. **Immediate Access**: Start reviewing early chapters while later ones are still being generated

Example of how files are saved:

```python
import geminiteacher as gt

course = gt.create_course_parallel(
    content="Your content here",
    course_title="Data_Science",
    output_dir="my_courses"
)

# Files will be saved in a structure like:
# my_courses/
#   └── Data_Science/
#       ├── chapter_01_Introduction_to_Data_Science.md
#       ├── chapter_02_Data_Collection_and_Cleaning.md
#       └── chapter_03_Exploratory_Data_Analysis.md
```

Each chapter file contains the structured content with title, summary, explanation, and extension sections.

## API Rate Limits Consideration

When working with external APIs like Google's Gemini, rate limits are an important consideration. The `parallel` module helps manage these limits through controlled submission timing:

1. **Random Delays**: Adds a configurable random delay between API requests to avoid overwhelming the API
2. **Exponential Backoff**: When retrying failed requests, uses exponential backoff to gradually increase wait times
3. **Configurable Workers**: Allows limiting the number of concurrent processes to respect API parallelism limits

### Recommended Settings for Google Gemini API

For the Google Gemini API, the following settings work well for most scenarios:

- **`max_workers`**: 2-6 (depending on your API tier)
- **`delay_range`**: (0.2, 1.0) seconds
- **`max_retries`**: 3

These settings balance speed with API reliability. For higher API tiers with more generous rate limits, you can increase `max_workers` and decrease the delay range.

## Error Handling

The parallel module implements comprehensive error handling:

1. **Retries for Empty Responses**: Automatically retries when the API returns empty content
2. **Exception Recovery**: Catches and handles API errors with automatic retries
3. **Fallback Content**: If all retries fail, returns a structured error message instead of failing completely

This ensures robustness even when dealing with unreliable network conditions or API instability.

## API Reference

### Core Functions

::: geminiteacher.parallel.parallel_generate_chapters

::: geminiteacher.parallel.generate_chapter_with_retry

::: geminiteacher.parallel.parallel_map_with_delay

## Performance Considerations

When using parallel processing, consider the following to optimize performance:

1. **CPU Cores**: The optimal `max_workers` is typically close to the number of available CPU cores
2. **Memory Usage**: Each worker process requires memory, so limit `max_workers` on memory-constrained systems
3. **API Rate Limits**: Always respect API rate limits by adjusting `delay_range` and `max_workers`
4. **Task Granularity**: Parallel processing works best when individual tasks take significant time

## Integration with Course Generator

The parallel module integrates seamlessly with the coursemaker module through the `create_course_parallel` function:

```python
import geminiteacher as gt

# Generate a course using parallel processing
course = gt.create_course_parallel(
    "Your raw content here",
    max_workers=4,
    delay_range=(0.2, 0.8),
    max_retries=3,
    course_title="Advanced_Topics",
    output_dir="output/courses"
)

print(f"Generated {len(course.chapters)} chapters in parallel")
```

## Limitations

- Increased memory usage compared to sequential processing
- Potential for higher API costs due to faster request rates
- Debugging can be more complex in parallel environments

## Future Enhancements

Future versions may include:
- Adaptive rate limiting based on API response times
- Better telemetry for monitoring API usage
- Support for concurrent.futures.ThreadPoolExecutor for I/O-bound tasks
- Dynamic worker allocation based on system resources 