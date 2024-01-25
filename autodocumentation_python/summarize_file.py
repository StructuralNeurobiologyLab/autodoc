# -*- coding: utf-8 -*-
# autodoc - automatic documentation for Python code
#
# Copyright (c) 2023 - now
# Max-Planck-Institute of biological Intelligence, Munich, Germany
# Authors: Karl Heggenberger, Joergen Kornfeld

import ast
import astunparse
import os


def gen_shifted_docstring(node):
    """
    Generates a shifted docstring for a given node. If the node does not have a docstring, it 
    returns an empty string.
    
    Args:
        node (ast.AST): An abstract syntax tree node representing a Python class or function.
    
    Returns:
        str: A string containing the shifted docstring of the node, or an empty string if the 
        node does not have a docstring.
    """
    if ast.get_docstring(node) is None:
        return ''
    
    docstring = "\n".join(['"""' , ast.get_docstring(node), '"""'])
    lines = docstring.strip().split("\n")
    shifted_lines = [' ' * 4 + " " * node.col_offset + line for line in lines]
    shifted_docstring = "\n".join(shifted_lines) + "\n"
    
    return shifted_docstring


def node_info(node):
    """
    Extracts the definition (def/class: name(args)) of a class or function and its docstring with 
    proper indentation from an abstract syntax tree node. This function does not distinguish 
    between a class defined with or without parentheses. For example, class Organelle: and class 
    Organelle(): are both parsed as class Organelle: .
    
    Args:
        node (ast.AST): An abstract syntax tree node representing a Python class or function.
    
    Returns:
        str: A string containing the class or function definition and its docstring, properly 
        indented.
    """

    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
        if isinstance(node, ast.FunctionDef):
            name = "def " + node.name
            args = f"({astunparse.unparse(node.args).strip()})"
        if isinstance(node, ast.ClassDef):
            name = "class " + node.name
            args = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    args.append(base.id)
                elif isinstance(base, ast.Attribute):
                    args.append(base.attr)
                else:
                    print(3*'    ' + f'Argument of class {node.name} is not a Name or Attribute -> not supported yet.')
            args = f"({', '.join(args)})" if args else ''

        indent = " " * node.col_offset
        shifted_name_args = f"{indent}{name}{args}:"
        shifted_docstring = gen_shifted_docstring(node)
        node_snippet = "\n".join([shifted_name_args, shifted_docstring])

        return node_snippet


def code_info(file_path):
    """
    Extracts the class and function definitions from a Python file and returns them as a string. 
    It reads the file, parses the code into an abstract syntax tree, and visits each node in the 
    tree to extract the class and function definitions.
    
    Args:
        file_path (str): The path to the Python file.
    
    Returns:
        str: A string containing the class and function definitions from the Python file.
    """
    with open(file_path, "r") as file:
        code = file.read()

    parsed_code = ast.parse(code)
    
    info = ''

    def visit_node(node):
        """
        Visits a node in the abstract syntax tree and appends the information of the node to the info 
        string if the node is a class or function definition. It also recursively visits the children 
        of the node.
        
        Args:
            node (ast.AST): An abstract syntax tree node.
        
        Returns:
            str: A string containing the class and function definitions from the node and its 
            children.
        """
        nonlocal info
        if node_info(node) is not None:  #only for class- and funct-nodes
            info += node_info(node)
            for children in node.body:
                visit_node(children)
            return info

    for node in parsed_code.body:
        visit_node(node)
    
    return info

# test_file_name = '' #must be present in current working directory
# destination_file_name = ''
# file_path = os.path.join(os.getcwd(), test_file_name)
# dest = os.path.join(os.getcwd(), destination_file_name)
# with open(dest, 'w') as f:
#     f.write(code_info(file_path))