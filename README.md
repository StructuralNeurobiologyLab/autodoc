# Automatic Code Documentation Tool

This repository provides a tool for automatically generating detailed Google format docstrings for each function and class in a given Python file. The tool utilizes the GPT (Generative Pre-trained Transformer) API provided by OpenAI to generate the docstrings. It also includes functionality to handle large files by splitting them into smaller snippets and generating docstrings for each snippet separately.

## How to Use

To use this tool, follow the steps below:

1. Clone or download this repository to your local machine.

2. Install the required dependencies by running the following command:

   ```
   pip install -r requirements.txt
   ```

3. Create a `config.yaml` file in the root directory of the repository and add your OpenAI API key to it. The `config.yaml` file should have the following format:

   ```yaml
   api_key: "YOUR_API_KEY"
   ```

4. Open the `main.py` file and modify the `source_path` variable to specify the URL or path of the Python repository you want to analyze and document.

5. Customize the parameters in the `main` function according to your needs. The available parameters are:

   - `Model`: The GPT model to use for generating the docstrings. You can choose from "gpt-4-32k", "gpt-4", "gpt-3.5-turbo-16k", or "gpt-3.5-turbo". gpt-3.5-turbo and gpt-3.5-turbo-16k can only be used if all codes are shorter than max_lno (do not have to be split into snippets). For Codes larger than 250 lines we recommend to use gpt-4-32k. The default value is "gpt-4".

   - `max_lno`: The maximum number of lines that the tool can handle in a single file. If a file is larger than this, it will be split into smaller snippets. To adjust this parameter read the [second bullet point](#notice) .The default value is 400.

   - `cost`: The cost of generating the docstrings if the file is not split into snippets. You can choose between "cheap" and "expensive". "cheap" will use the "gpt-3.5-turbo" model and the output will be the whole file (code + docstrings). "expensive" will use the "gpt-4" model and the output will be only the docstrings. The default value is "expensive".

   - `write_gpt_output`: Whether to write the generated docstrings into separate files. Set this to `True` if you want to save the docstrings in a separate file for each Python file in the repository. The default value is `True`.

   - `detailed`: whether .md and .rst files are combined and then summarized (True) or summarized individually, then merged and summarized again (False). You can choose between "True" and "False". The default value is "True".

6. Run the `main.py` file using the following command (if current cwd is autodoc):

   ```
   python code/main.py <URL or path(folder or file)>
   ```

   The tool will clone the source code from the specified repository, analyze the repository, generate docstrings for each Python file, insert the docstrings back into the respective files, and optionally write the generated docstrings into separate files.

7. After the tool finishes running, you can find the edited repository in the "edited_repository" folder of your current working directory. The Python files in the repository will now have detailed Google format docstrings inserted.

## Notice: 

- The analysis of the .md and .rst files (summarize_repo.py) is currently only done with gpt-3.5-turbo-16k. (The model can be changed in main.py in line 54)

- The larger the maximum input to the model, the more code can be processed at once. As a result, GPT understands the code better and can generate more accurate docstrings. For optimal docstrings it is therefore recommended to select the largest possible model (gpt-4-32k) and to set the maximum code length (max_lno) as high as possible(~1500). <br>
max_lno can be roughly estimated: <br>
   max_lno = (max_model_tokens - info_repo_tokens - info_code_tokens) : 20 <br>
   One token is roughly 4 characters and 0.75 English words. One line of code has roughly 20 tokens. <br>
   If calculated very generously: Info_repo = (2000 tokens|1500 words), info_code = (4000 tokens|3000 words) and we use gpt-4-32k then <br>
   max_lno = (32k - 2k - 4k) : 20 = 1300 [lines].

- The costs can also be estimated using the above estimates. See also the [pricing](https://openai.com/pricing) of openai.

## Repository Structure

The repository contains the following files:

- `create_docstrings.py`: This file contains the main function `create_docstrings` that generates detailed Google format docstrings for a given Python file.

- `config.yaml`: This file stores the OpenAI API key.

- `make_snippets.py`: This file contains the function `make_snippets` that generates code snippets from a file based on the maximum number of lines.

- `gptapi.py`: This file contains the function `gptapi` that generates a GPT output for the given code and command using the OpenAI API.

- `requirements.txt`: This file lists the required dependencies for running the tool.

- `main.py`: This file contains the main function `main` that orchestrates the entire process of generating and inserting docstrings into a given repository.

- `clone_source.py`: This file contains the function `clone_source` that clones or copies the source code to the target directory.

- `summarize_repo.py`: This file contains the function `summarize_repo` that analyzes a repository and generates a summary using the GPT API.

- `gpt_output.py`: This file contains the function `show_gpt_output` that writes the generated docstrings to a file in the specified directory.

- `summarize_file.py`: This file contains the functions `node_info` and `code_info` that extract the class and function definitions from a Python file.

- `insert_docstrings.py`: This file contains the functions `shift_docstring`, `remove_start_end_lines`, and `insert_docstrings` that insert docstrings into a Python file at the appropriate locations.


## Conclusion

This tool provides a convenient way to automatically generate detailed Google format docstrings for each function and class in a Python repository. By utilizing the GPT API, it can generate accurate and context-aware docstrings that can improve code documentation and readability.