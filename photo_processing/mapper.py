import numpy as np
import cv2
import math


def crop_polygon(points, img):
    print(points, points.shape, type(points))
    rect = cv2.boundingRect(points)
    x, y, w, h = rect
    crop = img[y:y + h, x:x + w].copy()

    points = points - points.min(axis=0)

    mask = np.zeros(crop.shape[:2], np.uint8)
    cv2.drawContours(mask, [points], -1, (255, 255, 255), -1, cv2.LINE_AA)

    dst = cv2.bitwise_and(crop, crop, mask=mask)
    return dst


def fill_polygon(points, img, color):
    mask = np.zeros(img.shape[:2], np.uint8)
    mask = 255 - mask
    cv2.drawContours(mask, [points], -1, color, -1, cv2.LINE_AA)

    result = cv2.bitwise_and(img, img, mask=mask)

    return result


def check_border(d1, d2, t):
    return (d2[0] - d1[0]) * (t[1] - d1[1]) - (d2[1] - d1[1]) * (t[0] - d1[0]) > 0


def intersect(d1, d2, t1, t2):
    A = d1[1] - d2[1]
    B = d2[0] - d1[0]
    C = d1[0] * d2[1] - d2[0] * d1[1]
    A1 = t1[1] - t2[1]
    B1 = t2[0] - t1[0]
    C1 = t1[0] * t2[1] - t2[0] * t1[1]

    y = (A * C1 - C * A1) / (B * A1 - A * B1)
    x = (C1 * B - C * B1) / (A * B1 - A1 * B)
    return [x, y]


def clip(mainPoly, windowPoly):
    outputPoly = mainPoly

    for i in range(0, len(windowPoly)):

        if not i:
            wv2 = windowPoly[0]
            wv1 = windowPoly[-1]
        else:
            wv2 = windowPoly[i]
            wv1 = windowPoly[i - 1]

        # print("clip..\nv1", wv1, "v2", wv2)
        inputList = outputPoly
        outputPoly = []

        for j in range(0, len(inputList)):

            if not j:
                mv2 = inputList[0]
                mv1 = inputList[-1]
            else:
                mv2 = inputList[j]
                mv1 = inputList[j - 1]

            # print("in vertexes", mv1, mv2)
            if check_border(wv1, wv2, mv1) and check_border(wv1, wv2, mv2):
                outputPoly.append(mv2)
            elif not check_border(wv1, wv2, mv1) and not check_border(wv1, wv2, mv2):
                pass
            elif check_border(wv1, wv2, mv1) and not check_border(wv1, wv2, mv2):
                outputPoly.append(intersect(wv1, wv2, mv1, mv2))
            elif not check_border(wv1, wv2, mv1) and check_border(wv1, wv2, mv2):
                outputPoly.append(intersect(wv1, wv2, mv1, mv2))
                outputPoly.append(mv2)
            # print("SAVED", outputPoly)
    return outputPoly


def rotate_image(mat, angle):

    height, width = mat.shape[:2]
    image_center = (width/2, height/2)

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    abs_cos = abs(rotation_mat[0,0])
    abs_sin = abs(rotation_mat[0,1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat


class DrPhoto:

    def __init__(self, photo, kwargs):
        self.photo = photo
        self.HEIGHT = kwargs['height']
        self.center = kwargs['center']
        self.cam_height = kwargs['cam_h']
        self.cam_width = kwargs['cam_w']
        self.focal_length = kwargs['foc_len']
        self.photo_width = self.cam_width * self.HEIGHT / self.focal_length
        self.photo_height = self.cam_height * self.HEIGHT / self.focal_length
        self.angle = kwargs['pitch'] * (math.pi / 180.0)
        self.Rcenter = (self.center[0] * 111000, self.center[1] * 111000)
        self.ppmX = photo.shape[1] / self.photo_width
        self.ppmY = photo.shape[0] / self.photo_height
        self.photo = rotate_image(photo, kwargs['pitch'])
        self.RB = None
        self.RT = None
        self.LB = None
        self.LT = None

    def change_ppmX(self, ppm):
        sc = ppm / self.ppmX
        self.photo = cv2.resize(self.photo, None, fx=sc, fy=1.0)
        self.ppmX = ppm

    def change_ppmY(self, ppm):
        sc = ppm / self.ppmY
        self.photo = cv2.resize(self.photo, None, fx=1.0, fy=sc)
        self.ppmY = ppm

    def calcRealCoord(self):
        w = self.photo_width
        h = self.photo_height
        mx = self.Rcenter[0]
        my = self.Rcenter[1]
        tmpX = self.Rcenter[0] - w / 2
        tmpY = self.Rcenter[1] + h / 2
        self.LT = (mx + (tmpX - mx) * math.cos(self.angle) - (tmpY - my) * math.sin(self.angle),
                   my + (tmpX - mx) * math.sin(self.angle) + (tmpY - my) * math.cos(self.angle))

        tmpX = self.Rcenter[0] + w / 2
        tmpY = self.Rcenter[1] + h / 2
        self.RT = (mx + (tmpX - mx) * math.cos(self.angle) - (tmpY - my) * math.sin(self.angle),
                   my + (tmpX - mx) * math.sin(self.angle) + (tmpY - my) * math.cos(self.angle))

        tmpX = self.Rcenter[0] + w / 2
        tmpY = self.Rcenter[1] - h / 2
        self.RB = (mx + (tmpX - mx) * math.cos(self.angle) - (tmpY - my) * math.sin(self.angle),
                   my + (tmpX - mx) * math.sin(self.angle) + (tmpY - my) * math.cos(self.angle))

        tmpX = self.Rcenter[0] - w / 2
        tmpY = self.Rcenter[1] - h / 2
        self.LB = (mx + (tmpX - mx) * math.cos(self.angle) - (tmpY - my) * math.sin(self.angle),
                   my + (tmpX - mx) * math.sin(self.angle) + (tmpY - my) * math.cos(self.angle))

    def __repr__(self):
        print("DrPhoto\n",
              "latlon", self.center, "\n",
              "real_center", self.Rcenter, "\n",
              "fly_height", self.HEIGHT, "\n",
              "cam_h/cam_w", (self.cam_height, self.cam_width), "\n",
              "pitch", self.angle, "\n",
              "photo_width", self.photo_width, "\n",
              "photo_height", self.photo_height, "\n",
              "LeftBotReal", self.LB, "\n",
              "LeftTopReal", self.LT, "\n",
              "RightBotReal", self.RB, "\n",
              "RightTopReal", self.RT)
        return "*"


def DrList(img_list, params_list):
    maxX = -1e18
    minX = 1e18
    maxY = -1e18
    minY = 1e18
    minPPMx = 1e18
    minPPMy = 1e18
    maxPPMx = -1e18
    maxPPMy = -1e18

    dr_list = []
    PPM = {}
    for ii, img in enumerate(img_list):
        dr_img = DrPhoto(img, params_list[ii])
        dr_img.calcRealCoord()
        # print("Dr_image", ii, "\n", dr_img)

        maxX = max(maxX, dr_img.LB[0], dr_img.RB[0], dr_img.RT[0], dr_img.LT[0])
        minX = min(minX, dr_img.LB[0], dr_img.RB[0], dr_img.RT[0], dr_img.LT[0])
        maxY = max(maxY, dr_img.LB[1], dr_img.RB[1], dr_img.RT[1], dr_img.LT[1])
        minY = min(minY, dr_img.LB[1], dr_img.RB[1], dr_img.RT[1], dr_img.LT[1])

        minPPMx = min(minPPMx, dr_img.ppmX)
        minPPMy = min(minPPMy, dr_img.ppmY)
        maxPPMx = max(maxPPMx, dr_img.ppmX)
        maxPPMy = max(maxPPMy, dr_img.ppmY)

        dr_list.append(dr_img)

    PPM['maxX'] = maxPPMx
    PPM['maxY'] = maxPPMy
    PPM['minX'] = minPPMx
    PPM['minY'] = minPPMy

    return dr_list, maxX, minX, maxY, minY, PPM


class Map:

    def __init__(self, maxX, minX, maxY, minY, ppmX, ppmY):
        maxX -= minX
        maxY -= minY
        self.moveX = -minX
        self.moveY = -minY
        self.rw = maxX
        self.rh = maxY
        h = int(round(maxY * ppmY) + 1)
        w = int(round(maxX * ppmX) + 1)
        self.error = False
        print("D", h, w)
        try:
            self.map = np.zeros((h, w, 3), dtype=np.uint8)
            self.map_copy = np.zeros((h, w, 3), dtype=np.uint8)
        except MemoryError:
            self.error = True
        self.ppmX = ppmX
        self.ppmY = ppmY

    def add_image(self, img, rx, ry, copy=False):
        h, w = img.shape[:2]
        mh, mw = self.map.shape[:2]
        px, py = round((rx + self.moveX) * self.ppmX), round((ry + self.moveY) * self.ppmY)
        py = mh - py

        h_min = int(py - h // 2)
        h_max = int(py + h // 2)
        w_min = int(px - w // 2)
        w_max = int(px + w // 2)

        if h_min < 0:
            h_min = 0
        if w_min < 0:
            w_min = 0
        if h_max > self.map.shape[0]:
            h_max = self.map.shape[0]
        if w_max > self.map.shape[1]:
            w_max = self.map.shape[1]

        area = self.map[h_min:h_max, w_min:w_max]

        if area.shape != img.shape:
            # print("reshape from", img.shape, "to", area.shape)
            img = cv2.resize(img.copy(), (area.shape[1], area.shape[0]))
        if copy:
            self.map_copy[h_min:h_max, w_min:w_max] = np.where(img != [0, 0, 0], img, area)
        else:
            self.map[h_min:h_max, w_min:w_max] = np.where(img != [0, 0, 0], img, area)

    def check_intersecting(self, dri_n, dri2):

        h, w = self.map.shape[:2]
        answer = self.map_copy

        nLB = [dri_n.LB[0], dri_n.LB[1]]
        nLT = [dri_n.LT[0], dri_n.LT[1]]
        nRT = [dri_n.RT[0], dri_n.RT[1]]
        nRB = [dri_n.RB[0], dri_n.RB[1]]

        LB2 = [dri2.LB[0], dri2.LB[1]]
        LT2 = [dri2.LT[0], dri2.LT[1]]
        RT2 = [dri2.RT[0], dri2.RT[1]]
        RB2 = [dri2.RB[0], dri2.RB[1]]

        norm_points = [[nLB[0], nLB[1]], [nLT[0], nLT[1]], [nRT[0], nRT[1]], [nRB[0], nRB[1]]]
        for i in range(len(norm_points)):
            norm_points[i][0] = (norm_points[i][0] + self.moveX) * self.ppmX
            norm_points[i][1] = h - (norm_points[i][1] + self.moveY) * self.ppmY

        intersect_poly = clip([nRB, nRT, nLT, nLB], [RB2, RT2, LT2, LB2])

        print("list intersect", intersect_poly)
        if len(intersect_poly):

            for i in range(len(intersect_poly)):
                intersect_poly[i][0] = (intersect_poly[i][0] + self.moveX) * self.ppmX
                intersect_poly[i][1] = h - (intersect_poly[i][1] + self.moveY) * self.ppmY

            old_poly = crop_polygon(np.array(intersect_poly).astype("int32"), self.map)
            new_poly = crop_polygon(np.array(intersect_poly).astype("int32"), self.map_copy)

            old_blur_rate = cv2.Laplacian(old_poly, cv2.CV_64F).var()
            new_blur_rate = cv2.Laplacian(new_poly, cv2.CV_64F).var()
            print("RATE", old_blur_rate, new_blur_rate)
            if old_blur_rate > new_blur_rate:
                print("OLD THE BEST")
                dri_n.photo = fill_polygon(np.array(intersect_poly).astype("int32"), answer, (0, 0, 0))
                dri_n.photo = crop_polygon(np.array(norm_points).astype("int32"), dri_n.photo)
        return dri_n


def MapCreator(img_list, params_list, scale=1.0, ppm='min', update_blur=False):
    new_list = []
    for img in img_list:
        img = cv2.resize(img, None, fx=scale, fy=scale)
        new_list.append(img)

    dr_list, maxX, minX, maxY, minY, PPM = DrList(new_list, params_list)
    MAP = None

    if ppm == 'min':
        mPPMx = PPM['minX']
        mPPMy = PPM['minY']
        for ii, drimg in enumerate(dr_list):
            drimg.change_ppmX(mPPMx)
            drimg.change_ppmY(mPPMy)

        MAP = Map(maxX, minX, maxY, minY, mPPMx, mPPMy)

    elif ppm == 'max':
        mPPMx = PPM['maxX']
        mPPMy = PPM['maxY']
        for ii, drimg in enumerate(dr_list):
            drimg.change_ppmX(mPPMx)
            drimg.change_ppmY(mPPMy)

        MAP = Map(maxX, minX, maxY, minY, mPPMx, mPPMy)

    if MAP.error:
        return -1

    for ii, drimg in enumerate(dr_list):
        if update_blur:
            MAP.add_image(drimg.photo, drimg.Rcenter[0], drimg.Rcenter[1], True)
            for i in range(ii - 1, -1, -1):
                print("check_intersecting", ii, i)
                drimg = MAP.check_intersecting(drimg, dr_list[i])

        MAP.add_image(drimg.photo, drimg.Rcenter[0], drimg.Rcenter[1])
    return MAP


