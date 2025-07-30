

import os

from pathlib import Path 
#"import inc_dec    # "The code to test
import unittest   # The test framework

cwd = Path().cwd()
temp_dir = cwd /"TEMP_Project"
if not temp_dir.exists():
     temp_dir.mkdir()
os.chdir(temp_dir)
#######################################################
from arenz_group_python.project import Project_Paths as pp

class test_Project_Paths(unittest.TestCase):
    
    def test_projectPath(self):
        print(Path().cwd())
        try:
            temp_dir.mkdir()
        except FileExistsError:
            print(f"-\"{temp_dir}\" exists already as a folder")
        except FileNotFoundError:
            print("The path to the project is not correct")
            
        self.assertTrue(temp_dir.is_dir)
        self.assertTrue(temp_dir.exists)
        self.assertTrue((temp_dir / ".env").exists)
        pp().create_project_structure(temp_dir)
        self.assertTrue(str(temp_dir),"b")
        
        
        
        
    
        
     
        
        
if __name__ == '__main__':
    unittest.main()
