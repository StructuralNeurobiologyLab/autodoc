import openai


def gptapi(code: str, command: str, Model: str, additional_info: str = None, 
            temperature: float = 0.2) -> str:
    """
    Generates a GPT output for the given code and command using the OpenAI API.
    
    This function constructs a series of messages that include a system message, a user command, and the 
    code to be edited. If additional information is provided, it is also included in the messages. The 
    function then sends these messages to the OpenAI API and retrieves the generated output.
    
    Args:
        code (str): The code that needs to be analyzed and edited.
        command (str): The command that specifies the type of editing to be performed on the code.
        additional_info (str, optional): Additional contextual information about the code. This could 
        include details about the repository the code is embedded in. Defaults to None.
        temperature (float, optional): The temperature parameter for the GPT model. A higher value 
        makes the output more random, while a lower value makes it more deterministic. Defaults to 0.1.
        Model (str, optional): The model to be used for generating the GPT output. Defaults to 
        "gpt-3.5-turbo".
    
    Returns:
        str: The generated GPT output which could be a detailed summary or docstring based on the 
        command provided.
    """

    messages = [
        {"role": "system", "content": "We aim to edit a repository with Google docstrings."},
        {"role": "user", "content": command},
        {"role": "user", "content": f"code to be edited:\n{code}"},
    ]

    if additional_info is not None:
        full_additional_info = f"additional_info: \n {additional_info} \nend of additional_info"
        messages.insert(2, {"role": "user", "content": full_additional_info})

    response = openai.ChatCompletion.create(
        model=Model,
        messages=messages,
        temperature=temperature,
    )
    answer = response['choices'][0]['message']['content']

    return answer