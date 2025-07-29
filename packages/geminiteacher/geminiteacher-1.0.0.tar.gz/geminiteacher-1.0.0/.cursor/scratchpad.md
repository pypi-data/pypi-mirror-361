# Planner's Scratchpad: Rebranding to GeminiTeacher

## Background and Motivation

The user has decided to change the project's direction. The new goal is to rebrand the entire repository from "GeminiTeacher" to "GeminiTeacher" and prepare it for publication on PyPI. The new package name will be `geminiteacher`, and it should be importable as `import geminiteacher as gt`.

This requires a comprehensive renaming effort across the entire codebase, documentation, and configuration files, as well as a significant rewrite of the `README.md` to be suitable for a public audience.

## Key Challenges and Analysis

1.  **Comprehensive Renaming**: The name "GeminiTeacher" and "geminiteacher" are present in file names, directory names, import statements, docstrings, comments, configuration files (`pyproject.toml`, `mkdocs.yml`), and documentation. A simple find-and-replace will not be sufficient; a systematic approach is needed to avoid breaking the project.
2.  **PyPI Packaging**: The `pyproject.toml` file must be thoroughly updated. This includes not just the project name, but also adding metadata like author, description, keywords, classifiers, and the URL for the repository, which are essential for a professional PyPI package.
3.  **Public-Facing Documentation**: The `README.md` must be rewritten from a developer's log into a clear, concise, and welcoming entry point for new users. It needs installation instructions, a simple "hello world" usage example, and a brief overview of the key features. The existing documentation in the `docs/` directory also needs to be updated to reflect the new branding and purpose.
4.  **API Usability**: The user wants to import the package as `import geminiteacher as gt`. We need to ensure the package's `__init__.py` files are structured correctly to expose the main functionalities (like `create_course`) at the top level of the package for easy access.
5.  **Example Code**: The `app/` directory, which currently serves as a direct runner for the tool, should be repurposed into an `examples/` directory. This provides clear, installable-package-based examples for users, which is standard practice for libraries.

## High-level Task Breakdown

This plan is broken down into phases to ensure a smooth transition.

### Phase 1: Core Code & Project Renaming

1.  **Rename `src` Directory**: Rename `src/geminiteacher` to `src/geminiteacher`.
2.  **Update `pyproject.toml`**:
    *   Change `name = "geminiteacher"` to `name = "geminiteacher"`.
    *   Add/update metadata: `version`, `description`, `authors`, `license`, `readme`, `repository`, `keywords`, and PyPI `classifiers`.
3.  **Global Search & Replace**:
    *   Replace all occurrences of `geminiteacher` (lowercase) with `geminiteacher` across all files.
    *   Replace all occurrences of `GeminiTeacher` (PascalCase) with `GeminiTeacher` across all files.
4.  **Update Core Imports**: Modify `src/geminiteacher/__init__.py` to expose the main functions (e.g., `create_course`, `create_course_parallel`) so a user can do `from geminiteacher import create_course`.

### Phase 2: Test Suite Migration

1.  **Rename Test Files**: Rename test files in the `tests/` directory to reflect the new module names (e.g., `test_coursemaker.py` -> `test_teacher.py`).
2.  **Update Test Imports**: Ensure all tests import from `geminiteacher` and pass successfully after the renaming. This step validates that Phase 1 was successful.

### Phase 3: Documentation Overhaul

1.  **Rewrite `README.md`**:
    *   Create a new `README.md` with the following sections:
        *   Project Title: GeminiTeacher
        *   PyPI badge and other relevant badges (build status, license).
        *   Short, clear description of the project's purpose.
        *   **Installation**: `pip install geminiteacher`
        *   **Quick Start**: A simple, copy-pasteable code example.
        *   **Features**: A high-level list of what the library can do.
        *   Link to the full documentation.
2.  **Update `docs/` Content**:
    *   Rename `docs/coursemaker.md` to `docs/usage.md`.
    *   Update `mkdocs.yml` to reflect the new project name and documentation structure.
    *   Review and update all markdown files in `docs/` to use the `GeminiTeacher` name and `import geminiteacher` convention.

### Phase 4: App Integration as Submodule

1.  **Integrate `app/` as a Package Submodule**: 
    *   Move the app directory content to `src/geminiteacher/app/` to make it a proper submodule.
    *   Update imports to use the package structure.
    *   Ensure the app is accessible as `geminiteacher.app`.
2.  **Create Command-line Interface**:
    *   Add entry points in `pyproject.toml` to make the app accessible as a command-line tool.
    *   Update the script to work as both a module import and a command-line tool.
3.  **Update Supporting Files**: Update configuration files and examples to align with the new submodule structure.

### Phase 5: Final Cleanup & Verification

1.  **Review `Makefile`**: Check for any outdated references to "geminiteacher".
2.  **Build & Test Locally**: Run `uv run pytest` to ensure all tests pass. Run `uv run mkdocs build` to ensure the documentation builds without warnings. Run the example script from the `examples/` directory to ensure it works with the installed package.
3.  **Final Review**: Perform a final check of the file structure and project state before declaring completion.

## Project Status Board

- [x] **Phase 1: Core Code & Project Renaming**
  - [x] Rename `src/geminiteacher` to `src/geminiteacher`
  - [x] Update `pyproject.toml`
  - [x] Perform global search & replace for `geminiteacher` and `GeminiTeacher`
  - [x] Update `src/geminiteacher/__init__.py`
- [x] **Phase 2: Test Suite Migration**
  - [x] Rename test files
  - [x] Update test imports and verify all tests pass
- [x] **Phase 3: Documentation Overhaul**
  - [x] Rewrite `README.md`
  - [x] Update `docs/` content and `mkdocs.yml`
- [x] **Phase 4: App Integration as Submodule**
  - [x] Integrate `app/` as a package submodule
  - [x] Create command-line interface
  - [x] Update supporting files
- [x] **Phase 5: Final Cleanup & Verification**
  - [x] Review `Makefile`
  - [x] Run all local checks (tests, docs build, example script)
  - [x] Perform final review

## Executor's Feedback or Assistance Requests

Phase 1 and 2 have been completed. The user has already renamed the directories and files, and we've fixed the test failures related to:
1. Updated function signatures in parallel_generate_chapters with new parameters (course_title and output_dir)
2. Fixed mock return values in test_parallel_generate_chapters
3. Fixed error handling in parallel_generate_chapters
4. Added missing imports for Path in parallel.py
5. Fixed broken test_generate_summary_handles_empty_chapters

All tests are now passing. Moving on to Phase 3: Documentation Overhaul.

## Reviewer's Audit & Feedback

*This section will be filled out after all tasks are completed.*

## Lessons

*This section will be updated with any discoveries made during the rebranding process.* 

## Final Summary

The GeminiTeacher package has been successfully rebranded and restructured for PyPI publication. All planned phases have been completed:

1. **Core Code & Project Renaming**: Renamed all source files and directories from `cascadellm` to `geminiteacher`.
2. **Test Suite Migration**: Updated all test files and fixed test failures.
3. **Documentation Overhaul**: Rewrote the README.md and updated all documentation files.
4. **App Integration as Submodule**: Integrated the app directory as a proper submodule with a command-line interface.
5. **Final Cleanup & Verification**: Verified all tests pass and the package is ready for publication.

The package now has:
- A clean, consistent API with proper imports
- A command-line interface accessible via `geminiteacher` command
- Comprehensive documentation with examples
- A proper package structure following Python best practices

The package is now ready for publication to PyPI using the following command:
```bash
python -m build && python -m twine upload dist/*
```

Make sure to install the build and twine packages first:
```bash
pip install build twine
``` 