import cv2
import numpy as np

def obj_detection(im1, im2, threshold_value):
    if im1.shape != im2.shape:
        print("Different shapes!!!")
        exit(0)

    IMG_SCALE = 5
    IMG_RESIZE = 1 / IMG_SCALE

    MAX_VALUE = 127
    NEW_BORDER_COLOR = (0, 255, 0)
    MOVE_BORDER_COLOR = (0, 0, 255)

    h, w = im1.shape[:2]
    h1, w1 = h//IMG_SCALE, w//IMG_SCALE

    res_im1 = cv2.resize(im1, (w1, h1))
    res_im2 = cv2.resize(im2, (w1, h1))

    print(res_im1.shape)

    res_im1 = cv2.GaussianBlur(res_im1, (3, 3), cv2.BORDER_DEFAULT)
    res_im2 = cv2.GaussianBlur(res_im2, (3, 3), cv2.BORDER_DEFAULT)
    res_im1 = res_im1.astype('int16')
    res_im2 = res_im2.astype('int16')

    delta_img = np.subtract(res_im2, res_im1)
    delta_img = np.absolute(delta_img)
    delta_img = np.mod(delta_img, 255)

    delta_img = delta_img.astype('uint8')
    delta_img_gray = cv2.cvtColor(delta_img, cv2.COLOR_BGR2GRAY);
        

    im_result1 = im1.copy()
    im_result2 = im2.copy()
    
    # get contours of objects
    retval, threshold = cv2.threshold(delta_img_gray, threshold_value, MAX_VALUE, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    threshold[threshold != 0] = 255
    for i, ctr in enumerate(contours):
        x, y, w, h = [int(x * IMG_SCALE) for x in cv2.boundingRect(ctr)]

        # get mask of object from its bounding box
        maskBoundingRect = np.zeros((im1.shape[0], im1.shape[1]))
        poly = np.array([[[x, y], [x + w, y], [x + w, y + h], [x, y + h]]])
        cv2.fillPoly(maskBoundingRect, pts = poly, color=(255))
        maskBoundingRect = maskBoundingRect.astype('uint8')

        # bitwise img and mask
        res1 = cv2.bitwise_and(im1, im1, mask = maskBoundingRect)
        res2 = cv2.bitwise_and(im2, im2, mask = maskBoundingRect)
        res1, res2 = res1.astype('uint8'), res2.astype('uint8')

        # get object from original img
        obj1, obj2 = res1[y: y + h, x: x + w], res2[y: y + h, x: x + w]
        obj1, obj2 = obj1.astype('uint8'), obj2.astype('uint8')

        # get variance from Laplacian
        var1 = cv2.Laplacian(obj1, cv2.CV_64F).var()
        var2 = cv2.Laplacian(obj2, cv2.CV_64F).var()

        if var2 == 0:
            k = var1
        else:
            k = var1 / var2

        if k > 1.35:
            cv2.rectangle(im_result1, (x, y), (x + w, y + h), MOVE_BORDER_COLOR, 2)
        elif k < 0.7:
            cv2.rectangle(im_result2, (x, y), (x + w, y + h), NEW_BORDER_COLOR, 2)

    return [im_result1, im_result2]

# obj_detection()