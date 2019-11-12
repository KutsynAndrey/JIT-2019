import copy
import math
import random
import numpy as np
from objects import *

def remove_elements(y_coords):
	remove_y_coords = []
	count_remove = 0
	for i in range(1, len(y_coords)):
		if equality(y_coords[i], y_coords[i - 1]):
			remove_y_coords.append(i - count_remove)
			count_remove += 1
	for i in remove_y_coords:
		del y_coords[i]

	return y_coords

def add_y_vertex(polygon):
	y_coords = []
	for i in range(len(polygon)):
		for vertex in range(len(polygon[i])):
			y_coords.append(polygon[i][vertex].y)
	return y_coords

def add_y_coords(size, polygon):
	y_coords = add_y_vertex(polygon)
	y_steps = []
	y_min = min(y_coords)
	y_max = max(y_coords)
	while y_min < y_max:
		y_coords.append(y_min)
		y_steps.append(y_min)
		y_min += size[1]
	y_coords.sort()
	y_steps.append(y_max)
	return [y_coords, y_steps]


def add_vertex(y_dict_vertex, x_dict_segment, y_coords, polygon):
	for el in y_coords:
		y_dict_vertex[el] = []
		x_dict_segment[el] = []
	for el in y_coords:
		for i in range(len(polygon)):
			for vertex in range(len(polygon[i])):
				if equality(polygon[i][vertex].y, el):
					y_dict_vertex[el].append(Vertex(i, vertex, polygon[i][vertex].x))
			y_dict_vertex[el].sort(key = lambda vertex: vertex.x)

	return y_dict_vertex

def convert_polygon(polygon_input, test = 1):
	polygon = []
	for i in range(len(polygon_input)):
		polygon.append([])
		for point in polygon_input[i]:
			polygon[i].append(Point(point[0], point[1]))
	
	if test == 0:
		for i in range(len(polygon)):
			for j in range(len(polygon[i])):
				polygon[i][j].x *= 111 * 1000
				polygon[i][j].y *= 111 * 1000

	return polygon

def convert_path(path):
	for i in range(len(path)):
		path[i][0] /= (111 * 1000)
		path[i][1] /= (111 * 1000)

	return path

def equality(a, b):
	if (a > 0 and b > 0) or (a < 0 and b < 0):
		return abs(abs(a) - abs(b)) < 10 ** (-4)
	return 0

def turn_polygon(polygon, radian):
	sin = math.sin(radian)
	cos = math.cos(radian)
	matrix = [[cos, -sin], [sin, cos]]

	for i in range(len(polygon)):
		for j in range(len(polygon[i])):
			polygon[i][j] = np.dot(matrix, [polygon[i][j].x, polygon[i][j].y])
			polygon[i][j] = Point(polygon[i][j][0], polygon[i][j][1])


	return polygon

def turn_dot(point, radian):
	sin = math.sin(radian)
	cos = math.cos(radian)
	matrix = [[cos, -sin], [sin, cos]]

	point = np.dot(matrix, point)
	return point

def valid_route(path, fly_loss, photo_loss, battery, fly_speed):
	# a * ((c * t) / 3600 + s) + (p * c) / 3600 = E
	# a - ток моторов(А)                 	fly_loss
	# c - количество фото				 	(len(path) - 2)
	# s - время полёта(в часах)			 	time
	# p - ток камеры(А)					 	photo_loss
	# t - время съёмки(const = 1 second) 	1

	s = 0
	for i in range(1, len(path)):
		x1 = path[i - 1][0]
		y1 = path[i - 1][1]
		x2 = path[i][0]
		y2 = path[i][1]
		s += math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
	# print('S:', s, 'SPEED:', fly_speed)
	fly_time = (s / fly_speed) / 3600
	E = fly_loss * ((len(path) - 2) / 3600 + fly_time) + photo_loss * (len(path) - 2)

	return [battery >= E, E, fly_time, s]

def get_segments(polygon, size):
	# add all y coords
	y_coords, y_steps = add_y_coords(size, polygon)
	# remove equal value
	y_coords = remove_elements(y_coords)

	# create dict
	# y_dict_vertex = these are x_coords of vertex in each y_coords
	# x_dict_segment = segments on each y_coords
	y_dict_vertex = MyTransformedDict()
	x_dict_segment = MyTransformedDict()
	# add vertex to each y_coords
	y_dict_vertex = add_vertex(y_dict_vertex, x_dict_segment, y_coords, polygon)

	for iterator, y in enumerate(y_coords):
		if iterator == 0:
			# add new edges from the first vertex
			for vertex in y_dict_vertex[y]:
				vertex1 = (vertex.number + 1) % len(polygon[vertex.polygon])
				vertex2 = (vertex.number - 1) % len(polygon[vertex.polygon])
				x_dict_segment[y].append(Segment(polygon[vertex.polygon][vertex.number], polygon[vertex.polygon][vertex1], vertex.x))
				x_dict_segment[y].append(Segment(polygon[vertex.polygon][vertex.number], polygon[vertex.polygon][vertex2], vertex.x))

		else:
			x_dict_segment[y] = copy.deepcopy(x_dict_segment[y_coords[iterator - 1]])
			# do step on the each edge
			for index, segment in enumerate(x_dict_segment[y]):
				x_dict_segment[y][index].x = segment.edge.x0 + segment.edge.vector.x * ((y - segment.edge.y0) / segment.edge.vector.y)
			# delete edge if it him end and create new new from to other vertex
			for vertex in y_dict_vertex[y]:
				remove_index = []
				for index, segment in enumerate(x_dict_segment[y]):
					vertex1 = (vertex.number + 1) % len(polygon[vertex.polygon])
					vertex2 = (vertex.number - 1) % len(polygon[vertex.polygon])
					if polygon[vertex.polygon][vertex1].y > polygon[vertex.polygon][vertex.number].y and polygon[vertex.polygon][vertex2].y > polygon[vertex.polygon][vertex.number].y:
						# it is a new vertex
						x_dict_segment[y].append(Segment(polygon[vertex.polygon][vertex.number], polygon[vertex.polygon][vertex2], vertex.x))
						x_dict_segment[y].append(Segment(polygon[vertex.polygon][vertex.number], polygon[vertex.polygon][vertex1], vertex.x))
						break
					if equality(segment.x, polygon[vertex.polygon][vertex.number].x):
						if polygon[vertex.polygon][vertex1].y > polygon[vertex.polygon][vertex.number].y:
							# it is a new edge
							x_dict_segment[y][index] = Segment(polygon[vertex.polygon][vertex.number], polygon[vertex.polygon][vertex1], vertex.x)
						elif polygon[vertex.polygon][vertex2].y > polygon[vertex.polygon][vertex.number].y:
							# it is a new edge
							x_dict_segment[y][index] = Segment(polygon[vertex.polygon][vertex.number], polygon[vertex.polygon][vertex2], vertex.x)
						else:
							# it are ends of two edge
							remove_index.append(index)
							remove_index.append(index + 1)
						break

				x_segment = []
				for index, el in enumerate(x_dict_segment[y]):
					if index not in remove_index:
						x_segment.append(x_dict_segment[y][index])
				x_dict_segment[y] = x_segment
			
			x_dict_segment[y].sort()

	return [x_dict_segment, y_steps]

def get_coords(segments, size, y_coords, y_coords_vertex):
	coords_photo = MyTransformedDict()
	# print("Y_MAX:", y_coords[-1])
	for j in range(1, len(y_coords)):
		cur_y = y_coords[j] - size[1] / 2.
		segment = []
		coords_photo[cur_y] = []
		y_ = [y_coords[j - 1], y_coords[j]]
		coords = []
		for y_coord in y_coords_vertex:
			if y_coord > y_coords[j - 1] and y_coord < y_coords[j]:
				y_.append(y_coord)
		for _y in y_:
			for i in range(len(segments[_y])):
				if i % 2 == 0:
					coords.append([segments[_y][i].x, 0])
				else:
					coords.append([segments[_y][i].x, 1])
		coords.sort()
		c = 0
		k = -1
		for i in range(len(coords)):
			if coords[i][1] == 0:
				c += 1
				if c == 1:
					k += 1
					segment.append([])
					segment[k].append(coords[i][0])
			else:
				if c != 0:
					c -= 1
					if c == 0:
						segment[k].append(coords[i][0])

		path = []
		for i in range(len(segment)):
			pointer = segment[i][0] + size[0] / 2.
			while pointer < segment[i][1]:
				coords_photo[cur_y].append(pointer)
				pointer += size[0]
			p = pointer - size[0]

			if segment[i][1] - p > size[0] / 2.:
				coords_photo[cur_y].append(segment[i][1])

	return coords_photo

def cycle(polygon_input, size, radian):
	polygon = turn_polygon(polygon_input, radian)
	y_coords_vertex = add_y_vertex(polygon)
	segments, y_steps = get_segments(polygon, size)
	coords = get_coords(segments, size, y_steps, y_coords_vertex)

	return [coords, radian]

def algorithm(polygon_input = [], size = [], start = [], fly_speed = 1, fly_loss = 0, photo_loss = 0, battery = 1):
	#Coords of polygon without last element(it is exactly first)
	# polygon_input = [[[4, 1], [2, 3], [3, 6], [4, 4], [6, 8], [8, 3], [11, 5], [12, 3]]]
	# print(polygon_input)
	# start = polygon_input[0][0]
	# size = [2, 1]

	# print('START..................................')
	result = []
	# convert polygon to comfortable use
	# print("POLYGON_BEFORE:", polygon_input)
	polygon_input = convert_polygon(polygon_input, 0)
	# print("POLYGON_AFTER:", polygon_input)
	# print("START_POINT:", start)
	# print('SIZE:', size)
	radian = 0
	result.append(cycle(polygon_input, size, radian))
	# for i in range(1):
	# 	radian = random.uniform(0, 2 * math.pi)
	# 	result.append(cycle(polygon_input, size, radian))

	for i in range(len(result)):
		segments, radian = result[i][0], result[i][1]
		path = segments.get_path(start)	
		result[i][0] = len(path)
		result[i].append(path)
	result.sort(key = lambda x: x[0])

	l, radian, path = result[0][0], result[0][1], result[0][2]
	# print('PATH_BEFORE:', path)
	for i in range(len(path)):
		path[i] = turn_dot(path[i], -radian)

	path = convert_path(path)
	path[0:0] = [start]
	path.append(start)
	valid, spent_battery, fly_time, length_route = valid_route(path, fly_loss, photo_loss, battery, fly_speed)

	if valid:
		# print('RADIAN:', radian, "LEN:", len(path))
		# print('PATH_AFTER:', path)

		return [1, path, radian, spent_battery, fly_time, length_route]
	return [0, [], 0, spent_battery, fly_time, length_route]

# algorithm()