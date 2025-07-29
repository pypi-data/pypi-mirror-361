# Auto-Learning System Plan

### Background and Motivation

The user wants to build an automated content-to-curriculum system using LangChain. The system will take a piece of raw learning material, structure it into a table of contents, generate a detailed, structured explanation for each section, and conclude with a full summary. This requires a multi-step LLM chain, careful prompt engineering, and structured output parsing.

The entire development process must follow the established Python Package Development Protocol, with a strict emphasis on Test-Driven Development (TDD) and pure, isolated unit tests.

### Key Challenges and Analysis

1.  **LLM Interaction in Tests**: The core logic involves multiple calls to an LLM. According to the testing protocol, these are I/O operations and **must be mocked**. Tests will need to verify that our code generates the correct prompts and correctly parses the (mocked) structured responses from the LLM.
2.  **Structured Output**: Phase 1 (Table of Contents) and Phase 3 (Chapter Explanation) require the LLM to return structured data (a list of titles and a JSON object with specific keys, respectively). This will be handled using LangChain's Output Parsers, likely `SimpleJsonOutputParser` for the TOC and a `PydanticOutputParser` for the chapter content to ensure type safety and structure.
3.  **State Management**: The pipeline is a sequence of dependent steps. The output of Phase 1 is the input for Phase 2, and so on. The orchestration logic must manage this state correctly, passing the original content and generated artifacts through the chain.
4.  **Prompt Engineering**: The success of the system hinges on the quality of the prompts. Each prompt (for TOC, chapter explanation, and summary) must be carefully designed to elicit the desired output from the LLM.

### High-level Task Breakdown

The implementation will be broken down into the following verifiable, test-driven tasks. A new module, `src/geminiteacher/coursemaker.py`, will be created to house the logic.

1.  **Setup**: Create the necessary files: `src/geminiteacher/coursemaker.py` and `tests/test_coursemaker.py`.
2.  **Phase 1 (Table of Contents)**: Implement `generate_toc` to create a chapter list from raw text.
3.  **Phase 2 (Prompt Generation)**: Implement `create_chapter_prompt_template` which is a simple utility.
4.  **Phase 3 (Chapter Explanation)**: Implement `generate_chapter` to create a structured explanation for a single chapter.
5.  **Phase 4 (Summary)**: Implement `generate_summary`.
6.  **Orchestration**: Implement the main `create_course` pipeline to connect all the steps.

### Project Status Board

-   [x] **Task 1: Setup**
    -   [x] Create `src/geminiteacher/coursemaker.py`
    -   [x] Create `tests/test_coursemaker.py`
-   [x] **Task 2: Implement Phase 1 - Table of Contents Generation (`generate_toc`)**
    -   [x] Write a failing test for `generate_toc` in `tests/test_coursemaker.py`.
    -   [x] Implement the `generate_toc` function in `src/geminiteacher/coursemaker.py` to pass the test.
-   [x] **Task 3: Implement Phase 2 - Chapter Prompt Generation (`create_chapter_prompt_template`)**
    -   [x] Write a test for the prompt template logic.
    -   [x] Define the `create_chapter_prompt_template` in `src/geminiteacher/coursemaker.py`.
-   [x] **Task 4: Implement Phase 3 - Chapter Explanation Generation (`generate_chapter`)**
    -   [x] Write a failing test for `generate_chapter` that mocks the LLM and checks for structured output parsing.
    -   [x] Implement the `generate_chapter` function.
-   [x] **Task 5: Implement Phase 4 - Summary Generation (`generate_summary`)**
    -   [x] Write a failing test for `generate_summary`.
    -   [x] Implement the `generate_summary` function.
-   [x] **Task 6: Implement Orchestration (`create_course`)**
    -   [x] Write a failing test for the `create_course` pipeline, mocking all LLM calls.
    -   [x] Implement the `create_course` pipeline to pass the test.

### Executor's Feedback or Assistance Requests

Tasks 1-6 have been completed successfully. During implementation, we encountered and resolved the following issues:

1. We initially attempted to use `BaseChatModel` directly in our implementation, but it's an abstract class that can't be instantiated. 
2. We resolved this by adjusting our implementation to use a more testable approach that avoids direct instantiation of the abstract class.
3. We created separate helper functions like `create_toc_prompt` and `parse_chapter_content` to improve modularity and make testing easier.
4. For Task 4, we implemented the `ChapterContent` class using Pydantic to provide a structured representation of chapter content with validation.
5. We encountered a challenge with parsing malformed LLM responses in the `parse_chapter_content` function, which we fixed by adding better detection of missing section headers.
6. For Task 5, we implemented the summary generation with a structured prompt that includes both the original content and chapter summaries.
7. For Task 6, we created a `Course` model to represent the complete course structure and implemented the orchestration function that ties all the steps together.

All tests are now passing, with proper mocking of LLM interactions to avoid any actual API calls. The implementation follows all the required protocols and best practices.

### Reviewer's Audit & Feedback

#### A. Requirement Fulfillment
-   [PASS] **Functional Correctness**: The implementation correctly addresses all the required functionality:
    - The `generate_toc` function produces a structured table of contents from raw content.
    - The `create_chapter_prompt_template` function creates a well-designed prompt template for chapter explanations.
    - The `generate_chapter` function produces structured chapter content with appropriate sections.
    - The `generate_summary` function creates a comprehensive course summary based on the original content and chapter information.
    - The `create_course` function successfully orchestrates the entire process from raw content to structured course.
    - All components work together seamlessly in a well-defined pipeline.

#### B. Test Protocol Adherence (`.cursor/pytest rule.md`)
-   [PASS] **Pure Unit Tests**: All tests are 100% isolated with proper mocking of LangChain components. No real LLM calls are made.
-   [PASS] **No Forbidden Tests**: There are no integration tests or tests with real I/O operations.
-   [PASS] **Test Execution**: All tests pass without errors.
-   [PASS] **Speed**: The test suite runs in under 0.5 seconds (0.46s in the final run), well below the 5-second target.

#### C. Python Development Protocol Adherence
-   [PASS] **Package Structure**: Code follows the correct `src` layout.
-   [PASS] **Docstrings**: All public functions and classes have proper NumPy-style docstrings with Parameters, Returns, and Examples sections.
-   [PASS] **Type Hinting**: All function signatures have complete type hints, including the use of appropriate types from the typing module.
-   [PASS] **Code Quality**: The code is clean, modular, and follows PEP 8 standards.

#### D. Workflow & Documentation Hygiene
-   [PASS] **Scratchpad Integrity**: Project history and status are clearly documented.
-   [PASS] **Lessons Learned**: Significant discoveries about structured output parsing, Pydantic modeling, and handling malformed LLM responses have been documented.

#### E. Implementation Quality
-   [PASS] **Modularity**: The code is well-organized with clear separation of concerns:
    - Prompt creation functions are separate from processing functions
    - Data models are clearly defined using Pydantic
    - The orchestration function coordinates the pipeline without duplicating logic
-   [PASS] **Error Handling**: The code gracefully handles edge cases:
    - Empty LLM responses
    - Malformed responses without expected sections
    - Empty chapter lists
-   [PASS] **Efficiency**: The implementation avoids unnecessary processing and redundant operations.

#### F. Design Patterns
-   [PASS] **Model-View Separation**: The data models (ChapterContent, Course) are cleanly separated from the processing logic.
-   [PASS] **Pipeline Pattern**: The `create_course` function implements a clear pipeline pattern, with each step building on the previous one.
-   [PASS] **Factory Methods**: The prompt creation functions act as factory methods, encapsulating the creation logic.

#### Additional Observations
- **Robustness**: The code includes proper error handling for malformed LLM responses, which is critical for production use.
- **Modularity**: The separation of concerns is excellent, with distinct functions for prompt creation, LLM interaction, and response parsing.
- **Testability**: The design choices make the code highly testable, particularly the modular approach to prompt creation and content parsing.
- **Multilingual Support**: The prompts properly implement simplified Chinese output as required.
- **Structure**: The use of Pydantic for data models provides clean validation and a clear data structure.
- **Completeness**: The implementation covers all aspects of the required functionality, from initial content analysis to final summary generation.

#### Areas for Future Improvement
- Consider adding more comprehensive validation in the data models, such as field length limits or content validation.
- For production use, consider adding logging to track LLM interactions and errors.
- The current implementation uses a placeholder for the LLM. In a real application, a concrete LLM implementation would need to be provided.
- Consider adding progress tracking for long-running processes when generating multiple chapters.
- The system could benefit from caching mechanisms to avoid regenerating content that hasn't changed.

The implemented code fully meets all the requirements and follows all the established protocols. The architecture is clean, modular, and maintainable, making it an excellent foundation for further development or production use.

### Lessons

1. **Abstract Class Handling**: When working with abstract classes like BaseChatModel, we should design our code to make it testable by allowing dependency injection or using patterns that allow for easy mocking.
2. **LangChain Testing**: When testing LangChain components, we need to mock all external interactions (like LLM API calls) to ensure fast, isolated tests.
3. **ChatPromptTemplate Testing**: The `ChatPromptTemplate` class in LangChain doesn't have a direct `template` attribute, but we can access the prompt content through the `messages` attribute.
4. **Structured Parsing**: When parsing structured output from LLMs, robust error handling is essential. We should always anticipate malformed outputs and have graceful fallback mechanisms.
5. **Pydantic Models**: Pydantic provides an excellent way to define structured data models with validation, making it perfect for representing LLM-generated structured content.
6. **Orchestration Pattern**: When building multi-step LLM pipelines, it's valuable to have a clear orchestration function that manages the flow of data between steps.
7. **Prompt Design**: Carefully designed prompts with clear instructions and structure lead to more predictable and useful LLM outputs. 

# Feature: Two Modes for Chapter Generation

### Background and Motivation

The user wants to add two modes to the app for chapter generation:

1. **Mode 1 (Adaptive)**: Given a maximum chapter number, the AI decides how many chapters to generate based on content complexity. This is the current default behavior.

2. **Mode 2 (Fixed)**: Given a maximum chapter number, the AI generates exactly that many chapters regardless of content complexity.

### Key Changes Required

1. **Modify TOC Generation**: Update the `generate_toc` function and its prompt template to support both modes.
2. **Modify the CLI Interface**: Update `app/generate_course.py` to include a mode flag for selecting between adaptive and fixed chapter count.
3. **Update Documentation**: Ensure that the new feature is properly documented.

### High-level Task Breakdown

1. **Add Mode Parameter**:
   - Add a `fixed_chapter_count` boolean parameter to `create_toc_prompt` and `generate_toc`
   - Update the `create_course` function to accept and pass this parameter

2. **Update TOC Prompt**:
   - Modify the TOC prompt template to have conditional instructions based on the mode
   - For Mode 1 (Adaptive): Keep existing behavior (1-N chapters based on content)
   - For Mode 2 (Fixed): Require exactly N chapters

3. **Update CLI Interface**:
   - Add a `--fixed-chapters` flag to `app/generate_course.py`
   - Add appropriate help text explaining the two modes
   - Pass the selected mode to the `create_course` function

4. **Testing**:
   - Add tests for both modes of chapter generation
   - Ensure backward compatibility

### Project Status Board

- [x] **Task 1: Add Mode Parameter**
  - [x] Update `create_toc_prompt` to accept and use `fixed_chapter_count` parameter
  - [x] Update `generate_toc` to pass the parameter
  - [x] Update `create_course` to accept the parameter

- [x] **Task 2: Update TOC Prompt**
  - [x] Modify prompt template to include conditional logic based on mode
  - [x] Test prompt generation with different modes

- [x] **Task 3: Update CLI Interface**
  - [x] Add `--fixed-chapters` flag to argument parser
  - [x] Update help text to explain the two modes
  - [x] Pass mode to `create_course` function

- [x] **Task 4: Add Tests**
  - [x] Add tests for Mode 1 (Adaptive)
  - [x] Add tests for Mode 2 (Fixed)
  - [x] Verify backward compatibility 

# Feature: Multi-Format Input Support via Pre-processing

### Background and Motivation

The user wants the application to accept input files in formats other than plain text, such as PDF. The plan is to pre-process these files and convert them into clean Markdown, which is an ideal input format for the downstream LLM that generates the course.

### Key Challenges and Analysis

After initial planning, the user decided to use the existing `markitdown` library from Microsoft instead of building a custom conversion solution. This is an excellent decision for several reasons:

1.  **Robust and Maintained**: `markitdown` is a popular, open-source tool specifically designed for converting various document types (including PDF, DOCX, PPTX, and more) into LLM-friendly Markdown.
2.  **Avoids Reinventing the Wheel**: Using a battle-tested library saves significant development time and provides a more reliable and feature-rich solution than a custom implementation.
3.  **Extensibility**: It has a plugin system and supports advanced backends like Azure Document Intelligence, offering powerful options for future enhancements.

**Decision**: We will integrate the `markitdown` library to handle all file-to-Markdown conversions. Our `converter` module will act as a lightweight wrapper around this library.

### High-level Task Breakdown

The plan has been simplified to focus on integrating the `markitdown` library.

1.  **Integrate Dependency**: Add `'markitdown[pdf]'` to the project dependencies in `pyproject.toml`.
2.  **Implement Converter Wrapper**: In `src/geminiteacher/converter.py`, implement a `convert_to_markdown` function that initializes the `MarkItDown` class and uses it to convert the input file.
3.  **Write Wrapper Tests**: In `tests/test_converter.py`, write unit tests that mock the `MarkItDown` object to ensure our wrapper function calls it correctly.
4.  **Integrate into the Main App**: Modify `app/generate_course.py` to check the input file extension and call the new converter function for supported types.
5.  **Update Documentation**: Update `app/README.md` to reflect the new capabilities and any new setup steps required for the dependency.

### Project Status Board

- [x] **Task 1: Setup Converter Module**
  - [x] Create `src/geminiteacher/converter.py`
  - [x] Create `tests/test_converter.py`
- [x] **Task 2: Integrate `markitdown`**
  - [x] Add `markitdown[pdf]` to `pyproject.toml`
  - [x] Implement the wrapper function in `converter.py`
  - [x] Write unit tests for the wrapper
- [x] **Task 3: Integrate into Main App**
  - [x] Update `app/generate_course.py` to call the converter
  - [x] Test the full integrated workflow
- [x] **Task 4: Update Docs**
  - [x] Update `app/README.md` to document new supported formats

# Feature: Custom Prompt for Chapter Generation

### Background and Motivation

The user wants to add the ability to customize the prompts used for chapter generation. Specifically, they want to allow users to provide a custom prompt that will be appended to the "系统性讲解" (Systematic Explanation) section of each chapter's prompt. This will give users more control over the style, focus, or specific instructions for the content generation.

### Key Challenges and Analysis

1. **Prompt Injection**: We need to carefully inject the custom prompt at the right location in the existing prompt template without disrupting its structure.
2. **Optional Feature**: This feature should be optional, with the system working normally if no custom prompt is provided.
3. **File Input**: The custom prompt should be read from a text file provided by the user.
4. **CLI Integration**: We need to update the command-line interface to accept a path to the custom prompt file.

### High-level Task Breakdown

1. **Update Prompt Template**:
   - Modify the `create_chapter_prompt_template` function to accept an optional `custom_prompt` parameter
   - Inject this custom prompt at the end of the "系统性讲解" section if provided

2. **Update Core Functions**:
   - Update `generate_chapter` to accept and pass the custom prompt
   - Update `create_course` to accept and pass the custom prompt to all chapter generations

3. **Add File Reading Logic**:
   - Create a utility function to read the custom prompt from a file

4. **Update CLI Interface**:
   - Add a `--custom-prompt` flag to `app/generate_course.py` that accepts a file path
   - Read the file and pass its contents to the `create_course` function

5. **Testing**:
   - Add tests for prompt generation with and without custom prompts
   - Add tests for the file reading utility
   - Ensure backward compatibility

### Project Status Board

- [x] **Task 1: Update Prompt Template**
  - [x] Modify `create_chapter_prompt_template` to accept and use `custom_prompt` parameter
  - [x] Update prompt template to include the custom prompt at the right location

- [x] **Task 2: Update Core Functions**
  - [x] Update `generate_chapter` to accept `custom_prompt` parameter
  - [x] Update `create_course` to accept and pass the parameter

- [x] **Task 3: Add File Reading Logic**
  - [x] Create utility function to read custom prompt from file
  - [x] Handle file not found and other potential errors

- [x] **Task 4: Update CLI Interface**
  - [x] Add `--custom-prompt` flag to argument parser
  - [x] Implement file reading and error handling
  - [x] Pass custom prompt to `create_course` function

- [x] **Task 5: Add Tests**
  - [x] Test prompt generation with and without custom prompt
  - [x] Test file reading utility
  - [x] Verify backward compatibility 