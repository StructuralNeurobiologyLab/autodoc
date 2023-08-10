import ast
import openai
import os

def analyze_repo(file_path: str, Model: str, detailed: bool = False) -> str:
    """
    Analyzes a repository and generates a summary using the gptAPI.
    
    This function takes in the path of a repository, a model, and a boolean indicating whether a detailed 
    analysis is required. It reads all .md and .rst files in the repository, feeds them into the gptAPI, 
    and generates a summary. If the detailed flag is set to True, all files are combined into a single 
    string and fed into the gptAPI. If the detailed flag is set to False, each file is summarized 
    individually and the summaries are combined into a final summary.
    
    Args:
        file_path (str): The path of the repository to be analyzed.
        Model (str): The model to be used by the gptAPI for generating the summary.
        detailed (bool, optional): A flag indicating whether a detailed analysis is required. 
                                   Defaults to False.
    
    Returns:
        str: The generated summary of the repository.
    """
    print('Summarizing repository using .rst and .md files ...')
    if detailed:
        all_content = []
        for root, subdir, files in os.walk(file_path):
            for file in files:
                if file.endswith((".md", ".rst")):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as file:
                        content = file.read()
                    all_content.append(content)
        all_content = "\n\n".join(all_content)

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
                {"role": "user", "content": all_content},
            ],
            temperature=0.4,
        )
        summary = response['choices'][0]['message']['content']

        return summary
    

    if not detailed:
        summary = []
        for root, subdir, files in os.walk(file_path):
            for file in files:
                if file.endswith((".md", ".rst")):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as file:
                        content = file.read()
                    
                    command = """
                    Generate a detailed summary for this file. Just output the summary.
                    """
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

        return final_answer
