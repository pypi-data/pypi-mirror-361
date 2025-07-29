"""Tests for the file converter module."""
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from geminiteacher.converter import convert_to_markdown


def test_convert_to_markdown_basic_usage():
    """
    Tests that the convert_to_markdown wrapper correctly uses the MarkItDown library.
    """
    # Arrange
    # Create a mock instance for the MarkItDown class
    mock_instance = MagicMock()
    mock_result = MagicMock()
    mock_result.text_content = "# Mocked Markdown"
    mock_instance.convert.return_value = mock_result
    mock_markitdown = MagicMock()
    mock_markitdown.MarkItDown.return_value = mock_instance
    
    # Mock Path behavior
    mock_path_instance = MagicMock()
    mock_path_instance.exists.return_value = True
    mock_path_instance.stem = "file"

    file_path = "dummy/path/to/file.pdf"

    # Act
    with patch('geminiteacher.converter.Path', return_value=mock_path_instance):
        with patch.dict('sys.modules', {'markitdown': mock_markitdown}):
            result = convert_to_markdown(file_path)

    # Assert
    # Verify that the convert method was called on the instance with the correct file path
    mock_instance.convert.assert_called_once_with(str(mock_path_instance))

    # Verify that the function returns the expected text content
    assert result == "# Mocked Markdown"


def test_convert_to_markdown_with_output_dir():
    """
    Tests that the convert_to_markdown function saves output to the specified directory.
    """
    # Arrange
    # Create a mock instance for the MarkItDown class
    mock_instance = MagicMock()
    mock_result = MagicMock()
    mock_result.text_content = "# Mocked Markdown"
    mock_instance.convert.return_value = mock_result
    mock_markitdown = MagicMock()
    mock_markitdown.MarkItDown.return_value = mock_instance
    
    # Mock Path behavior
    mock_path_instance = MagicMock()
    mock_path_instance.exists.return_value = True
    mock_path_instance.stem = "file"
    
    # Setup mocks
    mock_makedirs = MagicMock()
    mock_file = mock_open()

    file_path = "dummy/path/to/file.pdf"
    output_dir = "output/folder"

    # Act
    with patch('geminiteacher.converter.Path', return_value=mock_path_instance):
        with patch.dict('sys.modules', {'markitdown': mock_markitdown}):
            with patch('geminiteacher.converter.os.makedirs', mock_makedirs):
                with patch('builtins.open', mock_file):
                    result = convert_to_markdown(file_path, output_dir=output_dir)

    # Assert
    # Verify directory creation
    mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)
    
    # Verify file was opened for writing
    mock_file.assert_called_once()
    
    # Verify content was written to the file
    mock_file().write.assert_called_once_with("# Mocked Markdown")
    
    # Verify that the function returns the expected text content
    assert result == "# Mocked Markdown" 