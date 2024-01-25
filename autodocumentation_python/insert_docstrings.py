# -*- coding: utf-8 -*-
# autodoc - automatic documentation for Python code
#
# Copyright (c) 2023 - now
# Max-Planck-Institute of biological Intelligence, Munich, Germany
# Authors: Karl Heggenberger, Joergen Kornfeld

import re
import os
import ast
import astunparse
import traceback
from autodocumentation_python.gptapi import gpt_compare
from autodocumentation_python.check_config import check_config

def shift_docstring(docstring, indent):
    """
    Shifts the docstring by a specified number of spaces.
    
    Args:
        docstring (str): The docstring to be shifted.
        indent (int): The number of spaces to shift the docstring by.
    
    Returns:
        str: The shifted docstring. If the input docstring is None, it returns an empty string.
    """
    if docstring is None:
        return ''
    
    docstring = "\n".join(['"""', docstring, '"""'])
    lines = docstring.strip().split("\n")
    shifted_lines = [" " * indent + line for line in lines] #these docstrings are already shifted by 4 spaces
    shifted_docstring = "\n".join(shifted_lines) + "\n"
    
    return shifted_docstring


def remove_start_end_lines(docstrings: str):
    """
    Removes the start and end lines from a code string.
    
    Args:
        code_string (str): The code string from which start and end lines are to be removed.
    
    Returns:
        str: The cleaned code string with start and end lines removed.
    """
    # Define the pattern to match the start and end lines
    pattern = r'(^start$|^end$|^```python$|^```$|^(?!def|class)([a-zA-Z_]\w*)\s*\([^)]*\):\s*(\'\'\'[^\'\']*\'\'\'|"""[^"]*"""))'
    # Use regular expressions to remove the matched lines
    cleaned_code = re.sub(pattern, "", docstrings, flags=re.MULTILINE | re.DOTALL)

    return cleaned_code

#next 3 definitions are used to find the parent nodes of a node in the ast
class ParentAssigner(ast.NodeVisitor):
    def visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
            self.visit(child)

def assign_parent_to_nodes(tree):
    """
    Assigns parent nodes to each node in an AST.
    
    Args:
        tree (ast.AST): The AST to which parent nodes are to be assigned.
    """
    # Create an instance of the ParentAssigner and visit the tree
    parent_assigner = ParentAssigner()
    parent_assigner.visit(tree)


def find_parent_nodes(node, tree):
    """
    Finds the parent nodes of a given node in an AST.
    
    Args:
        node (ast.AST): The node whose parent nodes are to be found.
        tree (ast.AST): The AST in which the node exists.
    
    Returns:
        list: A list of parent nodes of the given node.
    """
    #assign_parent_to_nodes(tree) #must be called before this function is called
    parents = []

    while isinstance(node, ast.Module) is False:
        node = node.parent
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            parents.insert(0,node.name)

    return parents


def get_name_args(node):
    """
    Gets the name and arguments of a class or function definition node.
    
    Args:
        node (ast.AST): The class or function definition node.
    
    Returns:
        tuple: A tuple containing the name and arguments of the node.
    """
    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
        name = node.name
        if isinstance(node, ast.FunctionDef):
            args = f"{astunparse.unparse(node.args).strip()}"
        if isinstance(node, ast.ClassDef):
            bases = [base for base in node.bases]
            #args = f"{', '.join([base.id for base in bases])}" if bases else ''
            
            try:
                args = f"{', '.join([base.id for base in bases])}" if bases else ''
            except AttributeError:
                try:
                    args = f"{', '.join([base.value.id for base in bases])}" if bases else ''
                except AttributeError:
                    args = ''
    return name, args

def find_end_of_definition(code_lines, node):
    """
    Finds the end line of a class or function definition in a code file.
    
    Args:
        code_lines (list): The list of lines in the code file.
        node (ast.AST): The AST node representing the class or function definition.
    
    Returns:
        int: The line number of the end of the definition.
    """
    start_lno = node.__dict__['lineno']
    end_lno = node.body[0].lineno
    starting_text = code_lines[start_lno-1:end_lno-1]
    
    pattern = '(:\s*)$|(:\s*#.*$)'
    
    for i, line in enumerate(starting_text, start=1):
        matches = re.search(pattern, line, re.M)
        if matches:
            break
    
    return start_lno + i



def insert_docstrings(file_path, docstrings, Model):
    """
    Inserts docstrings into a Python file at the appropriate locations.
    
    Args:
        file_path (str): The path to the Python file where docstrings are to be inserted.
        docstrings (str): The string of docstrings to be inserted.
    
    Note:
        The docstrings are first cleaned by removing the start and end lines. The function then parses 
        the cleaned docstrings into an abstract syntax tree (AST). It iterates over all nodes in the 
        AST, and for each class or function definition, it inserts the corresponding docstring into 
        the Python file.
    """
    # docstrings = remove_start_end_lines(docstrings) #remove "start" and "end"- lines generated by gpt

    # numb_node_doc = []
    # numb_inserted_nodes = []
    # numb_nodes_code = []
    # #get amout of new classes and functions in original file:
    # with open(file_path, "r") as file:
    #     code = file.read()
    # tree_code = ast.parse(code)
    # for node in ast.walk(tree_code):
    #     if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
    #         numb_nodes_code.append(node.name)

    # tree_doc = ast.parse(docstrings)
    # assign_parent_to_nodes(tree_doc) #make .parent attribute for nodes in docstring ast

    # for node_doc in ast.walk(tree_doc):         #iterate over all nodes in the docstring ast
    #     if isinstance(node_doc, (ast.ClassDef, ast.FunctionDef)):
    #         if not ast.get_docstring(node_doc):
    #             continue
    #         numb_node_doc.append(node_doc)
    #         try:
    #             inserted_node = insert_1_docstring(node_doc, tree_doc, file_path, Model) #insert docstring one by one into the code
    #             if inserted_node:
    #                 numb_inserted_nodes.append(inserted_node)
    #         except AttributeError:
    #             print(f'insertion did not work for node: {node_doc.name}, {node_doc}')
    #             traceback.print_exc()

    # not_inserted = [node.name for node in numb_node_doc if node not in numb_inserted_nodes]
    # not_generated = [node for node in numb_nodes_code if node not in [node.name for node in numb_node_doc]]   #the nodes are from different trees -> not comparable/identical
    # if len(numb_inserted_nodes) != len(numb_nodes_code):
    #     print(f'    {len(numb_nodes_code)} new classes/functions in original file')
    #     print(f'    {len(numb_node_doc)} docstrings generated (can be found in gpt_output)')
    #     print(f'    {len(not_generated)} docstrings not generated: {", ".join(not_generated)}')
    #     print(f'    {len(not_inserted)} of generated {len(numb_node_doc)} docstrings not inserted: {", ".join(not_inserted)}')
    # print(f' -> {len(numb_inserted_nodes)}/{len(numb_nodes_code)} docstrings generated and inserted')


#This is attempt in progress to introduce parents to the output of not inserted/generated docstrings 
    docstrings = remove_start_end_lines(docstrings) #remove "start" and "end"- lines generated by gpt

    dict_nodes_doc = []
    dict_inserted_nodes = []
    #get amout of new classes and functions in original file:
    tree_doc = ast.parse(docstrings)
    assign_parent_to_nodes(tree_doc) #make .parent attribute for nodes in docstring ast


    for node_doc in ast.walk(tree_doc):         #iterate over all nodes in the docstring ast
        if isinstance(node_doc, (ast.ClassDef, ast.FunctionDef)):
            if not ast.get_docstring(node_doc):
                continue
            dict_nodes_doc.append({"name": node_doc.name, "parents": find_parent_nodes(node_doc, tree_doc)})
            try:
                insertion_successful, node_info = insert_1_docstring(node_doc, tree_doc, file_path, Model) #insert docstring one by one into the code
                if insertion_successful:
                    dict_inserted_nodes.append({"name": node_info[0].name, "parents": node_info[1]})
                elif not insertion_successful:
                    continue
            except Exception as e:
                print(f"An error occurred: {e}")
                traceback.print_exc()
                print(f'insertion did not work for node: {node_doc.name}, (parents: {find_parent_nodes(node_doc, tree_doc)}, node: {node_doc}')

    with open(file_path, "r") as file:
        code = file.read()
    tree_code = ast.parse(code)
    assign_parent_to_nodes(tree_code)
    dict_nodes_code = [{"name": node.name, "parents": find_parent_nodes(node, tree_code)} for node in ast.walk(tree_code) if isinstance(node, (ast.ClassDef, ast.FunctionDef))]

    not_inserted = [dict_node for dict_node in dict_nodes_doc if dict_node not in dict_inserted_nodes]
    not_generated = [dict_node for dict_node in dict_nodes_code if dict_node not in [dict_doc for dict_doc in dict_nodes_doc]]  #the nodes are from different trees -> not comparable/identical

    if len(dict_inserted_nodes) != len(dict_nodes_code):
        print(f'    {len(dict_nodes_code)} new classes/functions in original file')
        print(f'    {len(dict_nodes_doc)} docstrings generated (can be found in gpt_output)')
        print(f'    {len(not_generated)} docstrings not generated:')
        for dict in not_generated:
            name = dict["name"]
            parents = ", ".join(dict["parents"]) if dict["parents"] else " --- "
            print("    "*2,f"{name} (Parents: {parents}); ")
        print(f'    {len(not_inserted)} of {len(dict_nodes_doc)} generated docstrings not inserted:')
        for dict in not_inserted:
            name = dict["name"]
            parents = ", ".join(dict["parents"]) if dict["parents"] else " --- "
            print("    "*2,f"{name} (Parents: {parents}); ")
    print(f' -> {len(dict_inserted_nodes)}/{len(dict_nodes_code)} docstrings generated and inserted')


def insert_1_docstring(node_doc, tree_doc, file_path, Model):
    """
    Inserts a single docstring into a Python file.
    
    Args:
        node_doc (ast.AST): A node from the docstring AST.
        file_path (str): The path to the Python file where the docstring is to be inserted.
    
    Note:
        The function reads the Python file and parses it into an AST. It then iterates over all nodes 
        in the code AST. For each class or function definition, it checks if the name and parent nodes
        matches the name of the docstring node. If a match is found, it gets the docstring from the 
        docstring node and checks if the code node already has a docstring. If it does, the old 
        docstring is removed and the new one is inserted. If it doesn't, the new docstring is 
        inserted at the appropriate location. The function then writes the modified code back to 
        the Python file.
    """
    with open(file_path, "r") as file:
        code = file.read()
        file.seek(0)
        lines_code = file.readlines()
    tree_code = ast.parse(code) #need to be updated after each insertion since linelno of nodes change

    assign_parent_to_nodes(tree_code) #make .parent attribute for nodes in code ast
    parents_doc = find_parent_nodes(node_doc, tree_doc)

    for node_code in ast.walk(tree_code):
        if isinstance(node_code, (ast.ClassDef, ast.FunctionDef)):
            name_doc, args_doc = get_name_args(node_doc)
            name_code, args_code = get_name_args(node_code)
            parents_code = find_parent_nodes(node_code, tree_code)
            if name_code == name_doc and parents_doc == parents_code: # and args_code == args_doc    #sometimes additional info in agrs (e.g. type) is added by gpt -> not comparable
                docstring = ast.get_docstring(node_doc)
                if ast.get_docstring(node_code) is not None:
                    docstring = remove_start_end_lines(compare_docstrings(ast.get_docstring(node_code), docstring, Model)).strip()
                    #docstring = remove_start_end_lines(ast.get_docstring(node_code)).strip() #comment out above and enable this line to prevent comparison of old docstrings
                    start = node_code.body[0].__dict__['lineno'] #start line of old docstring
                    end = node_code.body[0].__dict__['end_lineno'] #end line of old docstring
                    for i in range(end-start+1):
                        del lines_code[start-1] #delete old docstring
                    indent = node_code.body[0].col_offset
                    shifted_docstring = shift_docstring(docstring, indent)
                    lines_code.insert(start-1, shifted_docstring)
                elif ast.get_docstring(node_code) is None:
                    start = find_end_of_definition(lines_code, node_code) - 1
                    indent = node_code.body[0].col_offset
                    shifted_docstring = shift_docstring(docstring, indent)
                    lines_code.insert(start, shifted_docstring)
                with open(file_path, "w") as file:
                    file.truncate()
                    file.write(''.join(lines_code))
                return True, (node_doc, parents_doc)
    return False, None
   
def compare_docstrings(old_docstring, new_docstring, Model):
    if old_docstring.strip() == new_docstring.strip():
        return new_docstring
    else:
        if Model != 'gpt-4-1106-preview':
            Model = 'gpt-4' 
        command = f'''
I want to replace the old docstring with a new one generated by GPT. 
However, it may be that the generated one does not contain all the 
information of the old docstring. Therefore, compare both versions 
and update the new docstring. If the information is conflicting, use 
the information from the old docstring. If there is no difference, 
simply return the new docstring - without further notification. 
The output docstring should have a maximum of 90 characters per line.

Your output should start with "start" and end with "end" (dont indent your main output because of this and no """):
start
updated generated docstring...
end


old docstring:
{old_docstring}
generated docstring:
{new_docstring}
'''
        edited_docstring = gpt_compare(command, Model=Model, temperature=0.8)
        return edited_docstring




# #MANUALLY INSERT DOCSTRINGS INTO CODE:
# from autodocumentation_python.check_config import check_config
# check_config()  #get api key

# path_gpt_output = os.path.join(os.getcwd(), 'reps_edited_retry1', 'gpt_output')


# for _, _, files in os.walk(path_gpt_output):
#     for file in files:
#         path_code = os.path.join(os.getcwd(), 'reps_edited_retry1', file)
#         path_doc = os.path.join(path_gpt_output, file)
#         with open(path_doc, "r") as file:
#             docstrings = file.read()
#         Model = 'gpt-4'
#         insert_docstrings(path_code, docstrings, Model)
    
    

# file_name = 'segmentation.py'
# edited_folder_name = 'reps_edited_try2'
# path_doc = os.path.join(os.getcwd(), edited_folder_name, 'gpt_output', file_name)
# path_code = os.path.join(os.getcwd(), edited_folder_name, file_name)

# with open(path_doc, "r") as file:
#     docstrings = file.read()

# Model = 'gpt-4'
# insert_docstrings(path_code, docstrings, Model)