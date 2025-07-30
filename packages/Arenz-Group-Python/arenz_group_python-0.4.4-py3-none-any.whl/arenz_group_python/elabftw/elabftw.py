from pathlib import Path
import elabapi_python
import os
from arenz_group_python import Project_Paths
import warnings

EXPERIMENTS_API = elabapi_python.ExperimentsApi()
ITEM_API = elabapi_python.ItemsApi()
#api_client = elabapi_python.ApiClient()

API_KEY_NAME = 'elab_API_KEY'
API_HOST_URL = 'https://elabftw.dcbp.unibe.ch/api/v2'


class entry:
    def __init__(self, ID, path, title, uploads): 
        self.ID = ID
        self.path = path
        self.title = title
        self.uploads = len(uploads)

def fix_title(title):
    
    return str(title).replace(":", "-").replace("\\", "-").replace("/", "-").replace(" ", "_")




class elabFTW_wrapper:
    def __init__(self):
        self.connected = False
        self.api_client = None
        self.EXPERIMENTS_API = EXPERIMENTS_API
        self.API_HOST_URL = API_HOST_URL
        self.ITEM_API = ITEM_API
        
    def get_experiments_api(self):
        if self.isConnected():
            return EXPERIMENTS_API
        
    def isConnected(self):
        if not self.connected:
            print("Connection has not been established to the data base. Run 'connect' first.")
        return self.connected
    
    def connect_to_database(self, verify_ssl = False):
        
        API_KEY = os.getenv('elab_API_KEY')
        global API_HOST_URL
        url = os.getenv('elab_API_HOST')
        if url is not None:
            API_HOST_URL = url
            print(f"Using API_HOST_URL: {API_HOST_URL}")
        if API_KEY is None:
            raise ValueError("'elab_API_KEY' environment variable not set in '.env'.")
        if API_HOST_URL is None:
            raise ValueError("elab_API_HOST environment variable not set in '.env'.")  
        
    # Configure the api client
        configuration = elabapi_python.Configuration()
        configuration.api_key['api_key'] = API_KEY
        configuration.api_key_prefix['api_key'] = 'Authorization'
        configuration.host = API_HOST_URL
        configuration.debug = False
        configuration.verify_ssl = verify_ssl

        
        # For convenience, mask the warnings about skipping TLS verification
        if not configuration.verify_ssl:
            import urllib3
            urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

        # create an instance of the API class
        
        self.api_client = elabapi_python.ApiClient(configuration)
        # fix issue with Authorization header not being properly set by the generated lib
        self.api_client.set_default_header(header_name='Authorization', header_value=API_KEY)

        self.connected = True
        #### SCRIPT START ##################

        info_client = elabapi_python.InfoApi(self.api_client)
        api_response = info_client.get_info()
        if api_response is not None:
            print("Connected to DB.")
        # Load the experiments api
            global EXPERIMENTS_API 
            self.EXPERIMENTS_API = elabapi_python.ExperimentsApi(self.api_client)
            global ITEM_API
            self.ITEM_API = elabapi_python.ItemsApi(self.api_client)
            #print(EXPERIMENTS_API.api_client.configuration.host)
        
    
    
    def api_read_experiments(self, *args, **kwargs):
        """_summary_
            
            :param str q: Search for a term in title, body or elabid. 
        Returns:
            list: experiments
        """
        if self.isConnected():
            return self.EXPERIMENTS_API.read_experiments(**kwargs)

    def api_get_item_by_elabid(self,elabid,**kwargs):
        if self.isConnected():
            try:
                return self.ITEM_API.get_item(elabid, **kwargs)
            except elabapi_python.rest.ApiException as e:
                print(f"Error retrieving item with elabid {elabid}: {e}")
                return None

    def api_get_experiment(self,ID,**kwargs):
        if self.isConnected():
            return self.EXPERIMENTS_API.get_experiment(ID,**kwargs)
        else:
            return None
     
    def get_struct(self,ID,parentpath=Project_Paths().rawdata_path):
        if  self.isConnected():
            exp = self.api_get_experiment(ID)
            #entries.append(entry(exp.id, parentpath / exp.title, exp.title, exp.uploads))
            title =fix_title(exp.title)
            entries = [entry(exp.id, parentpath, title, exp.uploads)]
            for j in exp.related_experiments_links:
                if j.entityid != ID:
                    entries.extend(self.get_struct(j.entityid, parentpath / title ))
            return entries    
         
    def create_experiment_directory(self,experimentID:int, path_to_parentdir:Path):
        if self.isConnected():
            if isinstance(experimentID,int):
                exp = self.api_get_experiment(experimentID)
            else:
                exp = experimentID  
            path_to_dir = Path(path_to_parentdir) / fix_title(exp.title)
            if not path_to_dir.exists():
                os.makedirs(path_to_dir)
            return path_to_dir
        

    def download_experiment_info(self,experimentID, fileEnding,path_to_dir=Path.cwd(), DownLoad_Overwrite: bool = True):
        if self.isConnected():
            if isinstance(experimentID,int):
                exp = self.api_get_experiment(experimentID)
            else:
                exp =experimentID
            title = fix_title(exp.title)
            
            filename = f'{title}.{fileEnding}'
            if path_to_dir:
                path_to_dir = Path(path_to_dir)
                if not path_to_dir.exists():
                    os.makedirs(path_to_dir)
                    
            if path_to_dir:
                path_to_file  = Path(Path(path_to_dir) / filename)
            else:
                path_to_file = filename
            print(f'\t\tSaving file "{filename}"')
            if path_to_file.exists() and not DownLoad_Overwrite:
                print(f'\t\tFile {path_to_file.name} already exists. Skipping download.')
            else:
                with open(path_to_file, 'wb') as file:
                    # the _preload_content flag is necessary so the api_client doesn't try and deserialize the response
                    file.write(self.EXPERIMENTS_API.get_experiment(exp.id, format=fileEnding, _preload_content=False).data)
            

    def download_experiment_pdf(self,experimentID, path_to_dir=Path.cwd(),DownLoad_Overwrite: bool = True):
        return self.download_experiment_info(experimentID, "pdf", path_to_dir,DownLoad_Overwrite)
            
    def download_experiment_json(self,  experimentID, path_to_dir=Path.cwd(),DownLoad_Overwrite: bool = True):
        return self.download_experiment_info(experimentID, "json", path_to_dir,DownLoad_Overwrite)
        
###################################################################################################
    def download_experiment_dataFiles(self,experimentID, Path_To_Dir:Path, DownLoad_Overwrite:bool):
       

        if Path_To_Dir:
            path_to_dir = Path(Path_To_Dir)
            if not path_to_dir.exists():
                print(f'Create directory {path_to_dir} first')
                return
                
            ##############################   
            uploadsApi = elabapi_python.UploadsApi(self.api_client)

            # get experiment with ID 256
            #exp = self.api_get_experiment(experimentID)
            if isinstance(experimentID,int):
                exp = self.api_get_experiment(experimentID)
            else:
                exp =experimentID
              
            # upload the file 'README.md' present in the current folder
            # display id, name and comment of the uploaded files
            if len(exp.uploads) == 0:
                print('\t\tNo uploads found')
                return
            else:
                print(f'\t\tFound {len(exp.uploads)} uploads')
                index = 0
                for upload in uploadsApi.read_uploads('experiments', exp.id):
                    index = index+1
                    print("\t\t", index,"\t", upload.id, upload.real_name, upload.comment)
                    #get and save file
                    path_to_file = Path(path_to_dir / upload.real_name)
                    if path_to_file.exists() and DownLoad_Overwrite == False:
                        print(f'\t\tFile {path_to_file.name} already exists. Skipping download.')
                    else:
                        with open(path_to_file, 'wb') as file:
                            # the _preload_content flag is necessary so the api_client doesn't try and deserialize the response
                            file.write(uploadsApi.read_upload('experiments', exp.id, upload.id, format='binary', _preload_content=False).data)
        else:
            print('Directory not defined')
            return    
    

    def download_experiment_single(self,experimentID:int,path_to_parent: Path,DownLoad_Overwrite: bool):
        exp = self.api_get_experiment(experimentID)

        dir = self.create_experiment_directory(exp,path_to_parent )
        self.download_experiment_pdf(exp,dir, DownLoad_Overwrite)
        self.download_experiment_json(exp,dir, DownLoad_Overwrite)
        self.download_experiment_dataFiles(exp,dir, DownLoad_Overwrite)    
    
    def create_structure_and_download_experiments(self,experimentID,DownLoad_Overwrite: bool):
        
        experiment_structure = self.get_struct(experimentID, Project_Paths().rawdata_path)
        
        print("Found", len(experiment_structure), "experiments")
        for i,obj in enumerate(experiment_structure):
            path=Path(obj.path) / fix_title(obj.title)
            relpath = path.relative_to(Project_Paths().rawdata_path.parent.parent)
            print(f"----{i+1}/{len(experiment_structure)}------------------ID=", obj.ID, f"\t<Project>\\{relpath}")
            self.download_experiment_single(obj.ID,obj.path, DownLoad_Overwrite)

    def list_rel_experiment_to_item(self, itemID:int):
        item = self.ITEM_API.get_item(itemID)
        print(f"Related experiments to item ID{itemID} - {item.category_title}: {item.title}\n")
        entries = []
        for j in item.related_experiments_links:
            entries.append(entry(j.entityid, "", j.title, []))
               # if j.entityid != ID:
               #     entries.extend(self.get_struct(j.entityid, parentpath / title ))
            print(j.entityid, j.title)  

        return entries
        
    
    def download_rel_experiment_to_item(self, itemID: int, DownLoad_Overwrite: bool):
        entries = self.list_rel_experiment_to_item(itemID)
        
        #item = self.ITEM_API.get_item(itemID)
        for i,obj in enumerate(entries):
            print("---------------------------------------------------------------------------------")
            print(f"Experiment: {(1+i)} of {len(entries)} --- " , (obj.title))
            print("---------------------------------------------------------------------------------")
            self.create_structure_and_download_experiments(obj.ID, DownLoad_Overwrite)


