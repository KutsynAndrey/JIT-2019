import subprocess
import numpy as np
import pandas as pd
import os

def tlog2csv(fl_file):
    fl_file.save("/static/tmp/test.tlog")
    p = subprocess.Popen(["java", "-jar", "TLogToCSV.jar", "static/tmp/test.tlog"],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()


def parser(fl_file):

    tlog2csv(fl_file)
    new_str = ''
    params_list = []
    with open("static/tmp/test.csv", "r") as f:
        for line in f:
            if line.find('CAMERA') != -1:
                new_str += line

    lines = new_str.split("\n")
    for ii, line in enumerate(lines):
        l = line.find("lat")
        r = line.find("cam_idx")
        line = line[l:r-1]
        line = line.split()
        item_params = {}
        for idx, param in enumerate(line):
            param = param.split(":")
            item_params[param[0]] = float(param[1])
        params_list.append(item_params)
    return params_list


def csv_parser(file, cam_h=0.24, cam_w=0.04):
    file.save(os.path.join('static/uploads', file.filename))
    table = pd.read_csv(os.path.join('static/uploads', file.filename))
    table = table.to_numpy()
    result = []
    for row in table:
        item = {"height": row[2], "center": (row[1], row[0]), "pitch": row[3], "foc_len": row[4], "cam_h": cam_h, "cam_w": cam_w}
        result.append(item)
    return result



