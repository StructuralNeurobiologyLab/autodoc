# -*- coding: utf-8 -*-
# autodoc - automatic documentation for Python code
#
# Copyright (c) 2023 - now
# Max-Planck-Institute of biological Intelligence, Munich, Germany
# Authors: Karl Heggenberger, Joergen Kornfeld

import os
import yaml
import openai

def check_config():
    """
    This function checks for the existence of a configuration file named 'config_autodoc.yaml' in the
    home directory. If the file does not exist, it prompts the user to input their OpenAI API key and
    creates a new configuration file with this key. If the file exists, it reads the API key from the
    file and sets it as the OpenAI API key.
    
    Args:
        None
    
    Returns:
        None
    """
    home_directory = os.path.expanduser("~")
    config_file_path = os.path.join(home_directory, "config_autodoc.yaml")

    if not os.path.exists(config_file_path):
        print(f'No config_autodoc.yaml found in {home_directory}. You can create it yourself (path: {config_file_path}) or we can do it for you.')
        api_key = input("For automatic creation, please enter your OpenAI API key (it remains confidential): ")
        config_data = {"api_key": api_key}

        with open(config_file_path, "w") as config_file:
            yaml.dump(config_data, config_file)




    with open(config_file_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    openai.api_key = config["api_key"]

