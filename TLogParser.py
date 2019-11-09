import subprocess
import pandas as pd
import os


def is_tlog(string):
    if string.find(".tlog") == -1:
        return False
    else:
        return True


def tlog2csv(fl_file):
    fl_file.save("static/tmp/" + fl_file.filename)
    p = subprocess.Popen(["java", "-jar", "TLogToCSV.jar", "static/tmp/test.tlog"],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()


def parser(fl_file):

    status = 0

    tlog2csv(fl_file)
    new_str = ''
    params_list = []
    with open("static/tmp/test.csv", "r") as f:
        for line in f:
            if line.find('CAMERA') != -1:
                new_str += line

    lines = new_str.split("\n")
    lines = lines[:-1]
    for ii, line in enumerate(lines):
        l = line.find("lat")
        r = line.find("cam_idx")
        line = line[l:r-1]
        line = line.split()
        item_params = {}
        for idx, param in enumerate(line):
            param = param.split(":")

            if param[0] == 'lng' or param[0] == 'lat':
                param[1] = param[1][:2] + "." + param[1][2:]
            item_params[param[0]] = float(param[1])

            # print("PARAM", param[0])
        real_item = {"height": abs(item_params['alt_rel']), "center": (item_params['lng'], item_params['lat']), "pitch": item_params['yaw'], "foc_len": item_params['foc_len'], "cam_h": 0.03, "cam_w": 0.04}
        if real_item["foc_len"] <= 0:
            status = 1
            real_item["foc_len"] = 0.0337
        params_list.append(real_item)
    return status, params_list


def csv_parser(file, cam_h=0.24, cam_w=0.04):

    file.save(os.path.join('static/uploads', file.filename))
    table = pd.read_csv(os.path.join('static/uploads', file.filename))
    table = table.to_numpy()
    result = []
    for row in table:
        item = {"height": abs(row[2]), "center": (row[1], row[0]), "pitch": row[3], "foc_len": row[4], "cam_h": cam_h, "cam_w": cam_w}
        result.append(item)
    return result



