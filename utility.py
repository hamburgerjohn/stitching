import re, os, sys, datetime
import numpy as np

def error(e):

    if e is None:
        print("-------------------------------------------------")
        print(f"Failed to Open File")
        print("-------------------------------------------------")

    else:
        print("-------------------------------------------------")
        print(f"Command failed with return code {e}")
        print("-------------------------------------------------")


def sortby_creation_date(files : list):

    files = sorted(files, key = lambda x: datetime.datetime.fromtimestamp(os.path.getctime(x)), reverse=True)

    files_dates = {}

    for file in files:
        files_dates.setdefault(file, datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime("%B %d, %Y - %H:%M:%S"))
    
    return files_dates


def get_file(file : str, drive : str):
    
    files_ = []

    for root, dir, files in os.walk(drive + ":\\"):
        for f in files:
            if f == file:
                files_.append(os.path.join(root, f))

    files_ = sortby_creation_date(files_)

    return files_

def read_txt(get_file : str):
    
    f = open(get_file, "r", encoding="UTF-8")

    data = []

    for line in f.readlines():


        line = [x for x in re.split(r"\s{2,}", line) if x != '' and x != '\n']

        if len(line) > 6:
            
            if "Measured" not in line:
                data.append(line[1])

    f.close()

    return [float(x) for x in data]

def get_current_drive():

    try:
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 

    except:
        print("Error getting drive of this exe")

    return exe_dir[0] 











    

    




