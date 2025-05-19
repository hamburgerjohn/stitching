import pandas as pd
from tabulate import tabulate


def x_nom_column():
    
    column = []

    value = 0.0

    for i in range(0, 28):

        column.append(value)

        value -= 50.0

        if value < -300.0:
            value = 0.0

    return column

def y_nom_column():
    
    column = []

    value = 0.0

    for i in range(0, 28):

        if i % 7.0 == 0.0 and i > 0.0:
            value -= 40.0

        column.append(value)

    return column

def excel_dataframe():

    data_set = {
        "X Nominal" : x_nom_column(),
        "Y Nominal" : y_nom_column(),
        "X Measured" : [0.000]*28,
        "Y Measured" : [0.000]*28,
        "X Error" : [0.000]*28,
        "Y Error" : [0.000]*28,
        "X meas raw" : [0.000]*28,
        "Y meas raw" : [0.000]*28
    }

    pd_data_set = pd.DataFrame(data_set)

    return pd_data_set

def measured_relative(raw_data : list):

    control = raw_data[0]

    rel_column = []

    for line in raw_data:
        rel_column.append(control - line)

    return rel_column

def get_map_header(map_file : str, x_offset : str, y_offset : str):
    
    f = open(map_file, "r", encoding="UTF-8")

    header = []

    count = 0
    for line in f.readlines():

        if len(line) < 10:
            
            if count == 3:
                header.append(x_offset + '\n')
            
            elif count == 4:
                header.append(y_offset + '\n')

            else:
                header.append(line)

        count += 1

    f.close()

    return header
    

def excel_calc(x_raw : list, y_raw : list, map_file : str, x_offset : str, y_offset : str):

    data_set = excel_dataframe()

    data_set["X meas raw"] = x_raw
    data_set["Y meas raw"] = y_raw

    data_set["X Measured"] = measured_relative(x_raw)
    data_set["Y Measured"] = measured_relative(y_raw)

    data_set["X Error"] = data_set["X Measured"] - data_set["X Nominal"]
    data_set["Y Error"] = data_set["Y Measured"] - data_set["Y Nominal"]


    format_set = tabulate(data_set.values.tolist(), list(data_set.columns), tablefmt="plain", floatfmt=".3f")

    column_names = ""

    for c in format_set:
        column_names += c
        if c == '\n':
            break

        
    format_set = format_set.replace(column_names, "")
    
    header = get_map_header(map_file, x_offset, y_offset)

    f = open("vgOnLine.2dxymap", "w+", encoding="UTF-8")

    for line in header:
        f.write(line)

    f.write(format_set)


    f.close()



