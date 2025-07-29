"""
Converter module for transforming different file formats to Markdown.
"""

import os
from pathlib import Path
from typing import Optional, Union


def convert_to_markdown(file_path: Union[str, Path], output_dir: Optional[str] = None) -> str:
    """
    Convert a document file (PDF, DOCX, PPTX, etc.) to Markdown text.
    
    This function uses the markitdown library to convert various document formats
    to Markdown. It supports PDF, DOCX, PPTX, and other formats.
    
    Parameters
    ----
    file_path : Union[str, Path]
        Path to the file to convert
    output_dir : Optional[str]
        Directory to save the intermediate Markdown file. If None, the file won't be saved.
        
    Returns
    ----
    str
        The converted Markdown text
        
    Raises
    ----
    ImportError
        If the markitdown library is not installed
    FileNotFoundError
        If the file does not exist
    ValueError
        If the file format is not supported
    """
    try:
        from markitdown import MarkItDown
    except ImportError:
        raise ImportError(
            "The markitdown library is required to convert documents. "
            "Please install it with: pip install markitdown[all]"
        )
    
    # Convert to Path object if string
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Initialize MarkItDown
    converter = MarkItDown()
    
    # Convert the file to Markdown
    result = converter.convert(str(file_path))
    markdown_text = result.text_content
    
    # Save the intermediate Markdown file if output_dir is specified
    if output_dir:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create output file path with .md extension
        output_file = Path(output_dir) / f"{file_path.stem}.md"
        
        # Save the Markdown text to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
    
    return markdown_text 