from elabapi_python.rest import ApiException

#import elabftw.elabftw
from .elabftw import API_KEY_NAME

from .elabftw import elabFTW_wrapper
from arenz_group_python import Project_Paths

ELAB = elabFTW_wrapper()



def connect(verify_ssl: bool = True):
    """Connect to the database.

    Args:
        verify_ssl (bool, optional): _description_. Defaults to True.
    """
    #from .elabftw import connect_to_database
    ELAB.connect_to_database(verify_ssl)
   
    
def get_experiment_api():
    return ELAB.get_experiments_api()

def get_item(ID_value:int):
    """Get project ID

    Args:
        ID_value (int): item identifier

    Returns:
        tuplet: project
    """
    if  ELAB.isConnected():
        return ELAB.api_get_item_by_elabid(ID_value)  # scope=3 for all projects

def download_experiment(ID_value:str|int, create_Tree = True, DownLoad_Overwrite: bool = False):
    """Download all experimental information and saves it into data_raw folder.
        A tree of all linked experiments can also be created.

    Args:
        ID_value (str, optional): experiment ID number as an interger, or as a string: ex. "ATS-JF060".
        create_Tree (bool, optional): download all associated experiments too. Defaults to True.
    """
    try:
        if ELAB.isConnected():
            ID = None
            if isinstance(ID_value,int):
                ID = ID_value 
            else:  
                    
                ID = get_experiment_ID(ID_value)
            
            if create_Tree:
                download_experiment_tree(ID)
            else:
                ELAB.download_experiment_single(ID, Project_Paths().rawdata_path, DownLoad_Overwrite)
                return
    except  ValueError as e:
        print("Experiment not found.")
        
def read_experiments(**kwargs) -> list:
    """read information about experiments
    
    use keywords.
    
    :param str q: Search for a term in title, body or elabid. \n
    :param str extended: Extended search (advanced query). 
    :param int related: Look only for entries linked to this entry id. 
    :param str related_origin: When using the \"related\" query parameter, select the type of the related ID (experiments or items) 
    :param str cat: Add a filter on the Category. Supports comma separated list of numbers, including \"null\". 
    :param str status: Add a filter on the Status. Supports comma separated list of numbers, including \"null\". 
    :param list[str] tags: An array of tags for filtering results containing all of these tags. 
    :param int limit: Limit the number of results. 
    :param int offset: Skip a number of results. Use with limit to work the pagination. 
    :param str owner: Filter results by author (user id) 
    :param int scope: Set the scope for the results. 1: self, 2: team, 3: everything. It defaults to the user value stored in preferences. 
    :param str order: Change the ordering of the results. 
    :param str sort: Change the sorting of results: ascending or descending. 
    :param str state: Filter results based on their state: 1 (Normal), 2 (Archived), 3 (Deleted). Supports comma separated values. 
        :return: list[Experiment]
                 If the method is called asynchronously,
                 returns the request thread.

    Returns:
        list: experiment info
    """
    if ELAB.isConnected():
        return ELAB.api_read_experiments(**kwargs)
     
    
def download_experiment_tree(ID,DownLoad_Overwrite: bool = False):
    """
    Get the experiment with the given ID from the eLabFTW database and save it to the rawdata folder.
    
    Parameters
    ----------
    ID : str
        The ID of the experiment to retrieve. Use ID as an integer or a string (e.g., "ATS-JF060").
    
    Returns
    -------
    None
    """
    #from .elabftw import create_structure_and_download_experiments
    try:
        ELAB.create_structure_and_download_experiments(ID,DownLoad_Overwrite)
    except ApiException as e:
        if e.status == 404:
            print(f"Experiment with ID {ID} not found. error 404")
        elif( e.status == 401):
            print(f"The API key is not correct. Check your .env file for '{API_KEY_NAME}'-key . error 401")
        else:
            print(f"An error occurred: {e}")


def list_item(ID_value:int):
    """Download a project. Thereby, downloading all experimental information and saves it into data_raw folder.
        A tree of all linked experiments can also be created.

    Args:
        ID_value (str, optional): experiment ID number as an interger, or as a string: ex. "ATS-JF060".
        create_Tree (bool, optional): download all associated experiments too. Defaults to True.
    """
    #from .elabftw import download_experiment
    ELAB.list_rel_experiment_to_item(ID_value)

def download_experiment_rel_to_item(ID_value:int,DownLoad_Overwrite: bool = False):
    """Download all experiments related to a project. Thereby, downloading all experimental information and saves it into data_raw folder.
        A tree of all linked experiments can also be created.

    Args:
        ID_value (str, optional): experiment ID number as an interger, or as a string: ex. "ATS-JF060".
        DownLoad_Overwrite (bool, optional): Files are only downloaded if not found on disk. Defaults to False.
    """
    #from .elabftw import download_experiment
    ELAB.download_rel_experiment_to_item(ID_value, DownLoad_Overwrite)

            
def get_experiment(ID_value,**kwargs):
    """Get experiment ID

    Args:
        ID_value (str | int): experiment identifier

    Returns:
        tuplet: experiment
    """
    if  ELAB.isConnected():
        if isinstance(ID_value,int):
            ID = ID_value
        else:
            ID = get_experiment_ID(ID_value)
        #from .elabftw import api_get_experiment
        return ELAB.api_get_experiment(ID,**kwargs)

def get_experiment_ID(ID_name):
    """Get experiment ID

    Args:
        ID_name (str): experiment identifier

    Returns:
        int: experiment id number
    """
    if  ELAB.isConnected():
        list_result = ELAB.api_read_experiments(q=ID_name)
        if list_result:
            for item in list_result:
                title = str(item.title).split()
                if title[0].casefold() == str(ID_name).casefold():
                    return int(item.id)
        return None