---
title: Arenz Group Python Package
nav_order: 1
---
# Install and Update
### Install: 
```python
 %pip install arenz_group_python
```
### Update
```python
 %pip install arenz_group_python -U
```


# Create a standard project with folders
```python
from arenz_group_python import Project_Paths as pp
pp().create_project_structure()
```

# Project Path constants
There are two path constants: pDATA_RAW, pDATA_TREATED
These constants return a PathLib to the raw data folder and the treated data folder.
```python
    from arenz_group_python import pDATA_RAW, pDATA_TREATED 
    file = pDATA_RAW / "FileName.txt"
    file2 = pDATA_TREATED / "FileName.txt"
```


# Save key values(dict) to a table-file(cvs)

see example [example/ex_file_dict.md]

# Copy Raw data from the server into the raw data folder.

```python
    from arenz_group_python import Project_Paths
    pp = Project_Paths()
    project_name = 'projectname'
    user_initials = '' #This is optional, but it can speed up things
    path_to_server = 'X:/EXP_DB'
    pp.copyDirs(project_name, user_initials, path_to_server )
```
