# Automatic Code Documentation Tool

The `autodocumentation_python` (`autodoc`) package provides a tool for automatically generating detailed Google format docstrings for each function and class in a given Python file. The tool utilizes the GPT (Generative Pre-trained Transformer) API provided by OpenAI to generate the docstrings. It also includes functionality to handle large files by splitting them into smaller snippets and generating docstrings for each snippet separately.
Autodoc differs from other generation tools by not only analyzing the code of the current function/class, but as much code as possible plus additional information about the repository and the code (if file is too large). This provides much more context for the docstring generation - and it works!

:warning: **Warning:** `gpt-4-32k` is currently not available.

## Usage

To use the `autodoc` tool, follow these steps:

1. Install `autodocumentation_python` using pip
```
pip install autodocumentation_python
```
2. Run the package using `autodoc` and the `path_to_analyze` - URL of repository or path of folder|file you want to analyze (see [example usage](#example-usage)).
```
autodoc path|URL_to_anlyze
```

### Example Usage

To generate and insert docstrings into a repository, run the following command:

```
autodoc <source_path> [--cost <cost>] [--write_gpt_output <write_gpt_output>] [--detailed_repo_summary <detailed_repo_summary>] [--max_lno <max_lno>] [--Model <Model>]
```

Replace `<source_path>` with the URL of the GitHub repository or the relative/absolute path to the directory/file to be documented. You can also provide the optional arguments as needed.

### Example Command

```
autodoc https://github.com/example/repo
```

This command will analyze the repository at the given URL, generate detailed docstrings using the 'gpt-4-32' model, and insert them back into the respective files. It will also write the generated docstrings into a separate file if enabled.

## How the tool works

1. The source is cloned with all files in 'edited_repository'. (If you have large data files, you might create a new folder containing only .py, .md and .rst files)
2. The price of editing the specified source_path is estimated ()
3. All `.md` and `.rst` files are summarized (part of additional info).
4. All `.py` files are analyzed/edited individually
   - 4.1 For files with more lines than `max_lno`:
     File regenerated without any code -> string of only redefined classes and functions with arguments and docstrings are saved with correct insertion (part of additional info).
   - 4.2 Code of the file and additional info are given to GPT (task: generate docstrings). The GPT response is stored in the `gpt_output` folder.
   - 4.3 Each generated docstring is compared to its old one (if present) to ensure no loss of information. Then the new docstring is inserted into the code. The code itself is not changed!

### Command Line Arguments

The `autodoc` tool accepts the following command line arguments:

- `source_path` (required): The URL/path of the GitHub repository or the directory/file (relative or absolute path) to be analyzed and documented.
- `--cost` (optional): With `expensive`, all files are always edited with the specified `Model`. With `cheap`, all files with fewer lines than `max_lno` are edited with gpt-3.5-turbo-16k, and only the larger files use the given model (e.g., gpt-4).
- `--Model` (optional): The GPT model used for docstring generation. Choose between 'gpt-4-32k', 'gpt-4' or 'gpt-4-1106-preview'(gpt-4-turbo)(default).
- `--write_gpt_output` (optional): Whether to write the GPT output/docstrings into a folder 'gpt-output' within the 'edited_repository' folder. Choose between True (default) or False.
- `--max_lno` (optional): The maximum number of lines from which a code is split into snippets. It is not necessary to specify this number, since we have default values based on your input of `Model`

## Notice: 

- If you get errors for individual files, the docstrings were most likely generated anyway, but could not be inserted into the code (formatting problems in the gpt response). Under `edited_repository/gpt_output` should be the file with generated docstrings. For a quick fix you can insert them by hand.<br>
<br>
If a class is longer than max_lno (e.g 700), functions outside or below this range (below start line of the class + 700) are not inserted in the gpt_output! This means that docstrings of these functions cannot be inserted. Solution: Clone this repository run `main` again and indent the affected functions in the gpt_output folder by hand and include the lowest part of the file `insert_docstrings` and run the file insert_docstrings: 
```
python3 -m autodocumentation_python.insert_docstrings
```
or write me a message.

- The analysis of the .md and .rst files (summarize_repo.py) is currently done with `gpt-4-1106-preview`.

- The larger the maximum input to the model, the more code can be processed at once. As a result, (we think!) GPT understands the code better and can generate more accurate docstrings. For optimal docstrings it is therefore recommended to select the largest possible model (gpt-4-32k) and to set the maximum code length (max_lno) as high as possible(~1500). <br>
max_lno can be roughly estimated: <br>
   One token is roughly 4 characters and 0.75 English words. One line of code has roughly 20 tokens. <br>
   max_lno = (max_model_tokens - info_repo_tokens - info_code_tokens) : 20 <br>
   If calculated very generously: Info_repo = (2000 tokens|1500 words), info_code = (4000 tokens|3000 words) and we use gpt-4-32k then <br>
   max_lno = (32k - 2k - 4k) : 20 = 1300 [lines].

## Repository Files

The `autodoc` repository contains the following files:
- `check_config.py`: Checks if config.py present in the home directory and adds one containing the users openAI key.
- `cost_estimator.py`: Contains the `cost_estimator` function, which estimates the cost for every combination of `Model` and `cost` value
- `main.py`: The main script that orchestrates the entire process of generating and inserting docstrings into a given repository.
- `create_docstrings.py`: Contains the `create_docstrings` function, which generates detailed Google format docstrings for each function and class in a given Python file.
- `gptapi.py`: Contains the `gptapi` function, which generates a GPT output for the given code and command using the OpenAI API.
- `make_snippets.py`: Contains the `make_snippets` function, which generates code snippets from a file based on the maximum number of lines.
- `summarize_repo.py`: Contains the `summarize_repo` function, which analyzes a repository and generates a summary using the gptAPI.
- `clone_source.py`: Contains the `clone_source` function, which clones or copies the source code to the target directory.
- `insert_docstrings.py`: Contains the `insert_docstrings` function, which inserts docstrings into a Python file at the appropriate locations after comparing them to the corresponding old docstring.
- `summarize_file.py`: Contains the `gen_shifted_docstring` and `node_info` functions, which extract the definition and docstring of a class or function from an abstract syntax tree node.
- `README.md`: The README file for the `autodoc` repository.

Please refer to the individual files for more detailed information about their functionality and implementation.

## Bugs

If any errors occur, feel free to write me a message on LinkedIn. I will try to fix the problem as soon as I can.
