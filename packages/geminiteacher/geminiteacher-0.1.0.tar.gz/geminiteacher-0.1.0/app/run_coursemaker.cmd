@echo off
REM Standard sequential processing
REM uv run generate_course.py Machine_Learning.docx --title "machine_learning" --verbose --max-chapters 80 --custom-prompt custom_instructions.txt

REM Parallel processing with 4 workers and custom delay settings
uv run generate_course.py input/xianxingdaishu.md --title "xianxingdaishu" --verbose --max-chapters 100 --custom-prompt input/xianxingdaishu_prompt.txt --parallel --max-workers 14 --min-delay 0.2 --max-delay 1.0 --max-retries 3