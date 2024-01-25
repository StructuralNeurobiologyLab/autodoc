# -*- coding: utf-8 -*-
# autodoc - automatic documentation for Python code
#
# Copyright (c) 2023 - now
# Max-Planck-Institute of biological Intelligence, Munich, Germany
# Authors: Karl Heggenberger, Joergen Kornfeld

import os
import re
import sys
import shutil
import subprocess

def count_lines(file_path):
    """
    Counts the number of non-empty lines in a file.
    
    Args:
        file_path (str): The path to the file.
        
    Returns:
        int: The number of non-empty lines in the file.
    """
    with open(file_path, "r") as file:
        return sum(1 for line in file if line.strip() != "")

def count_words(file_path):
    """
    Counts the number of words in a file. A word is defined as a sequence of alphanumeric characters.
    
    Args:
        file_path (str): The path to the file.
        
    Returns:
        int: The number of words in the file.
    """
    with open(file_path, "r") as file:
        content = file.read()
        words = re.findall(r'\w+', content)
        return len(words)

def count_code_and_words(directory, max_lno):
    """
    Counts the total lines of code and words in all Python, .rst, and .md files in a directory.
    Also counts the number of files with lines of code above a maximum limit and the total lines in these files.
    
    Args:
        directory (str): The path to the directory.
        max_lno (int): The maximum limit for lines of code in a file.
        
    Returns:
        tuple: The total lines of code, total words, number of files with lines of code above max_lno, 
               and total lines in these files.
    """
    total_lines = 0
    total_words = 0
    num_files_above_max = 0
    lines_above_max = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py"):
                lines = count_lines(file_path)
                total_lines += lines
                if lines > max_lno:
                    num_files_above_max += 1
                    lines_above_max += lines
            elif file.endswith((".rst", ".md")):
                total_words += count_words(file_path)
    
    return total_lines, total_words, num_files_above_max, lines_above_max

def cost_estimator(max_lno: int, target_dir: str, model, cost):
    # print(f"Total lines of code: {total_lines} -> {total_lines * 20} tokens")
    # print(f"Total words in .rst and .md files: {total_words} -> {total_words * 1.25} tokens (< 16k tokens!!! else detailed == False)")
    # print(f"Number of files with more than {max_lno} lines: {num_files_above_max}")
    # print(f"Total lines in files above {max_lno} lines: {lines_above_max} -> {lines_above_max * 20} tokens (with gpt4)")
    
    total_lines, total_words, num_files_above_max, lines_above_max = count_code_and_words(target_dir, 300)
    expensive_gpt4_32k = (total_lines * 20 * 0.12 + total_words * 1.25 * 0.004) / 1000
    cheap_gpt4_32k = ((((total_lines - lines_above_max)*20*2) + (total_words *1.25)) * 0.004 + (lines_above_max * 20) * 0.12) / 1000
    expensive_gpt4= (total_lines * 20 * 0.06 + total_words * 1.25 * 0.004) / 1000
    cheap_gpt4 = ((((total_lines - lines_above_max)*20*2) + (total_words *1.25)) * 0.004 + (lines_above_max * 20) * 0.06) / 1000

#a file with 3597 lines has 36455 tokens, a file summary of 14321 tokens and produces an gpt output of 12016 tokens -> input 36455+14321 = 50776 tokens; output 12016 tokens
                                                                                                                    #input 14.116 tokens per line; output 3.34 tokens per line
    #comparison of docstrings: 14321+12016 = 26337 -> 26337/3597 = 7.32 tokens per line for comparison input and 12016/3597 = 3.34 tokens per line for comparison output
    expensive_gpt_4_1106_preview = (((total_lines * (14.116+7.32) + total_words * 1.25) * 0.01 + (total_lines) *2* 3.34 * 0.03)/ 1000)*2    #*2 because the price actually seems to be like this

    print('To estimate the costs, we assume that one line of code corresponds to 20 tokens.')
    print(f'Estimated costs with settings...')
    print(f"    --cost 'expensive' --Model 'gpt-4-1106-preview':        {expensive_gpt_4_1106_preview:.2f}$")
    print(f"    --cost 'expensive' --Model 'gpt-4':                     {expensive_gpt4:.2f}$")
    print(f"    --cost 'expensive' --Model 'gpt-4-32k':                 {expensive_gpt4_32k:.2f}$")
    print(f"    --cost 'cheap' --Model 'gpt-4':                         {cheap_gpt4:.2f}$")
    print(f"    --cost 'cheap' --Model 'gpt-4-32k':                     {cheap_gpt4_32k:.2f}$")
    print('Keep in mind: these are just rough estimates!!!\n')

    if cost == 'expensive' and model == 'gpt-4':
        print(f'Your are going to spent about {expensive_gpt4:.2f}$')
    elif cost == 'expensive' and model == 'gpt-4-32k':
        print(f'Your are going to spent about {expensive_gpt4_32k:.2f}$')
    elif cost == 'cheap' and model == 'gpt-4':
        print(f'Your are going to spent about {cheap_gpt4:.2f}$')
    elif cost == 'cheap' and model == 'gpt-4-32k':
        print(f'Your are going to spent about {cheap_gpt4_32k:.2f}$')
    elif cost == 'expensive' and model == 'gpt-4-1106-preview':
        print(f'Your are going to spent about {expensive_gpt_4_1106_preview:.2f}$')
    else:
        print('You have chooses a combination of setting I havent calculated the price for (probably cheap and gpt-4-1106-preview).')

    confirmation = input("\nDo you want to continue with the program? (yes[y]/no[n]): ")

    if confirmation.lower() not in ("yes", 'y'):
        shutil.rmtree(target_dir) # Clean up the cloned repository
        print("Program terminated.")
        sys.exit(0)


    if total_words * 1.25 < 120000:
        detailed_repo_summary = True
    else:
        detailed_repo_summary = False

    return detailed_repo_summary
