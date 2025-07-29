"""Tests for the parallel processing module."""
from unittest.mock import patch, MagicMock, ANY
import pytest

from geminiteacher.parallel import (
    generate_chapter_with_retry,
    parallel_map_with_delay,
    parallel_generate_chapters,
    _worker_generate_chapter,
    _worker_generate_and_save_chapter,
    save_chapter_to_file
)
from geminiteacher.coursemaker import ChapterContent


@patch('geminiteacher.parallel.generate_chapter')
def test_generate_chapter_with_retry_success_first_attempt(mock_generate_chapter):
    """Test that generate_chapter_with_retry returns the chapter on first successful attempt."""
    # Arrange
    mock_chapter = ChapterContent(
        title="Test Chapter",
        summary="Test summary",
        explanation="Test explanation",
        extension="Test extension"
    )
    mock_generate_chapter.return_value = mock_chapter
    
    # Act
    result = generate_chapter_with_retry(
        chapter_title="Test Chapter",
        content="Test content",
        llm=None,
        temperature=0.0,
        custom_prompt=None
    )
    
    # Assert
    assert result == mock_chapter
    mock_generate_chapter.assert_called_once_with(
        chapter_title="Test Chapter",
        content="Test content",
        llm=None,
        temperature=0.0,
        custom_prompt=None
    )


@patch('geminiteacher.parallel.time.sleep')
@patch('geminiteacher.parallel.generate_chapter')
def test_generate_chapter_with_retry_empty_response_then_success(mock_generate_chapter, mock_sleep):
    """Test that generate_chapter_with_retry retries on empty explanation and succeeds."""
    # Arrange
    empty_chapter = ChapterContent(
        title="Test Chapter",
        summary="Test summary",
        explanation="",
        extension="Test extension"
    )
    good_chapter = ChapterContent(
        title="Test Chapter",
        summary="Test summary",
        explanation="Good explanation",
        extension="Test extension"
    )
    
    # Configure mock to return empty chapter first, then good chapter
    mock_generate_chapter.side_effect = [empty_chapter, good_chapter]
    
    # Act
    result = generate_chapter_with_retry(
        chapter_title="Test Chapter",
        content="Test content",
        max_retries=3,
        retry_delay=0.1
    )
    
    # Assert
    assert result == good_chapter
    assert mock_generate_chapter.call_count == 2
    mock_sleep.assert_called_once()  # Should sleep once between retries


@patch('geminiteacher.parallel.time.sleep')
@patch('geminiteacher.parallel.generate_chapter')
def test_generate_chapter_with_retry_exception_then_success(mock_generate_chapter, mock_sleep):
    """Test that generate_chapter_with_retry retries on exception and succeeds."""
    # Arrange
    good_chapter = ChapterContent(
        title="Test Chapter",
        summary="Test summary",
        explanation="Good explanation",
        extension="Test extension"
    )
    
    # Configure mock to raise exception first, then return good chapter
    mock_generate_chapter.side_effect = [ValueError("API error"), good_chapter]
    
    # Act
    result = generate_chapter_with_retry(
        chapter_title="Test Chapter",
        content="Test content",
        max_retries=3,
        retry_delay=0.1
    )
    
    # Assert
    assert result == good_chapter
    assert mock_generate_chapter.call_count == 2
    mock_sleep.assert_called_once()  # Should sleep once between retries


@patch('geminiteacher.parallel.time.sleep')
@patch('geminiteacher.parallel.generate_chapter')
def test_generate_chapter_with_retry_all_attempts_fail(mock_generate_chapter, mock_sleep):
    """Test that generate_chapter_with_retry returns error chapter when all attempts fail."""
    # Arrange
    mock_generate_chapter.side_effect = ValueError("API error")
    
    # Act
    result = generate_chapter_with_retry(
        chapter_title="Test Chapter",
        content="Test content",
        max_retries=2,
        retry_delay=0.1
    )
    
    # Assert
    assert isinstance(result, ChapterContent)
    assert result.title == "Test Chapter"
    assert "Error" in result.summary
    assert "encountered repeated errors" in result.explanation
    assert mock_generate_chapter.call_count == 3  # Initial + 2 retries
    assert mock_sleep.call_count == 2  # Should sleep between each retry


@patch('geminiteacher.parallel.ProcessPoolExecutor')
@patch('geminiteacher.parallel.time.sleep')
def test_parallel_map_with_delay(mock_sleep, mock_process_pool_executor):
    """Test that parallel_map_with_delay correctly processes items in parallel."""
    # Arrange
    mock_executor = MagicMock()
    mock_process_pool_executor.return_value.__enter__.return_value = mock_executor
    
    # Set up mock futures
    mock_futures = []
    for i in range(3):
        mock_future = MagicMock()
        mock_future.result.return_value = i * 2  # Simple transformation
        mock_futures.append(mock_future)
    
    mock_executor.submit.side_effect = mock_futures
    
    # Define test function and items
    def test_func(x, factor=1):
        return x * factor
    
    items = [1, 2, 3]
    
    # Act
    results = parallel_map_with_delay(
        test_func,
        items,
        max_workers=2,
        delay_range=(0.1, 0.2),
        factor=2
    )
    
    # Assert
    assert results == [0, 2, 4]  # Values from the mock futures
    assert mock_executor.submit.call_count == 3
    assert mock_sleep.call_count == 3  # Should sleep before each submission
    
    # Check that function and args were passed correctly
    mock_executor.submit.assert_any_call(test_func, 1, factor=2)
    mock_executor.submit.assert_any_call(test_func, 2, factor=2)
    mock_executor.submit.assert_any_call(test_func, 3, factor=2)


@patch('geminiteacher.parallel.parallel_map_with_delay')
def test_parallel_generate_chapters(mock_parallel_map_with_delay):
    """Test that parallel_generate_chapters correctly delegates to parallel_map_with_delay."""
    # Arrange
    mock_chapters = [
        ChapterContent(title="Chapter 1", summary="Summary 1"),
        ChapterContent(title="Chapter 2", summary="Summary 2")
    ]
    # Mock the return value to match the expected format: list of tuples (idx, chapter, file_path)
    mock_return = [
        (0, mock_chapters[0], "path/to/chapter1.md"),
        (1, mock_chapters[1], "path/to/chapter2.md")
    ]
    mock_parallel_map_with_delay.return_value = mock_return
    
    chapter_titles = ["Chapter 1", "Chapter 2"]
    content = "Test content"
    mock_llm = MagicMock()
    mock_llm.google_api_key = "fake_api_key"
    mock_llm.model = "gemini-1.5-pro"
    
    # Act
    result = parallel_generate_chapters(
        chapter_titles=chapter_titles,
        content=content,
        llm=mock_llm,
        temperature=0.5,
        custom_prompt="Custom prompt",
        max_workers=2,
        delay_range=(0.2, 0.3),
        max_retries=2,
        course_title="test_course",
        output_dir="test_output"
    )
    
    # Assert
    assert result == mock_chapters
    
    # Check that parallel_map_with_delay was called with the correct parameters
    # We need to check that it's called with _worker_generate_and_save_chapter and tuples of (index, title)
    mock_parallel_map_with_delay.assert_called_once()
    
    # Get the actual call arguments
    call_args = mock_parallel_map_with_delay.call_args
    
    # Check the function argument (should be _worker_generate_and_save_chapter)
    assert call_args[0][0] == _worker_generate_and_save_chapter
    
    # Check the items argument (should be list of (index, title) tuples)
    items_arg = call_args[0][1]
    assert isinstance(items_arg, list)
    assert len(items_arg) == 2
    assert items_arg[0] == (0, "Chapter 1")
    assert items_arg[1] == (1, "Chapter 2")
    
    # Check the keyword arguments
    assert call_args[1]['max_workers'] == 2
    assert call_args[1]['delay_range'] == (0.2, 0.3)
    assert call_args[1]['content'] == content
    assert call_args[1]['api_key'] == "fake_api_key"
    assert call_args[1]['model_name'] == "gemini-1.5-pro"
    assert call_args[1]['temperature'] == 0.5
    assert call_args[1]['custom_prompt'] == "Custom prompt"
    assert call_args[1]['max_retries'] == 2
    assert call_args[1]['course_title'] == "test_course"
    assert call_args[1]['output_dir'] == "test_output"


@patch('geminiteacher.coursemaker.configure_gemini_llm')
@patch('geminiteacher.parallel.generate_chapter_with_retry')
def test_worker_generate_chapter(mock_generate_chapter_with_retry, mock_configure_gemini_llm):
    """Test that _worker_generate_chapter correctly initializes an LLM and generates a chapter."""
    # Arrange
    mock_llm = MagicMock()
    mock_configure_gemini_llm.return_value = mock_llm
    
    mock_chapter = ChapterContent(
        title="Test Chapter",
        summary="Test summary",
        explanation="Good explanation",
        extension="Test extension"
    )
    mock_generate_chapter_with_retry.return_value = mock_chapter
    
    chapter_item = (0, "Test Chapter")
    content = "Test content"
    
    # Act
    result = _worker_generate_chapter(
        chapter_item=chapter_item,
        content=content,
        api_key="test_api_key",
        model_name="test-model",
        temperature=0.7,
        custom_prompt="Test prompt",
        max_retries=2,
        retry_delay=0.5
    )
    
    # Assert
    assert result == mock_chapter
    
    # Check that LLM was configured correctly
    mock_configure_gemini_llm.assert_called_once_with(
        api_key="test_api_key",
        model_name="test-model",
        temperature=0.7
    )
    
    # Check that generate_chapter_with_retry was called correctly
    mock_generate_chapter_with_retry.assert_called_once_with(
        chapter_title="Test Chapter",
        content=content,
        llm=mock_llm,
        temperature=0.7,
        custom_prompt="Test prompt",
        max_retries=2,
        retry_delay=0.5
    ) 