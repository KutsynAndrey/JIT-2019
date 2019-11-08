import cv2
import numpy as np
import imutils
import os


def show_var(img1, img2):
    #cv2.imshow("1", img1)
    #cv2.imshow("2", img2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def rotate_image(mat, angle):
    height, width = mat.shape[:2]
    image_center = (width / 2, height / 2)

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]

    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def partial_flv(img, kernel_size, step):
    variance_matrix = []
    border = int(kernel_size / 2)
    height, width = img.shape[0: 2]
    for h in range(border, height - border + 1, step):
        var_list = []
        for w in range(border, width - border + 1, step):
            cropped = cv2.getRectSubPix(img, (kernel_size, kernel_size), (w, h))
            variance = cv2.Laplacian(cropped, cv2.CV_64F).var()
            var_list.append([cropped, variance])
        variance_matrix.append(var_list)
    return variance_matrix


def flv_builder(img_list, kernel_size, step):
    height, width = img_list[0].shape[0:2]
    h_map, w_map = int((height - kernel_size) / step + 1), int((width - kernel_size) / step + 1)
    count = len(img_list)
    flv_list = []
    result_matrix = [[None for i in range(w_map)] for j in range(h_map)]

    for img in img_list:
        flv = partial_flv(img, kernel_size, step)
        flv_list.append(flv)

    for h in range(h_map):
        for w in range(w_map):
            index = -1
            m = -1
            for ii in range(count):
                variance = flv_list[ii][h][w][1]
                if variance > m:
                    m = variance
                    index = ii
            result_matrix[h][w] = flv_list[index][h][w][0]

    return result_matrix


def take_first(elem):
    return elem[0]


def sort_by_var(img_list):
    var_list = []
    for img in img_list:
        v = cv2.Laplacian(img, cv2.CV_64F).var()
        var_list.append((v, img))
    var_list.sort(key=take_first)
    return var_list[len(img_list)-1][1]


def supResStitcher(img_matrix):

    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()

    stitched_rows = []
    for ii, row in enumerate(img_matrix):
        (status, stitched) = stitcher.stitch(row)
        if status == 0:
            stitched = rotate_image(stitched, 90)
            stitched_rows.append(stitched)
        else:
            return 1

    for i in stitched_rows:
        cv2.imshow("test", i)
        cv2.waitKey(0)
    cv2.destroyAllWindows()
    status, result = stitcher.stitch(stitched_rows)
    result = rotate_image(result, -90)

    return result


def gridStitcher(img_matrix):
    rows_list = []
    for row_ii in range(len(img_matrix)):
        tmp = img_matrix[row_ii][0]
        for item_ii in range(1, len(img_matrix[row_ii])):
            tmp = np.concatenate((tmp, img_matrix[row_ii][item_ii]), axis=1)
        rows_list.append(tmp)
    result = rows_list[0]
    for row_ii in range(1, len(rows_list)):
        result = np.concatenate((result, rows_list[row_ii]), axis=0)
    return result


def load_img_list(path):
    listdir = os.listdir(path)
    img_list = []
    for item in listdir:
        img = cv2.imread(path + '/' + item)
        img_list.append(img)
    return img_list


def save_img_list(listdir):
    for item in listdir:
        item.save("static/tmp-photos/" + item.filename)


def clear_folder(path):
    listdir = os.listdir(path)
    for item in listdir:
        os.remove(path + '/' + item)


def photo_page_solution(listdir_im, listdir_so, img_improve, session):
    nothing = 'application/octet-stream'
    if listdir_im[0].content_type == nothing and listdir_so[0].content_type == nothing and img_improve.content_type == nothing:
        session["photos doesn't exist"] = True
        return 0, 0
    elif listdir_im[0].content_type != nothing and listdir_so[0].content_type != nothing:
        session["choose one operation"] = True
        return 3, 0
    elif listdir_im[0].content_type != nothing and img_improve.content_type != nothing:
        session["choose one operation"] = True
        return 3, 0
    elif img_improve.content_type != nothing and listdir_so[0].content_type != nothing:
        session["choose one operation"] = True
        return 3, 0
    elif listdir_im[0].content_type != nothing:
        clear_folder("static/tmp-photos")
        save_img_list(listdir_im)
        imlist = load_img_list("static/tmp-photos")
        flv_matrix = flv_builder(imlist, 80, 80)
        result = gridStitcher(flv_matrix)
        return 1, result
    else:
        clear_folder("static/tmp-photos")
        save_img_list(listdir_so)
        imlist = load_img_list("static/tmp-photos")
        result = sort_by_var(imlist)
        return 2, result
