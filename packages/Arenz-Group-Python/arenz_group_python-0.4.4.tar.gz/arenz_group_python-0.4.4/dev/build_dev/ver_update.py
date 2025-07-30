import toml
import json
from pathlib import Path
import re

def version_updated():
    
    
    # Opening JSON file
    pa = Path().cwd()
    for i in range(5):
        pa = pa.parent 
        pfile = pa/"package.json"
        if(pfile.exists()): 
            break
    f = open(pfile)

    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    # Iterating through the json
    # list

    project_version =data["version"]
    print("Project Version",project_version)
    # Closing file
    f.close()
    
    pyproject = pa /"pyproject.toml"
    with open(pyproject, "r") as f:
        data = toml.load(f)
    print(data)
    data["project"]["version"]=project_version
    with open(pyproject, 'w') as f:
        toml.dump(data, f)
    
    version_update_PackageFile(pa, project_version)
        



def version_update_PackageFile(project_path:Path, project_version:str):
    
    Package_Path = project_path / "src" /"arenz_group_python"/"__init__.py"
    data = None
    with open(Package_Path, "r") as f:
        data = f.read()
        #print(data)
        data=re.sub('__version__ = \"[0-9.]+\"',"__version__ = \"" + project_version+"\"", data)
        #print(data)
        f.close()
    with open(Package_Path, 'w') as f:
        if(data!="" or data is not None):
            f.write(data)
            print("package file was updated")
        f.close