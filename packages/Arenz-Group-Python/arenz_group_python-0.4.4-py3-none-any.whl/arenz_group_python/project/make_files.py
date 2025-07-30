from pathlib import Path

from .default_paths import PROJECT_FOLDERS

from .make_file_eLabFTW import make_copyFromELABFTW_file


                    
################################################################################
def make_project_files( main_dir: Path):               
    print("\ncreating files:\n")
    #Create a .env file for python.
    make_env_file(main_dir)
    make_requirement_file(main_dir)
    make_script_file(main_dir)
    # make_copy2server_file(main_dir) //obsolete, use the copy_from_server file instead.
    make_copyFromELABFTW_file(main_dir)
    make_Project_Update_All_Modules_file(main_dir)
         
    def_files = [
        main_dir / PROJECT_FOLDERS.nb_models / "modelData.ipynb",
        main_dir / PROJECT_FOLDERS.scripts  / "my_Module.py"
    ]
    for file in def_files:
        try:
            fo= open(file,"x")
            fo.close()
            print(f"+\"{file}\" was created")
        except FileExistsError:
            print(f"-\"{file}\" already exists")

    
    
    path = main_dir / PROJECT_FOLDERS.nb_exploration / "extractData.ipynb"
    try:
        with open(path,"x") as f:
            f.write('''{
    "cells": [
    {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# Exploring the data",
        "use this notebook and others to extract data.",
        "",
        "To use with electrochemistry data, use the following import:",
        "from ec4py import EC_Data #to load in a single tdms file",
        "",
        "from ec4py import CV_Data # to import a single CV.",
        "",
        "from ec4py import CV_Datas # to import a multiple CVs at once form a list of paths",
        "",
        "from arenz_group_python import Project_Paths # to load in path constants.",
        "",
        "from arenz_group_python import save_key_values # to save key values.",
        ""
        ]
    },
    {
    "cell_type": "code",
    "execution_count": null,
    "metadata": {},
    "outputs": [],
    "source": [
        "#from arenz_group_python import EC_Data",
        "#from arenz_group_python import Project_Paths",
        "#from arenz_group_python import CV_Data",
        "",
        "#if there is a file in the rawdata folder:",
        "#PATH_TO_FILE = Project_Paths().rawdata_path / \'FILE_NAME\' ",
        "#file1 = EC_Data(\'PATH_TO_FILE\')",
        "#file1.plot(\'E\',\'i\') # for a i vs E plot "
    ]
    },
    {
    "cell_type": "code",
    "execution_count": null,
    "metadata": {},
    "outputs": [],
    "source": [
        "from arenz_group_python import save_key_values",
        "",
        "# The target file is assumed to be in the data folder",
        "save_key_values(\'extracted_values.csv\',\'sample 7\', [4,2,5,4,5]) "
    ]
    }
    ],
    "metadata": {
    "kernelspec": {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3"
    },
    "language_info": {
    "name": "python",
    "version": "3.11.5"
    }
    },
    "nbformat": 4,
    "nbformat_minor": 2
    }''')
            f.close()
        print(f"+\"{path.name}\" was created")
    except FileExistsError:
        print(f"-\"{path.name}\" already exists")  
    
    
###################################################################################################


def make_script_file(main_dir: Path):
    path = main_dir / PROJECT_FOLDERS.scripts / "__init__.py"
    try:
        with open(path,"x") as f:
            f.write("# Leave it empty. This is just a special file that tells pip that your main module is in this folder.\n# No need to add anything here. Feel free to delete this line when you make your own package.")
            f.close()
        print(f"+\"{path.name}\" was created")
    except FileExistsError :
        print(f"-\"{path.name}\" already exists")
###################################################################################################

def make_env_file( main_dir: Path):
    path = main_dir / ".env"
    
    file_Env =  ["#Python environment file\n",
                "#The PYTHONPATH adds relative and absolute search paths\n",
                "# Paths are relative to the workspace folder for python,",
                "# however, they are relative to the jypiter notebook when execute in a notebook.\n",
                "# Therefor, an absolute search path is needed if jypiter is to be used.\n",
                f"WORKSPACE_FOLDER={str(main_dir)}\n",
                "PYTHONPATH=${WORKSPACE_FOLDER}"+ f"/{PROJECT_FOLDERS.scripts};\n",
                "# so it is best make the path absolute.  ';'\n",
                "\n",
                "# elabFTW api keys  ';'\n",
                "# Create your own API key in eLabFTW and save it here.\n",
                "elab_API_KEY=""\n",
                "# URL to the elabFTW server api ';'\n",
                "elab_API_HOST=https://elabftw.dcbp.unibe.ch/api/v2\n",
                ]
    try:
        with open(path,"x") as f:
            f.writelines(file_Env)
            #f.write(f"PYTHONPATH={PROJECT_FOLDERS.scripts}\r\n.\n")
            f.close()
        print(f"+\"{path.name}\" was created")
    except FileExistsError :
        print(f"-\"{path.name}\" already exists") 
        
        

################################################################################                
def make_project_files_data( main_dir: Path):               

    path = main_dir / PROJECT_FOLDERS.rawdata / "README.txt"
    file_raw =  ["# Use the rawdata folder to store all experimental data. ONLY!!!!.\n"
                "Copy the following text into a notebook:\n\n",
                "from arenz_group_python import Project_Paths\n",
                "\n",
                "pp = Project_Paths()\n",
                "project_name = \'projectname\'\n",
                "user_initials = \'\' #This is optional, but it can speed up things\n", 
                "path_to_server = \'X:/EXP_DB\'\n",
                "pp.copyDirs(path_to_server, user_initials , project_name )\n",
                ]
    try:
        with open(path,"x") as f:
            f.writelines(file_raw)
            f.close()
        print(f"+\"{path.name}\" was created")
    except FileExistsError :
        print(f"-\"{path.name}\" already exists")
        
        
    ##### PATH to data file    
    path = main_dir / PROJECT_FOLDERS.treated_data / "README.txt"
    try:
        with open(path,"x") as f:
            f.write("# Use the data folder to store all extracted values from data manipulation. \n\nNO RAW DATA!!!!.")
            f.close()
        print(f"+\"{path.name}\" was created")
    except FileExistsError :
        print(f"-\"{path.name}\" already exists")
        
    path = main_dir / PROJECT_FOLDERS.treated_data / "extracted_values.csv"
    try:
        with open(path,"x") as f:
            f.write("")
            f.close()
        print(f"+\"{path.name}\" was created")
    except FileExistsError :
        print(f"-\"{path.name}\" already exists")
###########################################################################################

def make_requirement_file(main_dir: Path):
    try: 
        from pip._internal.operations import freeze
    except ImportError: # pip < 10.0
        from pip.operations import freeze

    pkgs = freeze.freeze()
    path = main_dir / "requirements.txt"
    
    
    
    with open(path,"wt") as f:
        for pkg in pkgs:
            f.write(pkg+"\n")
        f.close()
    print(f"+\"{path.name}\" was created or updated")
    return

############################################################################################
def make_copy2server_file(main_dir:Path):
    path = main_dir / PROJECT_FOLDERS.nb_exploration / "copy_data_from_server.ipynb"
    try:
        with open(path,"x") as f:
            f.write('''{
    "cells": [
    {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# Copy data from teh server",
        "use this notebook to copy data from the server.",
        "",
        "Tag the folder you want to by first creating a file with the name:",
        "",
        "{Project Name}.tag",
        "",
        "ex: my_first_project.tag",
        " ",
        "",
        ""
        ]
    },
    {
    "cell_type": "code",
    "execution_count": null,
    "metadata": {},
    "outputs": [],
    "source": [
        "from arenz_group_python import Project_Paths",
        ""
    ]
    },
    {
    "cell_type": "code",
    "execution_count": null,
    "metadata": {},
    "outputs": [],
    "source": [
        "pp = Project_Paths()",
        "project_name = \'projectname\'",
        "user_initials = \'\' #This is optional, but it can speed up things", 
        "path_to_server = \'X:/EXP_DB\'",
        "pp.copyDirs(project_name, user_initials , path_to_server )",
        ""
    ]
    }
    ],
    "metadata": {
    "kernelspec": {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3"
    },
    "language_info": {
    "name": "python",
    "version": "3.11.5"
    }
    },
    "nbformat": 4,
    "nbformat_minor": 2
    }''')
            f.close()
        print(f"+\"{path.name}\" was created")
    except FileExistsError:
        print(f"-\"{path.name}\" already exists")   
    return


#######################################
############################################################################################
def make_Project_Update_All_Modules_file(main_dir:Path):
    path = main_dir / "Project_Update_All_Modules.ipynb"
    try:
        with open(path,"x") as f:
            f.write('''{
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Update all modules",
                ""
            ]
        },
        {
            "cell_type": "code",
            "execution_count": null,
            "metadata": {},
            "outputs": [],
            "source": [
                "%pip install -r requirements.txt",
                "%pip freeze > requirements.txt",
                ""
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
    }''')
            f.close()
        print(f"+\"{path.name}\" was created")
    except FileExistsError:
        print(f"-\"{path.name}\" already exists")   
    return