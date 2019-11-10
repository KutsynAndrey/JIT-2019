import numpy as np
import cv2


def watering(img, minH = 40, maxH = 140):
	minH, maxH = minH / 2., maxH / 2.
	upper = np.array([minH], np.float32)
	lower = np.array([maxH], np.float32)
	legendH, legendV = 115, 255

	if img.shape[0] > 600 and img.shape[1] > 800:
		img = cv2.resize(img, (800, 600))


	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	h, s, v = cv2.split(hsv)
	h[h < minH] = 0
	h[h > maxH] = 0
	# convert to np.float32
	Z = h.flatten()
	# convert to np.float32
	Z = np.float32(Z)

	pixels = h.shape[0] * h.shape[1]

	# define criteria, number of clusters(K) and apply kmeans()
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
	K = 2

	result = 0

	while 1:
		ret, label, center=cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
		ans = hsv.copy()
		ans = ans.astype('float32')

		# Now convert back into uint8, and make original image
		center = np.uint8(center)
		res = center[label.flatten()]

		label = label.reshape((h.shape))
		label = np.array(label, np.float32)
		res = res.reshape((h.shape))
		res = cv2.merge([res, s, v])
		res = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)
		flag = 0

		for i in range(K):
			mask = np.array(np.where(label == i, label, 0), np.uint8)
			if np.count_nonzero(mask == 0) == h.shape[0] * h.shape[1]:
				mask = np.array(np.where(label == 0, label, 255), np.uint8)
				mask = 255 - mask
				mask = np.array(mask, np.uint8)
				mask[mask != 0] = 255
			else:
				mask = np.array(mask, np.uint8)
				mask[mask != 0] = 255
			im = cv2.bitwise_and(h, h, mask = mask)
			maskSum = np.sum(mask) / 255
			S = np.sum(im)
			if maskSum != 0:
				mean = S / maskSum
				print('MEAN:', mean)
				if mean == 0:
					procent = 0
				else:
					procent = 100 - 100 * ((mean - minH) / (maxH - minH))
			else:
				procent = 0

			if procent != 0:
				ans[mask != 0] = (legendH, procent * 2.55, legendV)

			if maskSum < pixels / 50.:
				flag = 1

		if flag:
			break

		K += 1

	ans = ans.astype('uint8')
	ans = cv2.cvtColor(ans, cv2.COLOR_HSV2BGR)

	return ans
