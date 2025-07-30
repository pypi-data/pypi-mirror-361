
import csv
from pathlib import Path
from ..project.util_paths import Project_Paths
import re


DELIMITER = '\t'




def save_key_values(file_path:Path, sample_name:str, properties:list, delimiter:str=DELIMITER):
    """Saves key values into a csv. The function add a row, or replace an existing row based on the 
    sample name. The first column will always sample name. The following columns will be the list values.

    Args:
        file_path (Path): Path to data file or relative path
        sample_name (str): Name of sample, will be the first column of the row.
        properties (list): List of values to be stored on the same row

    """
    if file_path == "":
        print( "empty path ")
        return False
    p = file_path
    if isinstance(file_path,str):
        p = Path(file_path)
    if not p.is_absolute():
        pa = Project_Paths()._treated_data_path()
        pa = Path(str(Project_Paths()._treated_data_path()))
        #print(pa)
        p= pa.joinpath(p)

    
    all_data =[]
    sample = "\"" + sample_name + "\""
    new_row = [sample] + properties
    sample_already_in_dataset= False
    #print(p)
    #read in the whole file and check each row.
    if p.exists:    
        with open(p, 'r', newline='') as csvfile:
            #reads the file
            spamreader = csv.reader(csvfile, delimiter=DELIMITER, quotechar='|')

            all_data =[]
            i=0
            sample_already_in_dataset = False
            for row in spamreader:
                all_data.append(row)
                sa = re.search(sample_name, row[0])
                if sa :
                    print("sample name found -  updating row")
                    all_data[i] = new_row
                    sample_already_in_dataset= True
                i+=1
            if not sample_already_in_dataset:
                print("sample not found -  adding row")
                all_data.append(new_row)
            csvfile.close()   
    else:
        print("new file.")
        all_data.append(new_row)

    #print(all_data) 
    with open(p, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=DELIMITER,
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in all_data:
            spamwriter.writerow(row) #row
        csvfile.close()
    print(p)
    return
                