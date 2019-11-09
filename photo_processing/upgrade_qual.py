from photo_processing.functional import clear_folder, save_img_list, load_img_list, sort_by_var, get_metadata
from TLogParser import csv_parser, is_tlog, parser
from photo_processing.mapper import MapCreator


def photo_page_solution(listdir_im, listdir_so, img_improve, params_file, session):
    nothing = 'application/octet-stream'
    if listdir_im[0].content_type == nothing and listdir_so[0].content_type == nothing and img_improve.content_type == nothing:
        session["photos doesn't exist"] = True
        return 7, 0
    elif listdir_im[0].content_type != nothing and listdir_so[0].content_type != nothing:
        session["choose one operation"] = True
        return 3, 0
    elif listdir_im[0].content_type != nothing and img_improve.content_type != nothing:
        session["choose one operation"] = True
        return 3, 0
    elif img_improve.content_type != nothing and listdir_so[0].content_type != nothing:
        session["choose one operation"] = True
        return 3, 0
    elif params_file.content_type == nothing and not is_tlog(params_file.filename):
        session["params-list-doesn't-exist"] = True
        return 4, 0
    elif params_file.content_type != 'text/csv':
        session["upgrade-task-not-a-csv"] = True
        return 5, 0
    elif listdir_im[0].content_type != nothing:
        clear_folder("static/tmp-photos")
        clear_folder("static/uploads")
        save_img_list(listdir_im)
        param_list = csv_parser(params_file)

        if len(listdir_im) != len(param_list):
            session["count-file-img-error"] = True
            return 6, 0

        imlist = load_img_list("static/tmp-photos")
        result = MapCreator(imlist, param_list, s_img=True, fr=True, update_blur=True)
        return 0, result
    else:
        clear_folder("static/tmp-photos")
        save_img_list(listdir_so)
        imlist = load_img_list("static/tmp-photos")
        result = sort_by_var(imlist)
        return 0, result
