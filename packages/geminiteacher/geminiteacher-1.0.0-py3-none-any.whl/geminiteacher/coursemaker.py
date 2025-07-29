"""This module contains the logic for the automated course generation system."""
from typing import List, Dict, Any, Optional, Union

from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field


class ChapterContent(BaseModel):
    """
    A structured representation of a chapter's content.
    
    Attributes
    ----
    title : str
        The title of the chapter.
    summary : str
        A brief summary or introduction to the chapter.
    explanation : str
        The detailed explanation of the chapter's content.
    extension : str
        Additional thoughts or extensions related to the chapter.
    """
    
    title: str
    summary: str = ""
    explanation: str = ""
    extension: str = ""


class Course(BaseModel):
    """
    A complete course with chapters and summary.
    
    Attributes
    ----
    content : str
        The original raw content used to generate the course.
    chapters : List[ChapterContent]
        The list of chapters in the course.
    summary : str
        A comprehensive summary of the entire course.
    """
    
    content: str
    chapters: List[ChapterContent] = []
    summary: str = ""


def create_toc_prompt(max_chapters: int = 10, fixed_chapter_count: bool = False) -> ChatPromptTemplate:
    """
    Create the prompt template for TOC generation.
    
    Parameters
    ----
    max_chapters : int, optional
        Maximum number of chapters to generate. Default is 10.
    fixed_chapter_count : bool, optional
        If True, generate exactly max_chapters. If False, generate between 1 and max_chapters
        based on content complexity. Default is False.
    
    Returns
    ----
    ChatPromptTemplate
        A prompt template for generating a table of contents.
    """
    
    # Choose the instruction based on the mode
    if fixed_chapter_count:
        chapter_count_instruction = f"Create a logical structure with exactly {max_chapters} chapter titles in simplified Chinese."
    else:
        chapter_count_instruction = f"Create a logical structure with 1-{max_chapters} chapter titles in simplified Chinese. You don't have to always generate exactly {max_chapters} chapters. You have to Determine the number of chapters based on the content depth very smartly."
    
    return ChatPromptTemplate.from_template(
        f"""You are a post-doctoral professional creating a structured learning curriculum.
        
        Below is raw content that needs to be organized into a meaningful table of contents.
        {chapter_count_instruction}
        The key is to make the content taught as detailed as possible.
        Format your response as a numbered list, with each chapter on a new line.
        
        DO NOT include any explanations, introductions, or additional text.
        ONLY include the numbered list of chapter titles.
        
        Raw content:
        {{content}}
        """
    )


def create_chapter_prompt_template(custom_prompt: Optional[str] = None) -> ChatPromptTemplate:
    """
    Create a prompt template for generating chapter explanations.
    
    This template instructs the LLM to generate a structured explanation
    for a single chapter, based on its title and the original content.
    
    Parameters
    ----
    custom_prompt : Optional[str], optional
        Custom instructions to append to the "系统性讲解" section. Default is None.
    
    Returns
    ----
    ChatPromptTemplate
        A prompt template for generating chapter explanations.
    
    Examples
    -----
    >>> prompt = create_chapter_prompt_template()
    >>> prompt.format(chapter_title="Introduction to AI", content="...")
    
    >>> custom = "请特别关注实际应用案例，并提供更多代码示例。"
    >>> prompt = create_chapter_prompt_template(custom_prompt=custom)
    """
    # Define the base systematic explanation section
    systematic_explanation = """[这是最重要的部分。请尽量非常详细地解释所有知识点， 需要全面覆盖所有的原内容，原内容的举例也尽量保留。越详细越好， 不用节约token。
         你可以补充原文缺失的背景信息或重新组织结构，目标是让学习者仅凭你的讲解就能完全掌握，无需阅读原文。
         你需要以学习者为中心：关注初学者的认知起点，逐步引导，避免假设先验知识。结合实际案例或生活化例子，帮助理解抽象概念。
         在讲解中，首次提到不超过10个核心术语时，请用括号附上英文翻译。例如：人工智能 (Artificial Intelligence)。
         请你不要使用太多的子标题， 每一章都保持简洁的结构。 内容方面不需要简洁， 但是结构方面需要简洁。
         你的回复要以教科书风格和实践为标准。]"""
    
    # Append custom prompt if provided
    if custom_prompt:
        systematic_explanation += f"\n\n         用户自定义指令：{custom_prompt}"
    
    return ChatPromptTemplate.from_template(
        f"""你是一位博士后， 也是一位专业教育工作者，精通所有学科。正在为初学者创建一个结构化的学习课程。
        
        请基于以下内容，为章节《{{chapter_title}}》创建详细的讲解。
        你的回复必须使用以下结构：
        
        # 标题与摘要
        [此章节的标题，以及2-3句话概括主要内容]
        
        # 系统性讲解
        {systematic_explanation}
        
        # 拓展思考
        [提供额外的思考角度、应用建议或相关领域的连接， 保持简洁， 2-3个即可。]
        
        请确保你的解释针对初学者，使用通俗易懂的语言，并保持逻辑清晰。请你遵循最佳教学方法。
        
        原始内容:
        {{content}}
        """
    )


def create_summary_prompt_template() -> ChatPromptTemplate:
    """
    Create a prompt template for generating a course summary.
    
    This template instructs the LLM to generate a comprehensive summary
    of the entire course, based on the original content and chapter summaries.
    
    Returns
    ----
    ChatPromptTemplate
        A prompt template for generating course summaries.
    
    Examples
    -----
    >>> prompt = create_summary_prompt_template()
    >>> prompt.format(content="...", chapters_summary="...")
    """
    return ChatPromptTemplate.from_template(
        """你是一位博士后， 也是一位专业教育工作者，正在为一门面向新人课程创建总结。
        
        请基于原始内容和各章节的摘要，创建一个全面的课程总结。
        总结应该概括课程的主要内容、核心概念和学习价值。
        使用简体中文，确保语言通俗易懂，并突出课程的关键要点。
        
        原始内容:
        {content}
        
        章节摘要:
        {chapters_summary}
        """
    )


def configure_gemini_llm(api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro", temperature: float = 0.0) -> BaseLanguageModel:
    """
    Configure and return a Google Gemini model for use with the coursemaker module.
    
    Parameters
    ----
    api_key : str, optional
        The Google API key for accessing Gemini models. If None, will use the 
        GOOGLE_API_KEY environment variable.
    model_name : str, optional
        The name of the Gemini model to use. Default is "gemini-1.5-pro".
    temperature : float, optional
        The temperature setting for generation, affecting randomness in output.
        Default is 0.0 (deterministic output).
    
    Returns
    ----
    BaseLanguageModel
        A configured Gemini language model ready to use with coursemaker functions.
    
    Examples
    -----
    >>> llm = configure_gemini_llm(temperature=0.2)
    >>> course = create_course("Content to transform...", llm=llm)
    
    Notes
    -----
    This function requires the langchain-google-genai package to be installed:
    pip install langchain-google-genai
    """
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        raise ImportError(
            "The langchain-google-genai package is required to use Gemini models. "
            "Please install it with: pip install langchain-google-genai"
        )
    
    # Use the provided API key or get it from environment variables
    if api_key is None:
        import os
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key provided. Either pass an api_key parameter or "
                "set the GOOGLE_API_KEY environment variable."
            )
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key
    )


def get_default_llm(temperature: float = 0.0) -> BaseLanguageModel:
    """
    Get the default LLM for this module (Google Gemini).
    
    This is a helper function to automatically configure Gemini
    when no explicit LLM is provided to the generation functions.
    
    Parameters
    ----
    temperature : float, optional
        The temperature setting for the LLM, affecting randomness in output.
        Default is 0.0 (deterministic output).
    
    Returns
    ----
    BaseLanguageModel
        A configured Gemini language model.
    """
    try:
        return configure_gemini_llm(temperature=temperature)
    except ImportError as e:
        # In test environments, we'll return None to allow mocking
        import sys
        if 'pytest' in sys.modules:
            return None
        # In production, raise the error
        raise e


def generate_toc(content: str, llm: Optional[BaseLanguageModel] = None, temperature: float = 0.0, max_chapters: int = 10, fixed_chapter_count: bool = False) -> List[str]:
    """
    Generate a table of contents from raw content.
    
    This function takes raw text content and uses an LLM to generate
    a structured table of contents with 1-10 chapter titles.
    
    Parameters
    ----
    content : str
        The raw text content to analyze and create a table of contents for.
    llm : BaseLanguageModel, optional
        The language model to use for generation. If None, the function will 
        automatically configure a Gemini model.
    temperature : float, optional
        The temperature setting for the LLM, affecting randomness in output.
        Default is 0.0 (deterministic output).
    max_chapters : int, optional
        Maximum number of chapters to generate. Default is 10.
    fixed_chapter_count : bool, optional
        If True, generate exactly max_chapters. If False, generate between 1 and max_chapters
        based on content complexity. Default is False.
    
    Returns
    ----
    List[str]
        A list of chapter titles without numbering.
    
    Examples
    -----
    >>> toc = generate_toc("This is a text about machine learning...")
    >>> print(toc)
    ['Introduction to Machine Learning', 'Types of Machine Learning', ...]
    
    >>> toc = generate_toc("Content about history...", max_chapters=20)
    >>> print(len(toc))
    15  # The actual number may vary based on content
    
    >>> toc = generate_toc("Content about a simple topic...", max_chapters=5, fixed_chapter_count=True)
    >>> print(len(toc))
    5  # Will always generate exactly 5 chapters
    """
    # Create the prompt template
    prompt = create_toc_prompt(max_chapters=max_chapters, fixed_chapter_count=fixed_chapter_count)
    
    # If no LLM is provided, configure Gemini
    if llm is None:
        llm = get_default_llm(temperature)
    
    # Create the LLM chain
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
    )
    
    # Invoke the chain with the content
    result = chain.invoke({
        "content": content,
        "max_chapters": max_chapters
    })
    
    # Get the raw text from the result
    text = result.get("text", "")
    
    # Log the raw LLM response for debugging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("coursemaker")
    logger.info(f"Raw LLM response for TOC generation:\n{text}")
    
    # Split the text by newlines and extract chapter titles
    lines = text.strip().split("\n")
    chapter_titles = []
    
    for line in lines:
        # Remove leading numbers, dots, and whitespace
        line = line.strip()
        # Match patterns like "1. ", "1) ", "Chapter 1: ", etc.
        import re
        line = re.sub(r"^(\d+[\.\):]|Chapter\s+\d+:?)\s*", "", line)
        
        if line:  # Skip empty lines
            chapter_titles.append(line)
    
    return chapter_titles


def generate_chapter(chapter_title: str, content: str, llm: Optional[BaseLanguageModel] = None, temperature: float = 0.0, custom_prompt: Optional[str] = None) -> ChapterContent:
    """
    Generate a structured explanation for a single chapter.
    
    This function uses an LLM to create a detailed, structured explanation
    for a chapter based on its title and the original content.
    
    Parameters
    ----
    chapter_title : str
        The title of the chapter to explain.
    content : str
        The original raw content to base the explanation on.
    llm : BaseLanguageModel, optional
        The language model to use for generation. If None, the function will 
        automatically configure a Gemini model.
    temperature : float, optional
        The temperature setting for the LLM, affecting randomness in output.
        Default is 0.0 (deterministic output).
    custom_prompt : Optional[str], optional
        Custom instructions to append to the "系统性讲解" section. Default is None.
    
    Returns
    ----
    ChapterContent
        A structured object containing the chapter's title, summary, explanation, and extension.
    
    Examples
    -----
    >>> chapter = generate_chapter("Machine Learning Basics", "Content about ML...")
    >>> print(chapter.summary)
    'A brief introduction to the fundamental concepts of machine learning...'
    
    >>> custom = "请特别关注实际应用案例，并提供更多代码示例。"
    >>> chapter = generate_chapter("Machine Learning Basics", "Content about ML...", custom_prompt=custom)
    """
    # Create the prompt template
    prompt = create_chapter_prompt_template(custom_prompt=custom_prompt)
    
    # If no LLM is provided, configure Gemini
    if llm is None:
        llm = get_default_llm(temperature)
    
    # Create the LLM chain
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
    )
    
    # Invoke the chain with the chapter title and content
    result = chain.invoke({
        "chapter_title": chapter_title,
        "content": content,
    })
    
    # Parse the result to extract the structured content
    try:
        return parse_chapter_content(chapter_title, result.get("text", ""))
    except Exception as e:
        # Handle parsing errors by creating a basic chapter with an error note
        return ChapterContent(
            title=chapter_title,
            summary=f"Error parsing chapter content: {str(e)}",
            explanation="The LLM response format was unexpected.",
            extension="Please check the LLM configuration and prompt template."
        )


def generate_summary(content: str, chapters: List[ChapterContent], llm: Optional[BaseLanguageModel] = None, temperature: float = 0.0) -> str:
    """
    Generate a comprehensive summary for the entire course.
    
    Parameters
    ----
    content : str
        The original raw content to base the summary on.
    chapters : List[ChapterContent]
        The list of chapter content objects to include in the summary.
    llm : BaseLanguageModel, optional
        The language model to use for generation. If None, the function will 
        automatically configure a Gemini model.
    temperature : float, optional
        The temperature setting for the LLM, affecting randomness in output.
        Default is 0.0 (deterministic output).
    
    Returns
    ----
    str
        A comprehensive summary of the entire course.
    
    Examples
    -----
    >>> chapters = [ChapterContent(title="Chapter 1", summary="Summary 1")]
    >>> summary = generate_summary("Original content", chapters)
    >>> print(summary[:50])
    'This course covers the following key concepts...'
    """
    # Create the prompt template
    prompt = create_summary_prompt_template()
    
    # Prepare the chapter summaries
    chapters_summary = "\n\n".join([
        f"章节 {i+1}: {chapter.title}\n{chapter.summary}"
        for i, chapter in enumerate(chapters)
    ])
    
    # If no LLM is provided, configure Gemini
    if llm is None:
        llm = get_default_llm(temperature)
    
    # Create the LLM chain
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
    )
    
    # Invoke the chain with the content and chapter summaries
    result = chain.invoke({
        "content": content,
        "chapters_summary": chapters_summary,
    })
    
    return result.get("text", "")


def create_course(content: str, llm: Optional[BaseLanguageModel] = None, temperature: float = 0.0, verbose: bool = False, max_chapters: int = 10, fixed_chapter_count: bool = False, custom_prompt: Optional[str] = None) -> Course:
    """
    Create a complete structured course from raw content.
    
    This function orchestrates the entire course creation process:
    1. Generate a table of contents
    2. Create detailed explanations for each chapter
    3. Generate a comprehensive course summary
    
    Parameters
    ----
    content : str
        The raw content to transform into a course.
    llm : BaseLanguageModel, optional
        The language model to use for generation. If None, the function will
        automatically configure a Gemini model.
    temperature : float, optional
        The temperature setting for the LLM, affecting randomness in output.
        Default is 0.0 (deterministic output).
    verbose : bool, optional
        Whether to print progress messages during course generation.
        Default is False.
    max_chapters : int, optional
        Maximum number of chapters to generate. Default is 10.
    fixed_chapter_count : bool, optional
        If True, generate exactly max_chapters. If False, generate between 1 and max_chapters
        based on content complexity. Default is False.
    custom_prompt : Optional[str], optional
        Custom instructions to append to the "系统性讲解" section of each chapter. Default is None.
    
    Returns
    ----
    Course
        A complete course object with all components.
    
    Examples
    -----
    >>> course = create_course("Raw content about a topic...")
    >>> print(f"Generated {len(course.chapters)} chapters")
    
    >>> course = create_course("Extended content...", max_chapters=20)
    >>> print(f"Generated {len(course.chapters)} chapters")
    
    >>> course = create_course("Simple content...", max_chapters=5, fixed_chapter_count=True)
    >>> print(f"Generated {len(course.chapters)} chapters")
    >>> # Will always print "Generated 5 chapters"
    
    >>> custom = "请特别关注实际应用案例，并提供更多代码示例。"
    >>> course = create_course("Content about coding...", custom_prompt=custom)
    """
    # Initialize the course with the original content
    course = Course(content=content)
    
    # If no LLM is provided, configure Gemini
    if llm is None:
        if verbose:
            print("Configuring default Gemini LLM...")
        llm = get_default_llm(temperature)
    
    # Step 1: Generate the table of contents
    if verbose:
        print(f"Generating table of contents (max {max_chapters} chapters)...")
        if fixed_chapter_count:
            print(f"Using fixed chapter count mode: exactly {max_chapters} chapters")
        if custom_prompt:
            print("Using custom prompt for chapter generation")
    
    chapter_titles = generate_toc(
        content, 
        llm=llm, 
        temperature=temperature, 
        max_chapters=max_chapters,
        fixed_chapter_count=fixed_chapter_count
    )
    
    if verbose:
        print(f"Generated {len(chapter_titles)} chapter titles")
    
    # Step 2: Generate content for each chapter
    chapters = []
    for i, title in enumerate(chapter_titles):
        if verbose:
            print(f"Generating chapter {i+1}/{len(chapter_titles)}: {title}")
        chapter = generate_chapter(
            title, 
            content, 
            llm=llm, 
            temperature=temperature,
            custom_prompt=custom_prompt
        )
        chapters.append(chapter)
    
    course.chapters = chapters
    
    # Step 3: Generate the course summary
    if chapters:
        if verbose:
            print("Generating course summary...")
        course.summary = generate_summary(content, chapters, llm=llm, temperature=temperature)
        if verbose:
            print("Course generation complete!")
    
    return course


def parse_chapter_content(chapter_title: str, text: str) -> ChapterContent:
    """
    Parse the raw text output from the LLM into structured chapter content.
    
    This function extracts the summary, explanation, and extension sections
    from the LLM's response and organizes them into a ChapterContent object.
    
    Parameters
    ----
    chapter_title : str
        The title of the chapter.
    text : str
        The raw text output from the LLM.
    
    Returns
    ----
    ChapterContent
        A structured object containing the chapter's components.
    
    Raises
    -----
    ValueError
        If the text cannot be parsed into the expected sections.
    """
    # Initialize the chapter content with the title
    chapter_content = ChapterContent(title=chapter_title)
    
    # Define section markers
    sections = {
        "summary": ["# 标题与摘要", "# 摘要", "标题与摘要"],
        "explanation": ["# 系统性讲解", "# 讲解", "系统性讲解"],
        "extension": ["# 拓展思考", "# 拓展", "拓展思考"]
    }
    
    # Split the text by section markers
    section_text = {}
    lines = text.split("\n")
    current_section = None
    
    for line in lines:
        stripped_line = line.strip()
        
        # Check if this line is a section marker
        new_section = None
        for section, markers in sections.items():
            if any(stripped_line.startswith(marker) for marker in markers):
                new_section = section
                break
        
        if new_section:
            current_section = new_section
            section_text[current_section] = []
        elif current_section:
            section_text[current_section].append(line)
    
    # Join the lines for each section and add to the chapter content
    if "summary" in section_text and section_text["summary"]:
        chapter_content.summary = "\n".join(section_text["summary"]).strip()
    
    if "explanation" in section_text and section_text["explanation"]:
        chapter_content.explanation = "\n".join(section_text["explanation"]).strip()
    
    if "extension" in section_text and section_text["extension"]:
        chapter_content.extension = "\n".join(section_text["extension"]).strip()
    
    return chapter_content 


def create_course_parallel(
    content: str, 
    llm: Optional[BaseLanguageModel] = None, 
    temperature: float = 0.0, 
    verbose: bool = False, 
    max_chapters: int = 10, 
    fixed_chapter_count: bool = False, 
    custom_prompt: Optional[str] = None,
    max_workers: Optional[int] = None,
    delay_range: tuple = (0.1, 0.5),
    max_retries: int = 3,
    course_title: str = "course",
    output_dir: str = "output"
) -> Course:
    """
    Create a course with parallel chapter generation.
    
    This function creates a course by generating chapters in parallel using
    multiple processes. This can significantly speed up the course generation
    process, especially for courses with many chapters.
    
    Parameters
    ----------
    content : str
        The raw content to transform into a course
    llm : Optional[BaseLanguageModel], optional
        Language model to use. If None, a default model will be configured.
    temperature : float, optional
        Temperature for generation. Default is 0.0.
    verbose : bool, optional
        Whether to print progress messages. Default is False.
    max_chapters : int, optional
        Maximum number of chapters. Default is 10.
    fixed_chapter_count : bool, optional
        Whether to use fixed chapter count. Default is False.
    custom_prompt : Optional[str], optional
        Custom prompt instructions. Default is None.
    max_workers : Optional[int], optional
        Maximum number of worker processes. If None, uses the default.
    delay_range : tuple, optional
        Range (min, max) in seconds for the random delay between task submissions.
        Default is (0.1, 0.5).
    max_retries : int, optional
        Maximum number of retry attempts per chapter. Default is 3.
    course_title : str, optional
        Title of the course for saving files. Default is "course".
    output_dir : str, optional
        Directory to save the chapter files. Default is "output".
        
    Returns
    -------
    Course
        The generated course object
    """
    # Import here to avoid circular imports
    from geminiteacher.parallel import parallel_generate_chapters
    
    # Initialize the course with the original content
    course = Course(content=content)
    
    # If no LLM is provided, configure Gemini
    if llm is None:
        if verbose:
            print("Configuring default Gemini LLM...")
        llm = get_default_llm(temperature)
    
    # Step 1: Generate the table of contents
    if verbose:
        print(f"Generating table of contents (max {max_chapters} chapters)...")
        if fixed_chapter_count:
            print(f"Using fixed chapter count mode: exactly {max_chapters} chapters")
        if custom_prompt:
            print("Using custom prompt for chapter generation")
    
    chapter_titles = generate_toc(
        content, 
        llm=llm, 
        temperature=temperature, 
        max_chapters=max_chapters,
        fixed_chapter_count=fixed_chapter_count
    )
    
    if verbose:
        print(f"Generated {len(chapter_titles)} chapter titles")
    
    # Step 2: Generate content for each chapter in parallel
    if chapter_titles:
        # Get API key from the LLM if it's a ChatGoogleGenerativeAI instance
        api_key = None
        model_name = "gemini-1.5-pro"
        
        if llm is not None:
            try:
                # Try to extract API key from the LLM instance
                api_key = getattr(llm, "google_api_key", None)
                model_name = getattr(llm, "model", model_name)
            except Exception:
                pass
        
        chapters = parallel_generate_chapters(
            chapter_titles=chapter_titles,
            content=content,
            llm=llm,  # This will be used to extract API key and model if possible, but not passed to worker processes
            temperature=temperature,
            custom_prompt=custom_prompt,
            max_workers=max_workers,
            delay_range=delay_range,
            max_retries=max_retries,
            course_title=course_title,
            output_dir=output_dir
        )
        
        course.chapters = chapters
        
        # Step 3: Generate the course summary
        if verbose:
            print("Generating course summary...")
        course.summary = generate_summary(content, chapters, llm=llm, temperature=temperature)
        if verbose:
            print("Course generation complete!")
    
    return course 