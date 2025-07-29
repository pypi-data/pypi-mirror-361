# Planner's Scratchpad

## Background and Motivation

The user wants to improve the performance of the course generation process by introducing parallel processing. The current implementation generates chapters sequentially, which is time-consuming as it waits for each API call to complete before starting the next.

The goal is to use a multiprocessing pool to generate chapters concurrently, while respecting API rate limits and ensuring the final output is correctly ordered. The implementation should also be robust, with retries for failed API calls, and adhere to the project's coding standards.

## Key Challenges and Analysis

1.  **Parallel Execution**: The core logic needs to be refactored to allow individual chapters to be generated in separate processes. The `concurrent.futures.ProcessPoolExecutor` is a suitable tool for this.
2.  **Maintaining Order**: Chapter content must be assembled and saved in the correct sequence (Chapter 1, Chapter 2, etc.), even though the generation will happen in parallel and may finish out of order. `ProcessPoolExecutor.map` is a good choice here as it returns results in the order that tasks were submitted.
3.  **Rate Limiting**: Sending a large number of API requests simultaneously can trigger rate limits. A mechanism to introduce a small, random delay between submitting tasks to the process pool is required. Researching the specific rate limits for `gemini-1.5-flash` will be necessary to determine a safe delay strategy.
4.  **Error Handling**: API calls can fail due to network issues, timeouts, or empty responses. A retry mechanism must be implemented within the chapter generation function to handle these transient errors gracefully.
5.  **Testability**: The introduction of multiprocessing and `time.sleep` makes testing more complex. Tests will require significant mocking to remain fast and isolated unit tests, as per the repository's rules. We will need to mock the `ProcessPoolExecutor`, the delay function, and the API call itself.

## High-level Task Breakdown

1.  **Research Rate Limits**: Investigate the API rate limits for `gemini-2.5-flash` to inform the delay strategy.
2.  **Refactor for Parallelism**: Isolate the logic for generating a single chapter into a dedicated, self-contained function. This function will be the target for the multiprocessing pool.
3.  **Implement Multiprocessing Orchestrator**:
    *   Create a main function that prepares a list of tasks (e.g., a list of chapter titles or prompts).
    *   Use `concurrent.futures.ProcessPoolExecutor` to manage a pool of worker processes.
    *   Implement a loop that submits chapter generation tasks to the pool, including a small, random delay (`time.sleep`) between each submission.
4.  **Implement Robustness Features**:
    *   Inside the chapter generation function, wrap the API call in a loop or use a decorator to implement retry logic for timeouts or empty responses.
5.  **Manage Output**:
    *   Collect the results from the completed tasks.
    *   Ensure the results are sorted or handled in the correct chapter order before writing them to their respective markdown files.
6.  **Update Unit Tests**:
    *   Write new unit tests for the multiprocessing orchestrator.
    *   Mock `ProcessPoolExecutor`, `time.sleep`, and the chapter generation function.
    *   Verify that tasks are submitted with delays and that results are handled correctly.
    *   Add tests for the retry mechanism.

## Project Status Board

- [x] **Task 1: Research `gemini-2.5-flash` rate limits.**
- [x] **Task 2: Refactor single chapter generation into a callable function.**
  - Created `parallel.py` module with `generate_chapter_with_retry` function that adds retry logic
  - Implemented `parallel_map_with_delay` function for controlled parallel execution
  - Added `parallel_generate_chapters` function to orchestrate parallel chapter generation
  - Added comprehensive unit tests with proper mocking
- [x] **Task 3: Implement the `ProcessPoolExecutor` to manage parallel execution.**
  - Implemented in the `parallel_map_with_delay` function in the `parallel.py` module
  - The function correctly handles worker processes and task submission
- [x] **Task 4: Add a random delay between task submissions to avoid rate limiting.**
  - Implemented in `parallel_map_with_delay` which adds configurable random delays
  - The delay range can be customized via the `delay_range` parameter
- [x] **Task 5: Implement retry logic for API calls within the chapter generation function.**
  - Created `generate_chapter_with_retry` function that adds retry logic with exponential backoff
  - Added proper error handling to handle API failures gracefully
- [x] **Task 6: Ensure results are collected and saved in the correct order.**
  - The `parallel_map_with_delay` function preserves the input order in its output
  - Results are properly collected from futures in the order they were submitted
- [x] **Task 7: Create comprehensive unit tests with appropriate mocking.**
  - Added tests in `test_parallel.py` for all the parallel processing functionality
  - Properly mocked ProcessPoolExecutor, time.sleep, and the chapter generation function
  - Verified that tasks are submitted with delays and results are handled correctly
  - Added tests for the retry mechanism with various scenarios
  - Enhanced documentation in docs folder with parallel.md and updated coursemaker.md

## Executor's Feedback or Assistance Requests

Task 2 has been completed successfully. The implementation includes:

1. A new `parallel.py` module that contains:
   - `generate_chapter_with_retry`: A function that wraps the existing `generate_chapter` function with retry logic for handling empty responses or API errors
   - `parallel_map_with_delay`: A generic function for parallel processing with controlled delays between task submissions
   - `parallel_generate_chapters`: A function that uses the above components to generate chapters in parallel

2. An updated `coursemaker.py` with:
   - `create_course_parallel`: A new function that follows the same pattern as `create_course` but uses parallel processing

3. Updated `generate_course.py` with:
   - New command-line arguments for parallel processing (`--parallel`, `--max-workers`, etc.)
   - Logic to use either sequential or parallel processing based on user preference

4. Updated `run_coursemaker.cmd` with:
   - Example command for parallel processing with appropriate parameters

All tests are passing, including the new tests for parallel processing functionality. The implementation respects the API rate limits for `gemini-2.5-flash` by adding configurable delays between requests.

Tasks 3-7 have been completed successfully. The implementation includes:

1. ProcessPoolExecutor integration in the `parallel_map_with_delay` function to manage parallel execution
2. Random delay between API requests to avoid rate limiting
3. Robust retry logic with exponential backoff for API calls
4. Preservation of result order regardless of completion time
5. Comprehensive unit tests with proper mocking of all external dependencies

The documentation has been updated to reflect these new features:
1. Updated coursemaker.md with parallel processing information
2. Created a new parallel.md document with detailed API documentation
3. Updated modules.md to include the parallel module
4. Updated README.md with parallel processing capabilities
5. Updated mkdocs.yml to include the new documentation page

All tests are passing with `make test` and documentation builds successfully with `make docs-test`.

## Reviewer's Audit & Feedback

#### A. Requirement Fulfillment
- [PASS] **Functional Correctness**: The implementation successfully adds parallel processing capability to the course generation process while maintaining the same output structure and quality.

#### B. Test Protocol Adherence (`.cursor/rules/pytestrule.mdc`)
- [PASS] **Pure Unit Tests**: All tests are properly isolated with aggressive mocking of external dependencies.
- [PASS] **No Forbidden Tests**: No integration or E2E tests were added; all tests are pure unit tests.
- [PASS] **Test Execution**: All tests pass successfully with `make test`.
- [PASS] **Speed**: The test suite runs in under 5 seconds as required.

#### C. Python Development Protocol Adherence (`.cursor/rules/pythonrule.mdc`)
- [PASS] **Package Structure**: The code follows the `src` layout with proper module organization.
- [PASS] **Docstrings**: All public functions have comprehensive NumPy-style docstrings.
- [PASS] **Type Hinting**: All function signatures include complete type hints.
- [PASS] **Code Quality**: The code is modular, clean, and follows PEP 8 standards.

#### D. Workflow & Documentation Hygiene
- [PASS] **Scratchpad Integrity**: The project history is clear and the status is up-to-date.
- [PASS] **Lessons Learned**: Significant discoveries about rate limits were documented.

#### E. Implementation-Specific Review
- [PASS] **Parallel Processing**: The implementation correctly uses `ProcessPoolExecutor` for parallel execution.
- [PASS] **Rate Limiting**: The code includes configurable delay parameters to prevent API rate limit issues.
- [PASS] **Retry Logic**: The implementation includes retry logic for handling empty responses or API errors.
- [PASS] **Command-Line Interface**: The CLI has been updated to support parallel processing with appropriate options.

#### F. Recommendations for Future Improvements
- Consider adding logging to track the progress of parallel chapter generation.
- Consider implementing adaptive delay based on API response times or error rates.
- Add telemetry to monitor API usage and adjust parameters automatically.

Overall, the implementation meets all requirements and follows the project's coding standards. The code is well-structured, properly tested, and includes comprehensive documentation. The Task 2 implementation is approved.

## Lessons

- **`gemini-2.5-flash` Rate Limits (Tier 1 Paid User)**: The official documentation specifies the following limits:
    - **Requests Per Minute (RPM): 1,000**
    - Tokens Per Minute (TPM): 1,000,000
    - Requests Per Day (RPD): 10,000
- **Strategy**: The 1,000 RPM limit is very generous. The primary concern is not hitting the API with a large number of requests all at once. A small, randomized delay (e.g., between 0.1 and 0.5 seconds) between submitting tasks to the pool is a good practice to ensure smooth processing and avoid potential issues, even when technically under the RPM limit. 