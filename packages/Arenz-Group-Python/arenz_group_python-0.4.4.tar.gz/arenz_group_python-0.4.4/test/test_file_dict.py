

import os

from pathlib import Path 
#"import inc_dec    # "The code to test
import unittest   # The test framework

cwd = Path().cwd()
temp_dir = cwd /"TEMP_Project"
if not temp_dir.exists():
    temp_dir.mkdir()
os.chdir(temp_dir)

print("Current Work Dir:\n\t",temp_dir)
#######################################################################################
from arenz_group_python import save_dict_to_file, load_dict_from_file, save_dict_to_tableFile, open_dict_from_tablefile  # noqa: E402


keyValues_1= {
            "firstKey" : 5.23,
            "secondKey": "A string" ,
            "thridKey" :33
        }
        
keyValues_2= {
    "firstKey" : 511.23,
    "secondKey": "B string",
    "thridKey" :21 
        }




class test_file_dict(unittest.TestCase):
    
    def test_SaveLoad_File(self):
        
        print("CWD:\t",temp_dir, temp_dir.exists())
    
        file_path= temp_dir / "My_Dict_File.txt"

        

        save_dict_to_file(file_path,keyValues_1)
        self.assertTrue(file_path.exists)
        keyValues_B = load_dict_from_file(file_path)
        self.assertDictEqual(keyValues_1, keyValues_B)  
        
    def test_SaveLoad_TB(self):
        
        
        print("CWD:\t",temp_dir, temp_dir.exists())
        
        TB_file_path= temp_dir / "My_TB_File.txt"
        print("==Add sample 1")
        sample1 = "sample_name1"
        save_dict_to_tableFile(TB_file_path,"sample_name1", keyValues_1)
        self.assertTrue(TB_file_path.exists)
        print("==Add sample 2")
        sample2 = "sample_name2"
        save_dict_to_tableFile(TB_file_path,"sample_name2", keyValues_2)

        print("==Load File===")

        df = open_dict_from_tablefile(TB_file_path)
        
        list_names = [sample1,sample2]
        list_names_loaded = list(df.get("name"))
        self.assertListEqual(list_names,list_names_loaded)
        subdf = df.to_dict()
        print(df)
        
        
            

        
     
        
        
if __name__ == '__main__':
    unittest.main()
