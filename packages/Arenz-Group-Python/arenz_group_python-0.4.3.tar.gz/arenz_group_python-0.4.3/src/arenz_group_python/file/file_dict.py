from pathlib import Path
from ..data_treatment.util import Quantity_Value_Unit as Q
import pandas as pd
import warnings


DELIMITER = '\t'


def save_dict_to_file(file_path:Path, kw: dict):
    """Saves a dict to text file

    Args:
        file_path (Path): _description_
        kw (dict): _description_
    """
    with open(file_path, 'w') as file:
        for k,v in kw.items():
            file.writelines(f"{k} = {v}\n")    
        file.close
    return 

def load_dict_from_file(file_path:Path):
    """Reads a dict from file.
    I.e. the assumption is that each line looks like:
        my_int = 5\n
        my_float = 5.0\n
        my_quantity = 10.5 nm\n
        my_text = "a string" 

    Args:
        file_path (Path): to dict.

    Returns:
        dict: the dict from the file
    """
    k={}
    with open(file_path, 'r') as file:
        aa= True
        while(aa):
            a=  file.readline()
            if a == "":
                break
            else:
                k = string_to_dict(a, k)   
        file.close
    return k


###########################################################################################


def string_to_dict(s:str, k: dict):
    vals = s.split("=",1)
    if len(vals)>=2:
        key= str(vals[0]).strip().strip().replace("'","").replace('"',"").strip()
        v=vals[1].strip()
        try:
            k[key]=int(v)
        except ValueError:
            try:
                k[key]=float(v)
            except ValueError:
                try:
                    k[key]=Q(v)
                except:    
                    k[key] = vals[1].strip()
        #k[key] = vals[1].strip()    
    return k


def open_dict_from_tablefile(file_path:Path):
    """Opens a tablefile and returns a datafram.

    Args:
        file_path (Path)

    Returns:
        DataFrame: numpy data frame where each keyvalue is the column name.
    """
    df = pd.read_csv(file_path)
    for col in df.columns:
    #print(df[col].dtypes)
        for i in range(df.index.max()):
            if df[col].dtypes == object:
                o = df.iloc[i][col]
                try:
                    #print(df[col].dtypes,o,"fdsfsa",Q(o), "YES")
                    df.iloc[i][col]=Q(o)
                except:
                    print(df[col].dtypes,o,"", "no")
    return df

def save_dict_to_tableFile(file_path:Path, sample_name:str, properties:dict, delimiter:str=DELIMITER):
    """Saves key values into a csv. The function add a row, or replace an existing row based on the 
    sample name. The first column will always be called "name". The following columns will have the name of the key of the dict.

    Args:
        file_path (Path): Path to file
        sample_name (str): unique sample name. If name exist already, the raw will be overwritten.
        properties (dict): the dict to be saved.
        delimiter (str, optional): Defaults to DELIMITER.
    """
    file_path = Path(file_path)
    unique_key="name"
    if not file_path.exists():
        with open(file_path, 'w') as file:
            file.write(f"{unique_key}\n")    
        file.close
        print(f"File Path: {file_path}\n")
        print(f"File was created")
    try:    
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"File Path: {file_path}\n")
        print(f"File might be empty. Creating default header\n")
        print("")
        df = pd.DataFrame(columns=[unique_key])

    cols = list(df.columns)
    if(cols[0] != unique_key):
        df=df.rename(columns={cols[0]: unique_key})
        warnings.warn(f"The first column has been renamed to '{unique_key}'")

    properties[unique_key]=sample_name
    df = add_dict_to_DataFrame(df,properties)
    df.to_csv(file_path, index=False,sep=",")



def append_row(df, row):
    """Adds a row to a datafram

    Args:
        df (_type_): _description_
        row (_type_): _description_

    Returns:
        _type_: _description_
    """
    row =pd.Series(row)
    return pd.concat([
                df, 
                pd.DataFrame([row], columns=row.index)]
           ).reset_index(drop=True)


def add_dict_to_DataFrame(df, n:dict , key="name"):
    
    cols = list(df.columns)
    if(cols[0] != key):
        df = df.rename(columns={cols[0]: key})
        
    cols = list(df.columns)
    keyCol=cols[0]
    in_list =False
    row = 0
    for keyName in df.iloc[:,0]:
        if keyName == n[keyCol]:
            
            in_list = True
            break
        else:
            row=row+1
    #print(in_list,row)
    ## add:
    if not in_list:
        df = append_row(df, n)
        print( n[keyCol], "was added")
        #print(row)
    else:
        for colName in cols:
            df.at[row,colName] = n.get(colName,None)
        ex = {"name":[n["name"]]}
        for k,v in n.items():
            if k not in cols:
                ex[k] = [v]
        #print(ex)
        new_cols_data = pd.DataFrame.from_dict(ex)
        #print(new_cols_data)
        print(n[keyCol], "was already in the list: updating")
        df = df.join(new_cols_data.set_index(keyCol), on=keyCol)
    return df