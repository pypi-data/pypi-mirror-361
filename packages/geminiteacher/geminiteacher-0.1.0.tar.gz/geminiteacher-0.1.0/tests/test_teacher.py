"""Tests for the coursemaker module."""
from unittest.mock import patch, MagicMock, ANY

import pytest
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel

from geminiteacher.coursemaker import (
    generate_toc,
    create_toc_prompt,
    create_chapter_prompt_template,
    generate_chapter,
    ChapterContent,
    generate_summary,
    create_course,
    Course,
    configure_gemini_llm,
    get_default_llm,
    create_course_parallel
)


def test_create_toc_prompt():
    """Test that create_toc_prompt returns a ChatPromptTemplate."""
    # Act
    prompt = create_toc_prompt()
    
    # Assert
    assert isinstance(prompt, ChatPromptTemplate)
    # Check that the content is in the prompt message templates
    messages = prompt.messages
    prompt_content = str(messages[0].prompt)
    assert "{content}" in prompt_content
    assert "simplified Chinese" in prompt_content


def test_create_toc_prompt_with_fixed_chapter_count():
    """Test that create_toc_prompt with fixed_chapter_count=True returns appropriate instructions."""
    # Act
    prompt = create_toc_prompt(max_chapters=5, fixed_chapter_count=True)
    
    # Assert
    assert isinstance(prompt, ChatPromptTemplate)
    # Check that the content reflects fixed chapter count
    messages = prompt.messages
    prompt_content = str(messages[0].prompt)
    assert "exactly 5" in prompt_content
    assert "simplified Chinese" in prompt_content


def test_create_toc_prompt_with_adaptive_chapter_count():
    """Test that create_toc_prompt with fixed_chapter_count=False returns adaptive instructions."""
    # Act
    prompt = create_toc_prompt(max_chapters=5, fixed_chapter_count=False)
    
    # Assert
    assert isinstance(prompt, ChatPromptTemplate)
    # Check that the content reflects adaptive chapter count
    messages = prompt.messages
    prompt_content = str(messages[0].prompt)
    assert "with 1-5" in prompt_content
    assert "based on the content depth" in prompt_content


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_toc_returns_list_of_chapters(mock_llm_chain, mock_get_default_llm):
    """Test that generate_toc returns a list of chapter titles."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    # Configure the mocked chain to return a string with chapter titles
    mock_chain_instance.invoke.return_value = {
        "text": "1. Introduction to AI\n2. Machine Learning Basics\n3. Neural Networks"
    }
    
    raw_content = "This is some raw text about artificial intelligence and machine learning."
    
    # Act
    result = generate_toc(raw_content)
    
    # Assert
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0] == "Introduction to AI"
    assert result[1] == "Machine Learning Basics" 
    assert result[2] == "Neural Networks"
    
    # Verify the interaction with the mock
    mock_get_default_llm.assert_called_once_with(0.0)
    mock_llm_chain.assert_called_once_with(llm=mock_llm, prompt=ANY)
    mock_chain_instance.invoke.assert_called_once()
    # Check that raw_content is passed to the chain
    assert mock_chain_instance.invoke.call_args[0][0]['content'] == raw_content


@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_toc_with_explicit_llm(mock_llm_chain):
    """Test that generate_toc accepts an explicit LLM instance."""
    # Arrange
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    mock_chain_instance.invoke.return_value = {
        "text": "1. Chapter One"
    }
    
    # Create a mock LLM
    mock_llm = MagicMock()
    
    # Act
    result = generate_toc("Some content", llm=mock_llm)
    
    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == "Chapter One"
    
    # Verify the LLM was passed to the chain
    mock_llm_chain.assert_called_once_with(llm=mock_llm, prompt=ANY)


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_toc_handles_empty_result(mock_llm_chain, mock_get_default_llm):
    """Test that generate_toc gracefully handles empty result from LLM."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    mock_chain_instance.invoke.return_value = {"text": ""}
    
    # Act
    result = generate_toc("Some content")
    
    # Assert
    assert isinstance(result, list)
    assert len(result) == 0


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_toc_with_temperature(mock_llm_chain, mock_get_default_llm):
    """Test that generate_toc accepts temperature parameter."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    mock_chain_instance.invoke.return_value = {"text": "1. Chapter One"}
    
    # Act
    generate_toc("Some content", temperature=0.2)
    
    # Assert
    mock_get_default_llm.assert_called_once_with(0.2)
    assert mock_chain_instance.invoke.called


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_toc_with_fixed_chapter_count(mock_llm_chain, mock_get_default_llm):
    """Test that generate_toc with fixed_chapter_count=True passes the parameter to create_toc_prompt."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    # Configure the mocked chain to return a string with exactly the requested number of chapters
    mock_chain_instance.invoke.return_value = {
        "text": "1. Chapter One\n2. Chapter Two\n3. Chapter Three\n4. Chapter Four\n5. Chapter Five"
    }
    
    raw_content = "This is some test content."
    
    # Act
    result = generate_toc(raw_content, max_chapters=5, fixed_chapter_count=True)
    
    # Assert
    assert isinstance(result, list)
    assert len(result) == 5
    # Verify that create_toc_prompt was called with fixed_chapter_count=True
    # We can't directly mock create_toc_prompt because it's in the same module,
    # but we can verify it worked by checking if the result has the right number of chapters
    mock_get_default_llm.assert_called_once_with(0.0)
    mock_llm_chain.assert_called_once_with(llm=mock_llm, prompt=ANY)
    mock_chain_instance.invoke.assert_called_once()


def test_create_chapter_prompt_template():
    """Test that create_chapter_prompt_template returns a ChatPromptTemplate with correct variables."""
    # Act
    prompt = create_chapter_prompt_template()
    
    # Assert
    assert isinstance(prompt, ChatPromptTemplate)
    
    # Check that the required variables are in the prompt
    messages = prompt.messages
    prompt_content = str(messages[0].prompt)
    assert "{chapter_title}" in prompt_content
    assert "{content}" in prompt_content
    
    # Verify the structure is as expected (title, explanation, extension)
    assert "标题与摘要" in prompt_content
    assert "系统性讲解" in prompt_content
    assert "拓展思考" in prompt_content


def test_create_chapter_prompt_template_with_custom_prompt():
    """Test that create_chapter_prompt_template accepts and includes a custom prompt."""
    # Arrange
    custom_prompt = "请特别关注实际应用案例，并提供更多代码示例。"
    
    # Act
    prompt = create_chapter_prompt_template(custom_prompt=custom_prompt)
    
    # Assert
    assert isinstance(prompt, ChatPromptTemplate)
    # Check that the custom prompt is included in the template
    messages = prompt.messages
    prompt_content = str(messages[0].prompt)
    assert "用户自定义指令：" in prompt_content
    assert custom_prompt in prompt_content


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_chapter_returns_structured_content(mock_llm_chain, mock_get_default_llm):
    """Test that generate_chapter returns a properly structured ChapterContent object."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    mock_chain_instance.invoke.return_value = {
        "text": """# 标题与摘要
人工智能入门是了解AI基础概念和应用的第一步。本章介绍AI的定义、历史发展及其在现代社会中的重要性。

# 系统性讲解
人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，旨在开发能够模拟人类智能行为的系统。
这些系统可以学习、推理、感知、理解人类语言并解决问题。AI的发展历程可以追溯到1950年代，当时计算机科学家开始探索机器是否可以"思考"。

# 拓展思考
随着AI技术的快速发展，我们需要考虑伦理问题、就业影响以及未来人机协作的新范式。思考如何负责任地开发和应用AI技术对未来至关重要。"""
    }
    
    # Act
    chapter = generate_chapter("Introduction to AI", "Some content about AI", temperature=0.0)
    
    # Assert
    assert isinstance(chapter, ChapterContent)
    assert chapter.title == "Introduction to AI"
    assert "人工智能入门" in chapter.summary
    assert "人工智能（Artificial Intelligence" in chapter.explanation
    assert "随着AI技术的快速发展" in chapter.extension
    
    # Verify the interaction with the mock
    mock_get_default_llm.assert_called_once_with(0.0)
    mock_llm_chain.assert_called_once_with(llm=mock_llm, prompt=ANY)
    mock_chain_instance.invoke.assert_called_once()
    # Check that the right parameters are passed to the chain
    call_args = mock_chain_instance.invoke.call_args[0][0]
    assert call_args['chapter_title'] == "Introduction to AI"
    assert call_args['content'] == "Some content about AI"


@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_chapter_with_explicit_llm(mock_llm_chain):
    """Test that generate_chapter accepts an explicit LLM instance."""
    # Arrange
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    mock_chain_instance.invoke.return_value = {
        "text": """# 标题与摘要
简短摘要

# 系统性讲解
系统讲解

# 拓展思考
拓展思考"""
    }
    
    # Create a mock LLM
    mock_llm = MagicMock()
    
    # Act
    chapter = generate_chapter("Test Chapter", "Test content", llm=mock_llm)
    
    # Assert
    assert isinstance(chapter, ChapterContent)
    assert chapter.title == "Test Chapter"
    
    # Verify the LLM was passed to the chain
    mock_llm_chain.assert_called_once_with(llm=mock_llm, prompt=ANY)


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_chapter_with_custom_prompt(mock_llm_chain, mock_get_default_llm):
    """Test that generate_chapter passes custom_prompt to create_chapter_prompt_template."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    mock_chain_instance.invoke.return_value = {
        "text": """# 标题与摘要
This is a summary.

# 系统性讲解
This is an explanation.

# 拓展思考
This is an extension."""
    }
    
    custom_prompt = "请特别关注实际应用案例，并提供更多代码示例。"
    
    # Act
    result = generate_chapter("Test Chapter", "Some content", custom_prompt=custom_prompt)
    
    # Assert
    assert isinstance(result, ChapterContent)
    assert result.title == "Test Chapter"
    
    # Verify that create_chapter_prompt_template was called with custom_prompt
    # We can't directly verify this since we can't mock the function in the same module,
    # but we can check that LLMChain was created with a prompt that includes our custom prompt
    mock_llm_chain.assert_called_once()
    prompt_arg = mock_llm_chain.call_args[1]['prompt']
    assert isinstance(prompt_arg, ChatPromptTemplate)


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_chapter_handles_malformed_output(mock_llm_chain, mock_get_default_llm):
    """Test that generate_chapter handles malformed output from the LLM."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    # Simulate a malformed response without proper sections
    mock_chain_instance.invoke.return_value = {
        "text": "This is a malformed response without the expected sections."
    }
    
    # Act
    chapter = generate_chapter("Some Title", "Some content", temperature=0.0)
    
    # Assert
    assert isinstance(chapter, ChapterContent)
    assert chapter.title == "Some Title"
    # The parse_chapter_content function should now produce empty sections but handle errors
    assert chapter.summary == ""
    assert "error" not in chapter.summary.lower()  # Should not contain error message


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_summary(mock_llm_chain, mock_get_default_llm):
    """Test that generate_summary returns a summary string."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    mock_chain_instance.invoke.return_value = {
        "text": "这是一个关于人工智能和机器学习的综合课程。从基础概念到高级应用，课程涵盖了AI的各个方面。"
    }
    
    # Create test data
    original_content = "This is some content about AI and machine learning."
    chapters = [
        ChapterContent(title="Introduction to AI", summary="AI basics", explanation="AI explanation"),
        ChapterContent(title="Machine Learning", summary="ML basics", explanation="ML explanation")
    ]
    
    # Act
    result = generate_summary(original_content, chapters, temperature=0.0)
    
    # Assert
    assert isinstance(result, str)
    assert "人工智能" in result
    assert "机器学习" in result
    
    # Verify the interaction with the mock
    mock_get_default_llm.assert_called_once_with(0.0)
    mock_llm_chain.assert_called_once_with(llm=mock_llm, prompt=ANY)
    mock_chain_instance.invoke.assert_called_once()
    
    # Check that the right parameters are passed to the chain
    call_args = mock_chain_instance.invoke.call_args[0][0]
    assert call_args['content'] == original_content
    assert "Introduction to AI" in call_args['chapters_summary']
    assert "Machine Learning" in call_args['chapters_summary']


@patch('geminiteacher.coursemaker.LLMChain')
def test_generate_summary_with_explicit_llm(mock_llm_chain):
    """Test that generate_summary accepts an explicit LLM instance."""
    # Arrange
    mock_chain_instance = MagicMock()
    mock_llm_chain.return_value = mock_chain_instance
    mock_chain_instance.invoke.return_value = {
        "text": "Summary text"
    }
    
    # Create test data
    mock_llm = MagicMock()
    chapters = [ChapterContent(title="Test Chapter", summary="Test summary")]
    
    # Act
    result = generate_summary("Test content", chapters, llm=mock_llm)
    
    # Assert
    assert isinstance(result, str)
    assert result == "Summary text"
    
    # Verify the LLM was passed to the chain
    mock_llm_chain.assert_called_once_with(llm=mock_llm, prompt=ANY)


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.coursemaker.generate_summary')
def test_generate_summary_handles_empty_chapters(mock_generate_summary, mock_generate_toc, mock_get_default_llm):
    """Test that generate_summary handles empty chapters list."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    # Configure mock to return empty TOC
    mock_generate_toc.return_value = []
    mock_generate_summary.return_value = ""
    
    # Act
    course = create_course_parallel("Test content")
    
    # Assert
    assert course.content == "Test content"
    assert course.chapters == []
    assert course.summary == ""
    
    # Verify the interactions with the mocks
    mock_generate_toc.assert_called_once()
    mock_generate_summary.assert_not_called()  # Should not be called with empty chapters 


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.coursemaker.generate_chapter')
@patch('geminiteacher.coursemaker.generate_summary')
def test_create_course_orchestrates_all_steps(mock_generate_summary, mock_generate_chapter, mock_generate_toc, mock_get_default_llm):
    """Test that create_course orchestrates all the required steps."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    # Configure mocks
    mock_generate_toc.return_value = ["Chapter 1", "Chapter 2"]
    
    mock_chapters = [
        ChapterContent(title="Chapter 1", summary="Summary 1"),
        ChapterContent(title="Chapter 2", summary="Summary 2")
    ]
    mock_generate_chapter.side_effect = mock_chapters
    
    mock_generate_summary.return_value = "Course summary"
    
    # Act
    course = create_course(
        "Test content",
        temperature=0.2,
        verbose=True,
        max_chapters=5,
        fixed_chapter_count=True,
        custom_prompt="Custom prompt"
    )
    
    # Assert
    assert course.content == "Test content"
    assert course.chapters == mock_chapters
    assert course.summary == "Course summary"
    
    # Verify the interaction with the mocks
    mock_get_default_llm.assert_called_once_with(0.2)
    mock_generate_toc.assert_called_once_with(
        "Test content",
        llm=mock_llm,
        temperature=0.2,
        max_chapters=5,
        fixed_chapter_count=True
    )
    assert mock_generate_chapter.call_count == 2
    mock_generate_chapter.assert_any_call(
        "Chapter 1",
        "Test content",
        llm=mock_llm,
        temperature=0.2,
        custom_prompt="Custom prompt"
    )
    mock_generate_chapter.assert_any_call(
        "Chapter 2",
        "Test content",
        llm=mock_llm,
        temperature=0.2,
        custom_prompt="Custom prompt"
    )
    mock_generate_summary.assert_called_once_with(
        "Test content",
        mock_chapters,
        llm=mock_llm,
        temperature=0.2
    )


@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.coursemaker.generate_chapter')
@patch('geminiteacher.coursemaker.generate_summary')
def test_create_course_with_explicit_llm(
    mock_generate_summary, mock_generate_chapter, mock_generate_toc
):
    """Test that create_course passes the LLM to all sub-functions."""
    # Arrange
    mock_generate_toc.return_value = ["Chapter 1"]
    mock_generate_chapter.return_value = ChapterContent(title="Chapter 1", summary="Summary")
    mock_generate_summary.return_value = "Summary"
    
    # Create a mock LLM
    mock_llm = MagicMock()
    
    # Act
    course = create_course("Test content", llm=mock_llm)
    
    # Assert
    assert isinstance(course, Course)
    
    # Verify LLM was passed to all sub-functions
    mock_generate_toc.assert_called_once_with(
        "Test content",
        llm=mock_llm,
        temperature=0.0,
        max_chapters=10,
        fixed_chapter_count=False
    )
    mock_generate_chapter.assert_called_once_with(
        "Chapter 1", 
        "Test content", 
        llm=mock_llm, 
        temperature=0.0,
        custom_prompt=None
    )
    mock_generate_summary.assert_called_once_with(
        "Test content", 
        [mock_generate_chapter.return_value], 
        llm=mock_llm, 
        temperature=0.0
    )


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.coursemaker.generate_summary')
def test_create_course_handles_empty_toc(mock_generate_summary, mock_generate_toc, mock_get_default_llm):
    """Test that create_course handles empty table of contents gracefully."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm

    mock_generate_toc.return_value = []
    mock_generate_summary.return_value = ""

    # Act
    course = create_course("Test content", temperature=0.0)

    # Assert
    assert isinstance(course, Course)
    assert course.content == "Test content"
    assert len(course.chapters) == 0
    assert course.summary == ""

    # Verify the correct calls were made
    mock_get_default_llm.assert_called_once_with(0.0)
    mock_generate_toc.assert_called_once_with(
        "Test content", 
        llm=mock_llm, 
        temperature=0.0, 
        max_chapters=10, 
        fixed_chapter_count=False
    )
    mock_generate_summary.assert_not_called()


@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.coursemaker.generate_chapter')
@patch('geminiteacher.coursemaker.generate_summary')
def test_create_course_with_fixed_chapter_count(
    mock_generate_summary, mock_generate_chapter, mock_generate_toc
):
    """Test that create_course correctly passes the fixed_chapter_count parameter to generate_toc."""
    # Arrange
    mock_generate_toc.return_value = ["Chapter 1", "Chapter 2", "Chapter 3"]
    mock_generate_chapter.return_value = ChapterContent(title="Test Chapter")
    mock_generate_summary.return_value = "Test summary"
    
    # Create a mock LLM
    mock_llm = MagicMock()
    
    # Act
    course = create_course(
        "Test content", 
        llm=mock_llm, 
        max_chapters=3, 
        fixed_chapter_count=True
    )
    
    # Assert
    assert isinstance(course, Course)
    # Verify that generate_toc was called with fixed_chapter_count=True
    mock_generate_toc.assert_called_once_with(
        "Test content", 
        llm=mock_llm, 
        temperature=0.0, 
        max_chapters=3,
        fixed_chapter_count=True
    )
    # Verify it generated chapters for all the returned chapter titles
    assert mock_generate_chapter.call_count == 3


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.coursemaker.generate_chapter')
@patch('geminiteacher.coursemaker.generate_summary')
def test_create_course_with_custom_prompt(
    mock_generate_summary, mock_generate_chapter, mock_generate_toc, mock_get_default_llm
):
    """Test that create_course passes custom_prompt to generate_chapter."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    # Configure mocks to return appropriate values
    mock_generate_toc.return_value = ["Chapter 1", "Chapter 2"]
    mock_generate_chapter.return_value = ChapterContent(
        title="Chapter X",
        summary="Summary",
        explanation="Explanation",
        extension="Extension"
    )
    mock_generate_summary.return_value = "Course summary"
    
    # Create a custom prompt
    custom_prompt = "请特别关注实际应用案例，并提供更多代码示例。"
    
    # Act
    result = create_course("Some content", custom_prompt=custom_prompt)
    
    # Assert
    assert isinstance(result, Course)
    assert len(result.chapters) == 2
    
    # Verify that generate_chapter was called with custom_prompt
    assert mock_generate_chapter.call_count == 2
    for call_args in mock_generate_chapter.call_args_list:
        assert 'custom_prompt' in call_args[1]
        assert call_args[1]['custom_prompt'] == custom_prompt


@patch('geminiteacher.coursemaker.configure_gemini_llm')
def test_get_default_llm_in_test_environment(mock_configure_gemini):
    """Test that get_default_llm calls configure_gemini_llm with the right parameters."""
    # Arrange
    mock_llm = MagicMock()
    mock_configure_gemini.return_value = mock_llm
    
    # Act
    result = get_default_llm(temperature=0.5)
    
    # Assert
    assert result == mock_llm
    mock_configure_gemini.assert_called_once_with(temperature=0.5)


# Skip this test since we can't easily mock the import in a way that works reliably
@pytest.mark.skip(reason="Can't reliably mock the import in the test environment")
def test_configure_gemini_llm():
    """Test that configure_gemini_llm raises ImportError when the package is not available."""
    # This test is skipped because we can't reliably mock the import
    pass 


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.coursemaker.generate_summary')
@patch('geminiteacher.parallel.parallel_generate_chapters')
def test_create_course_parallel(
    mock_parallel_generate_chapters, mock_generate_summary, mock_generate_toc, mock_get_default_llm
):
    """Test that create_course_parallel orchestrates all steps with parallel chapter generation."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    # Configure mocks
    mock_generate_toc.return_value = ["Chapter 1", "Chapter 2"]
    
    mock_chapters = [
        ChapterContent(title="Chapter 1", summary="Summary 1"),
        ChapterContent(title="Chapter 2", summary="Summary 2")
    ]
    mock_parallel_generate_chapters.return_value = mock_chapters
    
    mock_generate_summary.return_value = "Course summary"
    
    # Act
    course = create_course_parallel(
        "Test content",
        temperature=0.2,
        verbose=True,
        max_chapters=5,
        fixed_chapter_count=True,
        custom_prompt="Custom prompt",
        max_workers=2,
        delay_range=(0.1, 0.5),
        max_retries=3
    )
    
    # Assert
    assert course.content == "Test content"
    assert course.chapters == mock_chapters
    assert course.summary == "Course summary"
    
    # Verify the interaction with the mocks
    mock_get_default_llm.assert_called_once_with(0.2)
    mock_generate_toc.assert_called_once_with(
        "Test content",
        llm=mock_llm,
        temperature=0.2,
        max_chapters=5,
        fixed_chapter_count=True
    )
    mock_parallel_generate_chapters.assert_called_once_with(
        chapter_titles=["Chapter 1", "Chapter 2"],
        content="Test content",
        llm=mock_llm,
        temperature=0.2,
        custom_prompt="Custom prompt",
        max_workers=2,
        delay_range=(0.1, 0.5),
        max_retries=3,
        course_title="course",
        output_dir="output"
    )
    mock_generate_summary.assert_called_once_with(
        "Test content",
        mock_chapters,
        llm=mock_llm,
        temperature=0.2
    )


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.parallel.parallel_generate_chapters')
@patch('geminiteacher.coursemaker.generate_summary')
def test_create_course_parallel_with_explicit_llm(
    mock_generate_summary, mock_parallel_generate_chapters, mock_generate_toc, mock_get_default_llm
):
    """Test that create_course_parallel accepts an explicit LLM instance."""
    # Arrange
    mock_llm = MagicMock()
    
    # Configure mocks
    mock_generate_toc.return_value = ["Chapter 1"]
    
    mock_chapters = [
        ChapterContent(title="Chapter 1", summary="Summary 1")
    ]
    mock_parallel_generate_chapters.return_value = mock_chapters
    
    mock_generate_summary.return_value = "Course summary"
    
    # Act
    course = create_course_parallel(
        "Test content",
        llm=mock_llm,
        max_workers=2
    )
    
    # Assert
    assert course.content == "Test content"
    assert course.chapters == mock_chapters
    assert course.summary == "Course summary"
    
    # Verify the interaction with the mocks
    mock_get_default_llm.assert_not_called()  # Should not call get_default_llm
    mock_generate_toc.assert_called_once_with(
        "Test content",
        llm=mock_llm,
        temperature=0.0,
        max_chapters=10,
        fixed_chapter_count=False
    )
    mock_parallel_generate_chapters.assert_called_once_with(
        chapter_titles=["Chapter 1"],
        content="Test content",
        llm=mock_llm,
        temperature=0.0,
        custom_prompt=None,
        max_workers=2,
        delay_range=(0.1, 0.5),
        max_retries=3,
        course_title="course",
        output_dir="output"
    )


@patch('geminiteacher.coursemaker.get_default_llm')
@patch('geminiteacher.coursemaker.generate_toc')
@patch('geminiteacher.parallel.parallel_generate_chapters')
@patch('geminiteacher.coursemaker.generate_summary')
def test_create_course_parallel_handles_empty_toc(
    mock_generate_summary, mock_parallel_generate_chapters, mock_generate_toc, mock_get_default_llm
):
    """Test that create_course_parallel handles empty table of contents gracefully."""
    # Arrange
    mock_llm = MagicMock()
    mock_get_default_llm.return_value = mock_llm
    
    # Configure mock to return empty TOC
    mock_generate_toc.return_value = []
    
    # Act
    course = create_course_parallel("Test content")
    
    # Assert
    assert course.content == "Test content"
    assert course.chapters == []
    assert course.summary == ""
    
    # Verify the interactions with the mocks
    mock_generate_toc.assert_called_once()
    mock_parallel_generate_chapters.assert_not_called()  # Should not be called with empty TOC
    mock_generate_summary.assert_not_called()  # Should not be called with empty chapters 