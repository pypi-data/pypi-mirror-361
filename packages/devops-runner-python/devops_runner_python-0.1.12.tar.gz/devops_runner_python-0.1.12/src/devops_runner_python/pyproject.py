import os
from typing import Any
import tomli
from pydantic import BaseModel

class PyprojectData(BaseModel):
    data: dict[str, Any]
    deployment: dict[str, Any]


def get_pyproject_data():
    """
    Reads the pyproject.toml file in the current working directory and returns its data.
    """
    pyproject_path = os.path.join(os.getcwd(), "pyproject.toml")
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomli.load(f)
        
    deployment = pyproject_data.get("tool", {}).get("devops", {}).get("deployment", {})
    return PyprojectData(data=pyproject_data, deployment=deployment)
    