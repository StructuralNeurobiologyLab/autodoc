import warnings
from gptapi import gptapi
from summarize_file import code_info, node_info
from make_snippets import make_snippets


def create_docstrings(file_path: str, additional_info: str = None, max_lno: int = 300, Model: str = "gpt-4-32k", 
                 cost: str = 'cheap'):
    """
    Generates detailed Google format docstrings for each function and class in a given Python file using the gptapi. 
    Handles large files by splitting them into smaller snippets and generating docstrings for each snippet separately. 
    
    Args:
        file_path (str): Path to the Python file for which to generate docstrings.
        additional_info (str, optional): Additional information about the repository that the code is embedded in. 
                                          This can help in generating more accurate docstrings. Defaults to None.
        max_lno (int, optional): Maximum number of lines that the function can handle in a single file. If the file 
                                  is larger than this, it will be split into smaller snippets. Defaults to 500.
        Model (str, optional): Model to use for generating the docstrings. Defaults to "gpt-3.5-turbo".
        cost (str, optional): Cost of generating the docstrings, if the file is not split into snippets. 'cheap' 
                               will use gpt-3.5-turbo and the output will be the whole file (code+docstrings). 
                               'expensive' will use gpt-4 and the output will be only the docstrings. Defaults to 'cheap'.
    
    Returns:
        str: Generated docstrings.
    """
    with open(file_path, "r") as file:
        code = file.read()
        file.seek(0)
        no_lines = len(file.readlines())

    if no_lines <= 300 and cost == 'cheap':
        Model = 'gpt-3.5-turbo-16k'
        print(f'Analyze file directly using {Model}: ', file_path)
        command = """
        Output this same code with DETAILED docstrings (or try to improve if one already exists)
        in google format for all 
        function and class. Never try to generate docstrings for the imports.
        Begin a new line if an individual line of the docstring is longer than 90 characters.
        Additional information is provided by the summary
        of the repository this code is embedded in.
        As an answer, only output the expanded code as a string, since your answer will be 
        directly inserted into a python file which must be executable.
        And keep any white spaces, indentation, and new lines in the code.
        Just print out the source code with the generated docstrings.
        """
        command = ' '.join(line.strip() for line in command.split('\n')).strip()
        print("    Docstrings are generated. Waiting for a gpt response...")
        edited_code = gptapi(code, command, additional_info=additional_info, Model=Model) #gptapi(code, command, additional_info=additional_info, Model = 'gpt-3.5-turbo')
        code_lines = edited_code.split('\n')
        if code_lines[0].startswith('\'\'\'python'):
            del code_lines[0]
        if code_lines[-1].startswith('\'\'\''):
            del code_lines[-1]
        edited_code = '\n'.join(code_lines)       


        return edited_code

    
    if (no_lines <= max_lno and cost == 'expensive') or (300<no_lines<=max_lno and cost == 'cheap'):
        print(f'analyze file directly using {Model}: ', file_path)
        command = """
        For the given code snippet below "code to be edited:" output detailed 
        docstrings (or try to improve if one already exists) in google format 
        for every function and class. 
        If a docstring is already very well written, just reuse it for that function/class. 
        ONLY OUTPUT THE DOCSTRINGS with the corresponding name of the function or 
        class (e.g. def name():; so no args) and not the code of the functions/classes!!! 
        By not printing the code, I save tokens.
        Never try to generate docstrings for the imports.
        Begin a new line if an individual line of the docstring is longer than 90 characters.
        Additional information is provided by the summary of the repository 
        this code is embedded in to interpret the context of the code.
        """
        command = ' '.join(line.strip() for line in command.split('\n')).strip()
        print("    Docstrings are generated. Waiting for a gpt response...")
        docstrings = gptapi(code, command, additional_info=additional_info, Model=Model)

        return docstrings

    elif no_lines > max_lno:
        print('analyzing file by splitting it into snippets: ', file_path)
        # if Model in ('gpt-3.5-turbo', 'gpt-3.5-turbo-16k'):
        #     print(f'    WARNING: The current file exceeds max_lno, but you use a gpt3 model - which is not allowed for files > max_lno')
        #     print(f'    skip file: {file_path}')
        #     return ''
        info_file = f'info about file: \n{code_info(file_path)}'
        info = (additional_info + info_file) if additional_info else info_file
        code_snippets = make_snippets(file_path, max_lno=max_lno)
        #See how code is divided into snippets
        # for i, snippet in enumerate(code_snippets):
        #     print(f"{i+1}; lines: {snippet['lines']} ----------------------------")
        #     print(snippet['code'])
                
        command = """
        Generate a detailed docstring (or try to improve if it already exists) for every function and class of 
        the code snippet below "code to be edited:". ONLY OUTPUT THE 
        DOCSTRINGS with the corresponding name of the function or 
        class (e.g. def name():; so no args) and not the code of the functions/classes!!! By not printing 
        the code, I save tokens. 
        If a docstring is already very well written, just reuse it for that function/class.
        Never try to generate docstrings for the imports.
        The individual lines of the docstrings should also not be longer than 90 characters.
        To better construe the variables and context of the code snippet
        you receive "additional information:". It includes a summary of 
        the repository this code is embedded in, as well as all names, args
        and docstrings of the functions and classes of the whole python file 
        the snippet is from. Don't create docstrings for the functions/classes 
        under "Info about file:"!

        If there is no function/class in the current codesnippet output an empty string.
        Start your output with "start" and end with "end".
        Do not include any notes or comments in your answer!
        """
        command = ' '.join(line.strip() for line in command.split('\n')).strip()
        docstrings = '' #this will be a str of the edited func/classes
        print('    Docstrings are generated. Waiting for a gpt response...')
        for i, code_snippet in enumerate(code_snippets):
            docstrings += gptapi(code_snippet['code'], command, additional_info=info, Model=Model) + '\n'
        
        return docstrings
