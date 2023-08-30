import os
import re
import sys
import shutil
import subprocess

def count_lines(file_path):
    with open(file_path, "r") as file:
        return sum(1 for line in file if line.strip() != "")

def count_words(file_path):
    with open(file_path, "r") as file:
        content = file.read()
        words = re.findall(r'\w+', content)
        return len(words)

def count_code_and_words(directory, max_lno):
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <repository_url>")
        sys.exit(1)
    
    repository_url = sys.argv[1]
    target_directory = "temp_repo"
    max_lno = 300
    
    # Clone the repository
    subprocess.run(["git", "clone", repository_url, target_directory])
    
    total_lines, total_words, num_files_above_max, lines_above_max = count_code_and_words(target_directory, max_lno)
    
    # Clean up the cloned repository
    shutil.rmtree(target_directory)
    
    cost_gpt_4_32k= (total_lines * 20 * 0.06 + total_words * 1.25 * 0.004) / 1000  #currently for gpt-4 == 0.06$/1000 tokens... gpt-4-32k currently not available
    cost_gpt_3_5_16k = ((((total_lines - lines_above_max)*20*2) + (total_words *1.25)) * 0.004 + (lines_above_max * 20) * 0.06) / 1000
    
    print(f"Total lines of code: {total_lines} -> {total_lines * 20} tokens")
    print(f"Total words in .rst and .md files: {total_words} -> {total_words * 1.25} tokens (< 16k tokens!!! else detailed == False)")
    print(f"Number of files with more than {max_lno} lines: {num_files_above_max}")
    print(f"Total lines in files above {max_lno} lines: {lines_above_max} -> {lines_above_max * 20} tokens (with gpt4)")
    print(f"Estimated cost with gpt-4: {cost_gpt_4_32k:.2f}$")
    print(f"Estimated cost with gpt-3.5-16k: {cost_gpt_3_5_16k:.2f}$")
    print('Keep in mind: these are just estimates!')
