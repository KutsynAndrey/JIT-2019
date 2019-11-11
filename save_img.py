import shutil
import requests

def MapZoom(mx):
	if mx < 100: return 22
	if mx < 250: return 21
	if mx < 500: return 20
	if mx < 750: return 19
	if mx < 1500: return 18
	if mx < 2500: return 17
	if mx < 5000: return 16
	if mx < 12500: return 15
	if mx < 25000: return 14
	if mx < 50000: return 13
	if mx < 100000: return 12
	if mx < 200000: return 11
	if mx < 400000: return 10
	if mx < 750000: return 9
	if mx < 1500000: return 8
	if mx < 3000000: return 7
	if mx < 6500000: return 6
	if mx < 12500000: return 5
	if mx < 25000000: return 4
	if mx < 50000000: return 3
	if mx < 200000000: return 2
	if mx < 500000000: return 1
	if mx < 1000000000: return 0

def save_img(H = 1000, centers = [[-77.0397, 38.8974]]):
	H = int(H)
	zoom = MapZoom(H)
	print(zoom)
	# file_path = 'http://qnimate.com/wp-content/uploads/2014/03/images2.jpg'

	for i in range(len(centers)):
		center = centers[i]
		print(center)
		file_path = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{},{},{}/1200x900?access_token=pk.eyJ1Ijoib2xlemgiLCJhIjoiY2swZ3oxb2E3MDAzODNkdXY5NHN6NHl2biJ9.S64PvKhaqrlVk_7jVAOmdw'.format(center[0], center[1], zoom)
		file_name = 'static/drones_photos/{}.jpg'.format(i)

		save_file = requests.get(
				'{}'.format(file_path), stream = True)
		with open(file_name, 'wb') as out_file:
			shutil.copyfileobj(save_file.raw, out_file)

# save_img(1000, [[-91.87514029, 42.74966216]])