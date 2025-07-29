FILE_TEMPLATE = """
Using the following file data enclosed within the <<< >>> delimeters write a \
top-file level concise summary that effectively captures the overall purpose and \
functionality of the file.

file data: <<< {data} >>>

Ensure your final summary is no longer than three sentences.
"""


ROOT_LEVEL_TEMPLATE = """
Generate a markdown text using the enclosed \
information within the <<< >>> delimiters as your context. \
Your output must strictly adhere to the provided structure below \
without adding any other section not mentioned on it.

This is the structure your output must have:
Structure:
----------
# <<<repository_name>>> (Please ensure that the initial letter \
is capitalized)

## Description
(Provide a concise one-line sentence that describes the primary \
purpose of the code, utilizing all the contextual details \
available.)

## Overview
(In this section, your task is to create a single, well-structured \
five-lines paragraph that concisely communicates the reasons behind the \
repository's creation, its objectives, and the mechanics underlying \
its functionality.)
----------

Repository data: <<< {data} >>>

Ensure proper formatting and adhere to Markdown syntax guidelines.
Do not add sections that are not listed in the provided structure.
"""

FOLDER_SHORT_DESCRIPTION_TEMPLATE = """
Generate a one-line description of the folder's purpose based on \
the summaries of the files contained in the folder enclosed within the <<< >>> delimiters

File summaries: <<< {data} >>>
"""


SYSTEM_PROMPT = """
You are an advanced code analyzer and documenting system. \
Your job is to generate summaries from code files written in various languages, \
and then, using those summaries, create top-level summaries for folders and the full project. \
Be concise, and focus on the intent of the code, not particularities. \
Your output should be used/read by a human to understand the basic structure \
and goal of each file and folder in a software project, \
and understand what the project does at a high level view
"""
