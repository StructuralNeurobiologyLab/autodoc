import os
import openai
import yaml
from clone_source import clone_source
from analyze_repo import analyze_repo
from create_docstrings import create_docstrings
from insert_docstrings import insert_docstrings
from gpt_output import show_gpt_output


with open("code/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
openai.api_key = config["api_key"]

def main(source_path: str) -> None:
    """
    The main function that orchestrates the entire process of generating and inserting docstrings into a 
    given repository. It performs the following steps:
    1. Clones the source code from the provided URL/path.
    2. Analyzes the repository.
    3. Generates docstrings for each Python file in the repository.
    4. Inserts the generated docstrings back into the respective files.
    5. If enabled, writes the generated docstrings into a separate file.
    
    Args:
        source_path (str): The URL/path of the GitHub repository to be analyzed and documented.
    
    Returns:
        None
    """

    # PARAMETERS
    Model = 'gpt-4'  #"gpt-4-32k", "gpt-4", "gpt-3.5-turbo-16k" or 'gpt-3.5-turbo'
    max_lno = 300  # max number of lines, when a file is split into snippets (for gpt)
    cost = 'cheap'  #'cheap' or 'expensive'  # docstring generation for files < max_lno either via gpt-3.5-turbo(cheap) or gpt-4(expensive))
    write_gpt_output = True  #False or True  # write the gpt output into a file
    detailed = False  #False or True    #analysis of the repository: summarize all .md|.rst files
                                        #if True, all .md|.rst files are combined into a single string and fed into the gptAPI (may be too long for gpt)
                                        #if False, each .md|.rst file is summarized individually and the summaries are combined into a final summary

    print('Parameters:')
    print(f'    Model: {Model})    max. snippet length: {max_lno} lines\n    cost: {cost}\n    write gpt output: {write_gpt_output}\n')
    print(f'    max. snippet length: {max_lno} lines')
    print(f'    write gpt output: {write_gpt_output}')
    print(f'    cost: {cost}')
    print(f'    detailed analysis/summary of repository: {detailed}')


    # CLONE SOURCE
    target_dir = os.path.join(os.getcwd(), "edited_repository")
    clone_source(source_path, target_dir)  # returns 'file' if input is a file

    # INFO ABOUT REPOSITORY
    info_repo = 'info about repository:\n' + analyze_repo(target_dir, Model='gpt-3.5-turbo-16k', detailed=detailed) + '\n'
    # print(info_repo)

    # CREATE DOCSTRINGS
    print('Analyzing files and waiting for a gpt response:')
    for root, _ , files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # in the next line the file is analyzed (if file > man_lno) and the docstrings are generated
                docstrings = create_docstrings(file_path, additional_info=info_repo, max_lno=max_lno, Model=Model, cost=cost)

                # Write docstrings(/gpt-output) into a file (if enabled)
                if write_gpt_output:
                    show_gpt_output(target_dir=target_dir, file=file, docstrings=docstrings)

                insert_docstrings(file_path, docstrings)  # inserts only the docstrings into the file

    print('\nFinished!')
    print('You can see your edited repository in the folder "edited_repository" of your current working directory')


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python main.py <github_repository_url>")
        sys.exit(1)
    main(sys.argv[1])
