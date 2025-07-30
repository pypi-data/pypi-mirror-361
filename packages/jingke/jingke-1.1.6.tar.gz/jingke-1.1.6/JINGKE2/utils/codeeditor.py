import os
class Writer:
    def pycreate(path):
        file = 'main.py'
        dir_list = os.listdir(path)
        print(dir_list) 
        with open(os.path.join(path, file), 'w') as fp:
            pass 
        dir_list = os.listdir(path)
    
    def writeCode(code, path):
        file = 'main.py'
        with open(os.path.join(path, file), 'w') as fp:
            fp.write(code)
     
    