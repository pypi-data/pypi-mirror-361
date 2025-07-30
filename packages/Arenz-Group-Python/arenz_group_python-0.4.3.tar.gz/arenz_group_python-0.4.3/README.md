# Arenz_Group_Python
Python libs for NanoElectroCatalysis.

## The aim
 - Create a standard project folder structure.
 - Easy transfer of data from server to local folder for work-up
 - Load and save key-values-pairs
 - Load and save key-values-pairs into tables.
 - Path constants for easy access to data folders.




## Documentation

https://nanoelectrocatalysis.github.io/Arenz_Group_Python/

# Get started
In the project root folder, create a jupyter file.

## Package installation or upgrade using Jupyter

In order to install this package use the following line in a jupyter notebook: 
```python
%pip install arenz_group_python
```
In order to upgrade this package use the following line in a jupyter notebook: 

```python
%pip install arenz_group_python --upgrade
```

Restart the kernal.

## Create the basic project folder structure.

Create a jupyter notebook in the root folder of the project and run:
```python
from arenz_group_python import *
create_project_structure(".")
```
This will create a standard folder structure and some standard files.


## Import raw data files.
Make sure that all the folders you want to import as a file called:
<IDENTIFYIER>.tag 
where <IDENTIFYIER> can be a project name, example: "project.tag"

```python
from arenz_group_python import Project_Paths
pp = Project_Paths()
project_name = 'projectname'
user_initials = '' #This is optional, but it can speed up things
path_to_server = 'X:/EXP_DB'
pp.copyDirs(project_name, user_initials , path_to_server)
```

## Examples
See documentation.
