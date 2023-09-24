import os
import shutil
import urllib.request
from git import Repo


def is_valid_url(url: str) -> bool:
    """
    Checks if a given URL is valid by attempting to open it. This function is used to validate 
    the URL of a GitHub repository before cloning it.
    
    Args:
        url (str): The URL to be checked.
    
    Returns:
        bool: Returns True if the URL is valid and can be opened, otherwise returns False.
    """
    try:
        response = urllib.request.urlopen(url)
        return True
    except Exception:
        return False

def clone_source(input: str, target_dir: str) -> None:
    """
    Clones a source from a given input (URL or local path) into a target directory. If the input is a valid
    URL, it clones the repository into the target directory. If the input is a valid local directory, it copies
    the directory into the target directory. If the input is a valid local file, it copies the file into the
    target directory. If the input is neither a valid URL nor a valid local path, it raises a ValueError.
    
    Args:
        input (str): The input source to be cloned. It can be a URL or a local path.
        target_dir (str): The target directory where the source will be cloned.
    
    Raises:
        ValueError: If the input is neither a valid URL nor a valid local path.
    """
    path = os.path.join(os.getcwd(), input)
    print("input: ", input)
    print("path: ", path)
    print("target_dir: ", target_dir)

    # if os.path.isdir(target_dir):
    #     shutil.rmtree(target_dir)
    #     print(f"Deleted {target_dir} \n")

    if is_valid_url(input):
        os.makedirs(target_dir)
        Repo.clone_from(input, target_dir)
        print(f"Cloned repository into {target_dir} \n")
    elif os.path.isdir(path):
        shutil.copytree(path, target_dir)
        print(f"Copied folder into {target_dir} \n")
    elif os.path.isfile(path):
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy(path, target_dir)
        print(f"Copied file into {target_dir} \n")
    else:
        raise ValueError("Input is neither a valid URL nor a valid path.")


def copy_py_files(path_source, path_dest):
    """
    Copies all Python files from a source directory to a destination directory. It walks through the source
    directory and its subdirectories, and for each Python file found, it constructs the source and destination
    file paths and copies the file to the destination. It also creates the destination directory if it doesn't
    exist. The 'edited_repository' folder is excluded from the analysis.
    
    Args:
        path_source (str): The source directory from where the Python files will be copied.
        path_dest (str): The destination directory where the Python files will be copied.
    """
    # Walk through the source directory and its subdirectories
    print('copying py files')
    for root, dirs, files in os.walk(path_source):
        if 'edited_repository' in dirs:
            dirs.remove('edited_repository') #exlude 'edited_repository' folder from analysis
        for file in files:
            if file.endswith(".py"):  # Check if the file is a Python file
                # Construct the source and destination file paths
                source_file = os.path.join(root, file)
                dest_file = os.path.join(path_dest, os.path.relpath(source_file, path_source))

                # Create the destination directory if it doesn't exist
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                # Copy the file to the destination
                shutil.copy(source_file, dest_file)
