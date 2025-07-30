

from pathlib import Path
import inspect
import shutil

from .default_paths import PROJECT_FOLDERS
from .make_files import make_project_files,make_project_files_data

############################################################
############################################################
class Project_Paths:
    """
    # Class Project_Paths 
    the class can be used to more easily create the paths typically used in a project

        - "Project_Paths().cwd" to go get current working directory

        - "Project_Paths().data_rawdata" to go get rawdata directory

        - "Project_Paths().treateddata_path" to go get the treated data directory

    - create_project_structure( Path) to create a project folder tree. Note, it uses the executing notebook as root dir if no path is given
    
    """
    #def __new__(cls,*args, **kwargs):
        
    #######################################################################
    def _find_dir(self,path_to_caller: Path, dir_name:str) -> Path:
        
        path_to_dir = Path()
        if isinstance(path_to_caller, Path):  #make sure the path is a Path
            p = path_to_caller
        else:
            p = Path(path_to_caller)

        if (p / dir_name).exists():
            path_to_dir = p / dir_name   
        else:   
            parents_dir = p.parents
            
            for x in parents_dir:
                a = x / dir_name
                #print(a.is_dir(),"\t\t",str(a) )
                if a.is_dir():
                    path_to_dir = a
                    break
        if path_to_dir == Path():
            raise NotADirectoryError(f'\"{dir_name}\" could not be found as a branch of the folder tree form the notebook.\nPlease use standard project structure.\nProject_Paths().create_project_structure()\nfrom the root of the project.\n')
        return path_to_dir      

    ######################################################################################
    def _rawdata_path(self, path_to_caller : Path = Path.cwd() ) -> Path:
        """_summary_

        Args:
            path_to_caller (Path): _description_

        Returns:
            Path: Path to rawdata folder
        """
        p = path_to_caller
        k = Path()
        #print(PROJECT_FOLDERS.rawdata)
        if path_to_caller == Path(""):
            p = Path.cwd()
        try:
            k = self._find_dir(p, str(PROJECT_FOLDERS.rawdata))
            return k 
        except NotADirectoryError as err:
            print(err)
        
        
        #return Path(".") 
    
    ###############################################################################################
    def _treated_data_path(self, path_to_caller : Path = Path.cwd() ) -> Path:
        """_summary_

        Args:
            path_to_caller (Path): _description_

        Returns:
            Path: path to "treated_data" folder
        """
        try:
            k = self._find_dir(path_to_caller, str(PROJECT_FOLDERS.treated_data))
            return k 
        except NotADirectoryError as err:
            print(err)
        
        

    #################################################################################################
    def callers(self) -> str:
        caller_from = inspect.stack()[1]
        caller_filename_full = caller_from.filename
        return caller_filename_full

    #####################################################################
    def _current_working_dir(self)  -> Path:
        return Path.cwd()
    
    #####################################################################################################
    @property 
    def cwd(self)  -> Path:
        return self._current_working_dir() 
        
    ####################################################################################################
    @property 
    def rawdata_path(self)  -> Path:
        """return: the path to the folder for the raw data"""
        return self._rawdata_path()
    
    ##################################################################################################
    @property 
    def data_path(self)  -> Path:
        """return to data path"""
        return self._treated_data_path()
    
    @property 
    def treateddata_path(self)  -> Path:
        """return the path to the folder for the treated data"""
        return self._treated_data_path()
    
    ##################################################################################################
    def create_project_structure(self, project_path: Path =  Path.cwd() ):
        """The fx creates a standard folder structure for projects.

        Args:
            project_path (Path): Path to the base folder of the project. 
        """
        pp= Path(project_path)
        try:
            if not pp.exists():
                raise FileNotFoundError
        except FileNotFoundError:
            print("The path to the project is not correct, folder does not exist.")
            return
        
        for folderPath in PROJECT_FOLDERS:
            try:
                newFolder =  pp / folderPath
                newFolder.mkdir()
            except FileExistsError:
                print(f"-\"{folderPath}\" exists already as a folder")
            except FileNotFoundError:
                print("The path to the project is not correct.")
                return
        
        make_project_files( pp)
        make_project_files_data(pp) 
    ###############################################################    
    def find_dirs_with_tags(self, server_dir: Path, dirID: str , fileID:str ): 
        
        return find_dirs_with_tags( server_dir, dirID , fileID )
    
    def copyDirs(self, fileID:str , dirID: str = "" ,server_dir: Path = Path("X:/exp_db") ):
        """Copy all files from each folder and subfolder containing a file with the ending .tag
        to the raw data folder while keeping the folder structure.
        
        Args:
            fileID (str): project name, i.e name of tag-file.
            dirID (str): string to select only certain folders containing the string. Makes the crawling faster.
            server_dir (Path): path to server data base
            

        Returns:
            str: absolute path to the directory with a matching tag.
        """
        server_dir = _to_Path(server_dir)
        dirs = find_dirs_with_tags( server_dir, dirID , fileID )
        if len(dirs) != 0:
            dest_dirs = create_Folder_Structure_For_RawData(server_dir, self.rawdata_path, dirs)
            for i in range(len(dirs)):
                try:
                    ig = shutil.ignore_patterns("*.tag")
                    shutil.copytree(dirs[i], dest_dirs[i], dirs_exist_ok=True, ignore = ig)      
                except FileExistsError:
                    print("failed to copy:", dirs[i])
                    
        return 

#end of class ############################################################################   




#########################################################################################     
def find_dirs_with_tags( server_dir: Path, dirID: str , fileID:str ):
    """_summary_

    Args:
        server_dir (Path): path to server data base
        dirID (str): string to select only certain folders containing the string.
        fileID (str): project name, i.e name of tag-file.

    Returns:
        str: absolute path to the directory with a matching tag.
    """
    dirs_with_tags =[]
    fileID = fileID + ".tag"
    str_match = "*" + dirID + "*/" + fileID
    print("Pattern to look for:", str_match)
    if server_dir.is_dir() and server_dir.exists():
        print("Source Dir: ", server_dir)
        for root,dirs,files in server_dir.walk(on_error=print):
            for file in files: #look for tags
                file_p = root / file
                if file_p.match(str_match):
                    #print(file_p,"found tag")
                    if root not in dirs_with_tags:
                        dirs_with_tags.append(root)
    else:
        print("ERROR: The server path is not correct or server could not be found.")
        print("\t",server_dir)
    for dir in dirs_with_tags:
        print("\t",dir)
    if len(dirs_with_tags)== 0:
        print("ERROR: no project folders were found.")
    return dirs_with_tags  
##########################################################################################################################################
def create_Folder_Structure_For_RawData(server_dir: Path, dest: Path, dirs: list[Path]):
    """ 
    Creates folder tree in the destination folder

    Args:
        server_dir (Path): _description_
        dest (Path): _description_
        dirs (_type_): _description_
    """
    server_dir = _to_Path(server_dir)
    dest = _to_Path(dest)
    print("destination: ", dest, " exists: ", dest.exists())
    dest_dirs =[]
    if dest.exists(): #if the destination folder exists already
        for dir in dirs:
            dest_f = dest / dir.relative_to(dir.parent)
            dest_dirs.append(dest_f)
            if not dest_f.exists():
                print(f"\t.\\{dest_f.relative_to(dest)}","creating")
                #print (dir.parent)
                parent_folders =[]
                for i in range(6): 
                    if dest_f.parents[i].exists(): 
                        break
                    else:
                        parent_folders.insert(0,dest_f.parents[i])
                for parent in parent_folders:
                    dest_fp = dest / parent
                    try:
                        dest_fp.mkdir()
                    #print("\tmake a tree", dest_fp.relative_to(dest), dest_fp.exists())
                    except FileNotFoundError:
                        print(f"parent does not exist for {dest_fp}")
                try:
                    dest_f.mkdir()
                except FileNotFoundError:
                    print(f"parent does not exist for {dest_f}")
            else:
                print(f"\t.\\{dest_f.relative_to(dest)}", "exists")
    return dest_dirs

def _to_Path(path_to_caller):
    p = Path()
    if isinstance(path_to_caller, Path):  #make sure the path is a Path
        p = path_to_caller
    else:
        p = Path(path_to_caller)
    return p





pDATA_RAW = Project_Paths()._rawdata_path()
"""Pathlib Path to the project's "raw_data" folder.
"""
pDATA_TREATED = Project_Paths()._treated_data_path()
"""Pathlib Path to the project's "treated_data" folder.
"""
