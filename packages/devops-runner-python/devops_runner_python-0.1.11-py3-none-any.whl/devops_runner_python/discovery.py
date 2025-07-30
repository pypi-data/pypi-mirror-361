import os
import glob
import tomli
from typing import Dict
from pydantic import BaseModel
from colorama import Fore, Style

class Project(BaseModel):
    name: str
    path: str
    scripts: Dict[str, str]


def find_python_projects(base_dir: str = None) -> Dict[str, Project]:
    """
    Finds all pyproject.toml files under the given directory (or current working directory if None)
    and creates a dictionary mapping project names to their paths and scripts.
    
    Args:
        base_dir: The base directory to search from. Defaults to current working directory.
        
    Returns:
        A dictionary mapping project names to tuples containing:
        - The directory path
        - A dictionary of script names to their entry points
    """
    if base_dir is None:
        base_dir = os.getcwd()
    
    # Find all pyproject.toml files recursively
    pattern = os.path.join(base_dir, "**/pyproject.toml")
    pyproject_files = glob.glob(pattern, recursive=True)
    
    projects = {}
    
    for pyproject_path in pyproject_files:
        pyproject_dir = os.path.dirname(pyproject_path)
        if base_dir == pyproject_dir or 'venv/' in pyproject_dir:
            continue

        try:
            # Read and parse the pyproject.toml file
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomli.load(f)
            
            # Extract the project name if it exists
            if "project" in pyproject_data and "name" in pyproject_data["project"]:
                project_name = pyproject_data["project"]["name"]
                
                # Extract scripts if they exist
                scripts = pyproject_data.get("tool", {}).get("devops", {}).get("scripts", {})
                
                # Store the directory containing the pyproject.toml file and its scripts
                projects[project_name] = Project(name=project_name, path=pyproject_dir, scripts=scripts)
        except Exception as e:
            # Skip files that can't be parsed
            print(f"Error processing {pyproject_path}: {e}")
    
    print(f"{Fore.YELLOW}Workspace Discovery initialized. Workspaces found: {", ".join(projects.keys())}{Style.RESET_ALL}")
    return projects
