# -*- coding: utf-8 -*-
# autodoc - automatic documentation for Python code
#
# Copyright (c) 2023 - now
# Max-Planck-Institute of biological Intelligence, Munich, Germany
# Authors: Karl Heggenberger, Joergen Kornfeld

import sys
import argparse
from distutils.util import strtobool
import os
import openai
import yaml
from autodocumentation_python.clone_source import clone_source, copy_py_files, check_path, delete_content_except_one_folder #these are also some helper functions
from autodocumentation_python.summarize_repo import summarize_repo
from autodocumentation_python.create_docstrings import create_docstrings
from autodocumentation_python.insert_docstrings import insert_docstrings
from autodocumentation_python.check_config import check_config
from autodocumentation_python.cost_estimator import cost_estimator
import traceback
#from autodocumentation_python.filename_of_personal_repository_info import name_of_repository_info_function


def main(source_path: str, cost: str, write_gpt_output: bool, max_lno, Model: str, summarize_repository) -> None:
    """
    Orchestrates the process of generating and inserting docstrings into a given repository.
    
    This function performs the following steps:
    1. Clones the source code from the provided URL/path.
    2. Analyzes the repository.
    3. Generates docstrings for each Python file in the repository.
    4. Inserts the generated docstrings back into the respective files.
    5. If enabled, writes the generated docstrings into a separate file.
    
    Args:
        source_path (str): The URL/path of the GitHub repository to be analyzed and documented.
        cost (str, optional): The cost of the GPT model used for docstring generation. Defaults to 'expensive'.
        write_gpt_output (bool, optional): If True, writes the GPT output/docstrings into a separate file. 
            Defaults to True.
        detailed_repo_summary (bool, optional): If True, generates a detailed summary of the repository. 
            Defaults to True.
        max_lno (int, optional): The maximum number of lines to split the code. Defaults to 1200.
        Model (str, optional): The GPT model used for docstring generation. Defaults to 'gpt-4-32k'.
    
    Returns:
        None
    """
    # CHECK INPUT

    # if save_terminal_output:
    #     output_file_path = 'terminal_output.txt'
    #     output_file = open(output_file_path, 'w')
    #     # Save the current standard output and error streams
    #     original_stdout = sys.stdout
    #     original_stderr = sys.stderr
    #     # Redirect standard output and error to the file
    #     sys.stdout = output_file
    #     sys.stderr = output_file

    if max_lno == None:
        if Model == 'gpt-4-32k':
            max_lno = 1200
        elif Model == 'gpt-4':
            max_lno = 300
        elif Model == 'gpt-4-1106-preview':
            max_lno = 700
        else:
            max_lno = 300

    # CLONE SOURCE
    target_dir = os.path.join(os.getcwd(), "edited_repository")
    clone_source(source_path, target_dir)
    path_dest = os.path.join(target_dir, 'gpt_output') #path to the gpt_output folder

    # ESTIMATE COSTS
    detailed_repo_summary = cost_estimator(max_lno = max_lno, target_dir = target_dir, model = Model, cost = cost) #also checks if combinded .md/.rst files are too long for gpt-3.5-16k


    # CHECK CONFIG
    check_config() #and get api_key
    edit_in_file = True if input("Do you want to edit your current files (y) or leaving them untouched and create a new folder called 'edited_repository' including the edited files (n)? (y/n): ") == 'y' else False


    # PRINT PARAMETERS
    print('\n\nParameters:')
    print(f'    Source path: {source_path}')
    print(f'    cost: {cost}')
    print(f'    write gpt output: {write_gpt_output}')
    print(f'    summarize .md & .rst files: {summarize_repository}')
    print(f'    max. snippet length: {max_lno} lines')
    print(f'    Model: {Model}')


    # INFO ABOUT REPOSITORY
    #info_repo = f'info about repository:\n{read_SyConn_info()}'    #if you want to add your own info about the repository: make a file and function which returns a string with the info
                                                                    #and comment out the next code block (try/except) as remove comment in line 21
    try:
        info_repo = summarize_repo(target_dir, summarize_repository, Model='gpt-4-1106-preview', detailed=detailed_repo_summary)
    except Exception:
        info_repo = summarize_repo(target_dir, summarize_repository, Model='gpt-3.5-turbo-16k', detailed=False)


    # CREATE DOCSTRINGS
    print('\nAnalyzing files:')
    for root, dirs , files in os.walk(target_dir):
        if 'gpt_output' in dirs:
            dirs.remove('gpt_output') #exlude gpt_output folder from analysis
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                gpt_path = os.path.join(path_dest, os.path.relpath(file_path, target_dir))

                #in the next line the file is analyzed (if file > man_lno), docstrings are generated and saved in gpt_output (if enabled)
                docstrings = create_docstrings(file_path, additional_info=info_repo, 
                                              max_lno=max_lno, Model=Model, cost=cost,
                                              write_gpt_output=write_gpt_output, gpt_path=gpt_path)

                # inserts docstrings
                try:
                    print('    Compare docstrings to old ones and insert them...')
                    if edit_in_file:
                        #find path to file which is located in the source directory (but the current analyzed file is selected within the source folder/file copied to the folder cwd/edited_repository)
                        dir_source_diff = os.path.relpath(check_path(source_path), start=os.getcwd()) #dirs from cwd to (user specified) target_dir
                        file_diff = os.path.relpath(file_path, start=os.path.join(os.getcwd(),'edited_repository')) #path from edited_repository to analyzed file
                        file_path = os.path.join(os.getcwd(), dir_source_diff, file_diff)
                    insert_docstrings(file_path, docstrings, Model) 
                except Exception as err:
                    print(f'    Error: {err}')
                    traceback.print_exc()
                    print('    Could not insert docstrings.')
                    print('    The file will be skipped.')
                    continue
                
    #also copy info_repo in gpt_output
    if write_gpt_output and info_repo != None:
        dest_path = os.path.join(target_dir, 'gpt_output')
        with open(os.path.join(dest_path, 'info_repo'), "w") as file:
            file.write(info_repo)
    if edit_in_file:
        delete_content_except_one_folder(os.path.join(os.getcwd(), 'edited_repository'), 'gpt_output')



    print('\nFinished!')
    print('You can see your edited repository in the folder "edited_repository" of your current working directory')
    # if save_terminal_output:
    #     # Reset the standard output and error streams
    #     sys.stdout = original_stdout
    #     sys.stderr = original_stderr
    #     # Close the file
    #     output_file.close()
    #     print(f'The terminal output was saved in the file {output_file_path} in the folder "edited_repository" of your cwd')




def execute():
    """
    An helper function to parse the command line arguments and call the main function. This is needed because of pip-packaging.
    """
    parser = argparse.ArgumentParser(description="Process repositories/folder/files and optional variables.")
    
    # Positional argument
    parser.add_argument("source_path", type=str, help="(GitHub_repository_URL/directory_path/file_path)\n  specify the source to be edited with docstrings")
    
    # Optional arguments
    parser.add_argument("--cost", type=str, default='expensive', help="('expensive'/'cheap'); expensive: always uses gpt-4-32k; cheap: uses gpt-3.5-turbo-16k for files < 300 lines and gpt-4-32k for files > 300 lines")
    parser.add_argument("--write_gpt_output", dest='write_gpt_output', type=lambda x: bool(strtobool(x)), default=True, help="(True/False); writes the GPT output/docstrings into a folder 'gpt-output' within the folder eddited repository ")
    parser.add_argument("--max_lno", type=int, help="(int_number); length [in lines] from which a code is split into snippets (max_lno is also approx. the length of the snippets)")
    parser.add_argument("--Model", type=str, default='gpt-4-1106-preview', help="(gpt-4-32k/gpt-4); gpt-model used for docstring generation (if cost = 'expensive' for all files, if cost = 'cheap' only for ones > 300 lines) ")
    parser.add_argument("--summarize_repository", dest='summarize_repository', type=lambda x: bool(strtobool(x)), default=True, help="(True/False); generates a detailed summary of all .md & .rst files of the repository")
    #parser.add_argument("--save_terminal_output", dest='save_terminal_output', type=lambda x: bool(strtobool(x)), default=True, help="(True/False); saves the terminal output in a file 'terminal_output.txt' in the folder 'edited_repository'")

    args = parser.parse_args()
    
    main(
        args.source_path,
        cost=args.cost,
        write_gpt_output=args.write_gpt_output,
        max_lno=args.max_lno,
        Model=args.Model,
        summarize_repository=args.summarize_repository,
        #save_terminal_output=args.save_terminal_output,
    )

if __name__ == "__main__":
    execute()
