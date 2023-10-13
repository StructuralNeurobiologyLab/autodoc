# -*- coding: utf-8 -*-
# autodoc - automatic documentation for Python code
#
# Copyright (c) 2023 - now
# Max-Planck-Institute of biological Intelligence, Munich, Germany
# Authors: Karl Heggenberger, Joergen Kornfeld

import os
import ast
import astunparse


def make_snippets(file_path: str, max_lno: int = 300):
    """
    Generates code snippets from a file based on the maximum number of lines. This function is used to 
    break down a large code file into smaller snippets for easier analysis and docstring generation.
    
    Args:
        file_path (str): The path to the file from which code snippets are to be generated.
        max_lno (int, optional): The maximum number of lines for each snippet. Defaults to 300.
    
    Returns:
        list: A list of dictionaries. Each dictionary contains a code snippet (str) ['code'] and its respective 
        line count (int) ['lines'].
    """

    def length_of_node(node):
        """
        Calculates the length of a node in terms of lines of code. This function is used to determine the 
        size of a code snippet based on the number of lines in the node.
        
        Args:
            node (ast.AST): The node to calculate the length of.
        
        Returns:
            int: The length of the node in terms of lines of code.
        """
        return node.end_lineno - node.lineno + 1
    
    with open(file_path, "r") as file:
        code = file.read()
        file.seek(0)
        lines = file.readlines()

    tree = ast.parse(code)

    cutted_file = []
    current_snippet = ''
    current_snippet_length = 0
    current_snippet_start = 1

    def evaluate_node(node):
        """
        Evaluates a node to determine if it should be included in the current snippet or start a new one. 
        This function is used to ensure that the size of each code snippet does not exceed the maximum 
        number of lines specified.
        
        Args:
            node (ast.AST): The node to evaluate.
        
        Returns:
            None
        """
        nonlocal current_snippet
        nonlocal current_snippet_length
        nonlocal current_snippet_start
        if length_of_node(node) + current_snippet_length <= max_lno:
            current_snippet_length = node.end_lineno + 1 - current_snippet_start
        else:
            # end current snippet
            text_node = astunparse.unparse(node).strip()
            if text_node.startswith('@'):
                current_snippet_list = lines[current_snippet_start-1 : node.lineno-2]
                current_snippet_length = len(current_snippet_list)
                current_snippet = ''.join(current_snippet_list)
            elif not text_node.startswith('@'):
                current_snippet_list = lines[current_snippet_start-1 : node.lineno-1]
                current_snippet_length = len(current_snippet_list)
                current_snippet = ''.join(current_snippet_list)
            dict_current_snippet = {'code': current_snippet, 'lines': current_snippet_length}
            cutted_file.append(dict_current_snippet)
            current_snippet = ''
            current_snippet_length = 0

            # start new snippet now
            if text_node.startswith('@'):
                current_snippet_start = node.lineno - 1
            elif not text_node.startswith('@'):
                current_snippet_start = node.lineno
            
            if length_of_node(node) <= max_lno:
                current_snippet_length = node.end_lineno + 1 - current_snippet_start
            elif length_of_node(node) > max_lno:
                children = node.body
                for child in children:
                    evaluate_node(child)


    for node in tree.body:
        evaluate_node(node)

    # end last snippet
    current_snippet_list = lines[current_snippet_start-1 :]
    current_snippet_length = len(current_snippet_list)
    current_snippet = ''.join(current_snippet_list)
    dict_current_snippet = {'code': current_snippet, 'lines': current_snippet_length}
    cutted_file.append(dict_current_snippet)

    return cutted_file
