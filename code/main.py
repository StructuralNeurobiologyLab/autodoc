import argparse
from distutils.util import strtobool
import os
import openai
import yaml
from clone_source import clone_source
from summarize_repo import summarize_repo
from create_docstrings import create_docstrings
from insert_docstrings import insert_docstrings
from gpt_output import show_gpt_output


with open("code/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
openai.api_key = config["api_key"]


def main(source_path: str, cost: str = 'expensive', write_gpt_output: bool = True, detailed_repo_summary: bool = True, max_lno: int = 1200, Model: str = 'gpt-4-32k') -> None:
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
    # PRINT PARAMETERS
    print('Parameters:')
    print(f'    Source path: {source_path}')
    print(f'    cost: {cost}')
    print(f'    write gpt output: {write_gpt_output}')
    print(f'    detailed analysis/summary of repository: {detailed_repo_summary}')
    print(f'    max. snippet length: {max_lno} lines')
    print(f'    Model: {Model}')


    # CLONE SOURCE
    target_dir = os.path.join(os.getcwd(), "edited_repository")
    clone_source(source_path, target_dir)  # returns 'file' if input is a file

    # INFO ABOUT REPOSITORY
    info_repo = summarize_repo(target_dir, Model='gpt-3.5-turbo-16k', detailed=detailed_repo_summary) + '\n'

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

                try:
                    insert_docstrings(file_path, docstrings)  # inserts only the docstrings into the file
                except Exception as err:
                    print(f'    Error: {err}')
                    print('    Could not insert docstrings.')
                    print('    The file will be skipped.')
                    continue
                
    if write_gpt_output:
        dest_path = os.path.join(target_dir, 'gpt_output')
        with open(os.path.join(dest_path, 'info_repo'), "w") as file:
            file.write(info_repo)


    print('\nFinished!')
    print('You can see your edited repository in the folder "edited_repository" of your current working directory')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repositories/folder/files and optional variables.")
    
    # Positional argument
    parser.add_argument("source_path", type=str, help="(GitHub_repository_URL/directory_path/file_path)\n  specify the source to be edited with docstrings")
    
    # Optional arguments
    parser.add_argument("--cost", type=str, default='expensive', help="('expensive'/'cheap'); expensive: always uses gpt-4-32k; cheap: uses gpt-3.5-turbo-16k for files < 300 lines and gpt-4-32k for files > 300 lines")
    parser.add_argument("--write_gpt_output", dest='write_gpt_output', type=lambda x: bool(strtobool(x)), default=True, help="(True/False); writes the GPT output/docstrings into a folder 'gpt-output' within the folder eddited repository ")
    parser.add_argument("--detailed_repo_summary", dest='detailed_repo_summary', type=lambda x: bool(strtobool(x)), default=True, help="(True/False); True: all .md|.rst files are combined into a single string and fed into the gptAPI (may be too long for gpt -> False); False: each .md|.rst file is summarized individually and the summaries are combined into a final summary")
    parser.add_argument("--max_lno", type=int, default=1200, help="(int_number); length [in lines] from which a code is split into snippets (max_lno is also approx. the length of the snippets)")
    parser.add_argument("--Model", type=str, default='gpt-4-32', help="(gpt-4-32k/gpt-4); gpt-model used for docstring generation (if cost = 'expensive' for all files, if cost = 'cheap' only for ones > 300 lines) ")

    args = parser.parse_args()
    
    main(
        args.source_path,
        cost=args.cost,
        write_gpt_output=args.write_gpt_output,
        detailed_repo_summary=args.detailed_repo_summary,
        max_lno=args.max_lno,
        Model=args.Model
    )
