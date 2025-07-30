from pathlib import Path
import sys
    
def add_path_to_local_module():

    p = Path.cwd()
    #print(p)
    for p in Path.cwd().parents:
        pa = p / "src"
        if pa.exists():
            #print(pa)
            if pa in sys.path:
                print("path already add", pa) 
                pass 
            #sys.path
            else:
                sys.path.insert(0,str(pa))
                print("path was added")
            break
 