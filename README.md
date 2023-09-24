# Automatic Code Documentation Tool

The `autodoc` repository provides a tool for automatically generating detailed Google format docstrings for each function and class in a given Python file. The tool utilizes the GPT (Generative Pre-trained Transformer) API provided by OpenAI to generate the docstrings. It also includes functionality to handle large files by splitting them into smaller snippets and generating docstrings for each snippet separately.
Autodoc differs from other generation tools by not only analyzing the code of the current function/class, but as much code as possible plus additional information about the repository and the code (if file is too large).

:warning: **Warning:** `gpt-4-32k` is currently not available. Therefore the following default values are currently changed:
- `--Model:` before: 'gpt-4-32k'; now: 'gpt-4'
- `--max_lno:` before: 1200; now: 300

## Usage

To use the `autodoc` tool, follow these steps:

1. Clone or download the `autodoc` repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Navigate to the root directory of the `autodoc` repository in your terminal and run `code/main.py some_relative_path` (see [example usage](#example-usage)).

### Command Line Arguments

The `autodoc` tool accepts the following command line arguments:

- `source_path` (required): The URL/path of the GitHub repository or the directory/file to be analyzed and documented.
- `--cost` (optional): The cost of generating the docstrings (further explanation below). Choose between 'expensive' (default) or 'cheap'.
- `--write_gpt_output` (optional): Whether to write the GPT output/docstrings into a folder 'gpt-output' within the 'edited_repository' folder. Choose between True (default) or False.
- `--max_lno` (optional): The maximum number of lines from which a code is split into snippets. Default is 1200.
- `--Model` (optional): The GPT model used for docstring generation. Choose between 'gpt-4-32k' (default) or 'gpt-4'.
- `--detailed_repo_summary` (optional): Whether to generate a detailed (further explanation below) summary of the repository (by summarizing all .md & .rst files). Choose between True (default) or False.

**Further Explanation:**

- `cost:` With `expensive`, all files are always edited with the specified `Model`. With `cheap`, all files with fewer lines than `max_lno` are edited with gpt-3.5-turbo-16k, and only the larger files use the given model (e.g., gpt-4).
- `detailed_repo_summary:` If `True`, then all .md and .rst files are merged at once by gpt. However, if there are many long .md files in the repository, they may have more than 16k tokens in total. Then each .md|.rst file will be summarized separately, and all summaries will be merged again (if set to `False`).

### Example Usage

To generate and insert docstrings into a repository, run the following command:

```
python main.py <relative_source_path> [--cost <cost>] [--write_gpt_output <write_gpt_output>] [--detailed_repo_summary <detailed_repo_summary>] [--max_lno <max_lno>] [--Model <Model>]
```

Replace `<relative_source_path>` with the URL/path of the GitHub repository or the relative path to the directory/file to be documented. You can also provide the optional arguments as needed.

### Example Command

```
python main.py https://github.com/example/repo
```

This command will analyze the repository at the given URL, generate detailed docstrings using the 'gpt-4-32' model, and insert them back into the respective files. It will also write the generated docstrings into a separate file if enabled.

## How the tool works

1. The source is cloned with all files in 'edited_repository'.
2. All `.md` and `.rst` files are summarized (part of additional info).
3. All `.py` files are analyzed/edited individually
   - 3.1 For files with more lines than `max_lno`:
     File regenerated without any code -> string of only redefined classes and functions with arguments and docstrings are saved with correct insertion (part of additional info).
   - 3.2 Code of the file and additional info are given to GPT (task: generate docstrings). The GPT response is stored in the `gpt_output` folder.
   - 3.3 Docstrings are inserted into the code. The code itself is not changed!

## Notice: 

- I have written a small program that roughly estimates the costs. It is based on the calculation explained in this last bullet point. See also the [pricing](https://openai.com/pricing) of openai.

   ```
   python cost_estimator.py <URL or relative_path(folder or file)>
   ```

- If you get errors for individual files, the docstrings were most likely generated anyway, but could not be inserted into the code (formatting problems in the gpt response). Under `edited_repository/gpt_output` should be the file with generated docstrings. For a quick fix you can insert them by hand.

- The analysis of the .md and .rst files (summarize_repo.py) is currently only done with gpt-3.5-turbo-16k. (The model can be changed in main.py in line 54)

- The larger the maximum input to the model, the more code can be processed at once. As a result, GPT understands the code better and can generate more accurate docstrings. For optimal docstrings it is therefore recommended to select the largest possible model (gpt-4-32k) and to set the maximum code length (max_lno) as high as possible(~1500). <br>
max_lno can be roughly estimated: <br>
   max_lno = (max_model_tokens - info_repo_tokens - info_code_tokens) : 20 <br>
   One token is roughly 4 characters and 0.75 English words. One line of code has roughly 20 tokens. <br>
   If calculated very generously: Info_repo = (2000 tokens|1500 words), info_code = (4000 tokens|3000 words) and we use gpt-4-32k then <br>
   max_lno = (32k - 2k - 4k) : 20 = 1300 [lines].

## Repository Files

The `autodoc` repository contains the following files:

- `gpt_output.py`: Contains the `show_gpt_output` function, which writes the generated docstrings to a file in the specified directory.
- `main.py`: The main script that orchestrates the entire process of generating and inserting docstrings into a given repository.
- `create_docstrings.py`: Contains the `create_docstrings` function, which generates detailed Google format docstrings for each function and class in a given Python file.
- `gptapi.py`: Contains the `gptapi` function, which generates a GPT output for the given code and command using the OpenAI API.
- `make_snippets.py`: Contains the `make_snippets` function, which generates code snippets from a file based on the maximum number of lines.
- `summarize_repo.py`: Contains the `summarize_repo` function, which analyzes a repository and generates a summary using the gptAPI.
- `clone_source.py`: Contains the `clone_source` function, which clones or copies the source code to the target directory.
- `insert_docstrings.py`: Contains the `insert_docstrings` function, which inserts docstrings into a Python file at the appropriate locations.
- `summarize_file.py`: Contains the `gen_shifted_docstring` and `node_info` functions, which extract the definition and docstring of a class or function from an abstract syntax tree node.
- `README.md`: The README file for the `autodoc` repository.

Please refer to the individual files for more detailed information about their functionality and implementation.

## Bugs

If any errors occur, feel free to write me a message. I will try to fix the problem as soon as I can.
