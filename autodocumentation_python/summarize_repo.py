# -*- coding: utf-8 -*-
# autodoc - automatic documentation for Python code
#
# Copyright (c) 2023 - now
# Max-Planck-Institute of biological Intelligence, Munich, Germany
# Authors: Karl Heggenberger, Joergen Kornfeld

import openai
import os

def summarize_repo(file_path: str, summarize_repository, Model: str = 'gpt-3.5-turbo-16k', detailed: bool = True) -> str:
    """
    Analyzes a repository and generates a summary using the GPT API.
    
    This function takes in the path of a repository, a model, and a boolean indicating whether a detailed 
    analysis is required. It reads all .md and .rst files in the repository, feeds them into the GPT API, 
    and generates a summary. If the detailed flag is set to True, all files are combined into a single 
    string and fed into the GPT API. If the detailed flag is set to False, each file is summarized 
    individually and the summaries are combined into a final summary.
    
    Args:
        file_path (str): The path of the repository to be analyzed.
        Model (str): The model to be used by the GPT API for generating the summary.
        detailed (bool, optional): A flag indicating whether a detailed analysis is required. 
                                   Defaults to True.
    
    Returns:
        str: The generated summary of the repository. If no additional information about the environment 
             in which the file is embedded is found, None is returned.
    """
    if not summarize_repository:
        return None
    print('\nSummarizing repository using .rst and .md files ...')
    if detailed:
        all_content = []
        for root, _, files in os.walk(file_path):
            for file in files:
                if file.endswith((".md", ".rst")):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as file:
                        content = file.read()
                    all_content.append(content)
        all_content = "\n\n".join(all_content)

        if all_content == "":
            print('    No additional info about the environment in which the file is embedded.')
            return None

        command = """
Generate a very detailed summary for this repository given its documentation. 
Focus especially on details in the methodologies.
It is later used to provide additional information when analyzing the repository`s code to 
generate docstrings using the gptAPI. 
The summary should not be longer than 1000 tokens or 750 words.
Just output the summary.
"""
        response = openai.ChatCompletion.create(
            model=Model,
            messages=[
                {"role": "user", "content": command},
                {"role": "user", "content": all_content},
            ],
            temperature=0.4,
        )
        summary = response['choices'][0]['message']['content']
        output = f'info about repository:\n{summary}'

        return output
    

    if not detailed:
        summary = []
        for root, _, files in os.walk(file_path):
            for file in files:
                if file.endswith((".md", ".rst")):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as file:
                        content = file.read()
                    
                    command = """Generate a detailed summary for this file. Just output the summary."""
                    response = openai.ChatCompletion.create(
                        model=Model,
                        messages=[
                            {"role": "user", "content": command},
                            {"role": "user", "content": content},
                        ],
                        temperature=0.4,
                    )
                    answer = response['choices'][0]['message']['content']
                    summary.append(answer)

        summary = "\n\n".join(summary)

        if summary == "":
            print('    No additional info about the environment in which the file is embedded.')
            return None
        
        command = """
Generate a detailed summary for this repository. It is later used 
to provide additional information when analyzing the code to 
generate docstrings using the gptAPI.
Just output the summary.
"""
        response = openai.ChatCompletion.create(
            model=Model,
            messages=[
                {"role": "user", "content": command},
                {"role": "user", "content": summary},
            ],
            temperature=0.4,
        )
        final_answer = response['choices'][0]['message']['content']
        output = f'info about repository:\n{final_answer}'

        return output
