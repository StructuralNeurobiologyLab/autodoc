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
    Clones or copies the source code to the target directory. The source code can be a GitHub 
    repository, a local directory, or a local file. This function is used to prepare the 
    environment for the analysis of the code and the generation of docstrings.
    
    Args:
        input (str): The source code to be copied. It can be a URL of a GitHub repository, 
                     a path of a local directory, or a path of a local file.
        target_dir (str): The directory where the source code will be copied.
    
    Raises:
        ValueError: If the input is neither a valid URL nor a valid path.
    """
    path = os.path.join(os.getcwd(), input)
    print("input: ", input)
    print("path: ", path)
    print("target_dir: ", target_dir)

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
