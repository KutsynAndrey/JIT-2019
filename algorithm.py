import copy
import math
import random
import numpy as np
import time
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
	y_min = min(y_coords)
	y_max = max(y_coords)
	while y_min < y_max:
		y_coords.append(y_min)
		y_min += size[1]
	y_coords.sort()

	return y_coords

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

def convert_polygon(polygon_input):
	polygon = []
	for i in range(len(polygon_input)):
		polygon.append([])
		for point in polygon_input[i]:
			polygon[i].append(Point(point[0], point[1]))
	# for i in range(len(polygon)):
	# 	polygon[i].x *= 111 * 1000
	# 	polygon[i].y *= 111 * 1000

	return polygon

def equality(a, b):
	return abs(a - b) < 10 ** (-8)

def turn_polygon(polygon, radian):
	sin = math.sin(radian)
	cos = math.cos(radian)
	matrix = [[cos, -sin], [sin, cos]]

	for i in range(len(polygon)):
		for j in range(len(polygon[i])):
			polygon[i][j] = np.dot(matrix, [polygon[i][j].x, polygon[i][j].y])
			polygon[i][j] = Point(polygon[i][j][0], polygon[i][j][1])

	return polygon

def get_segments(polygon, size):
	# add all y coords
	y_coords = add_y_coords(size, polygon)
	# remove equal value
	y_coords = remove_elements(y_coords)

	# create dict
	# y_dict_vertex = these are x_coords of vertex in each y_coords
	# x_dict_segment = segments on each y_coords
	y_dict_vertex = {}
	x_dict_segment = {}
	# add vertex to each y_coords
	y_dict_vertex = add_vertex(y_dict_vertex, x_dict_segment, y_coords, polygon)
	result_segments = []

	for iterator, y in enumerate(y_coords):
		# print('Y=', y)
		if iterator == 0:
			# add new edges from the first vertex
			for vertex in y_dict_vertex[y]:
				vertex1 = (vertex.number + 1) % len(polygon[vertex.polygon])
				vertex2 = (vertex.number - 1) % len(polygon[vertex.polygon])
				x_dict_segment[y].append(Segment(polygon[vertex.polygon][vertex.number], polygon[vertex.polygon][vertex1], vertex.x))
				x_dict_segment[y].append(Segment(polygon[vertex.polygon][vertex.number], polygon[vertex.polygon][vertex2], vertex.x))

			result_segments.append(x_dict_segment[y])
		else:
			x_dict_segment[y] = copy.deepcopy(x_dict_segment[y_coords[iterator - 1]])
			# do step on the each edge
			for index, segment in enumerate(x_dict_segment[y]):
				segment.x = segment.edge.x0 + segment.edge.vector.x * ((y - segment.edge.y0) / segment.edge.vector.y)
			# delete edge if it him end and create new new from to other vertex
			remove_index = []
			for vertex in y_dict_vertex[y]:
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
				x_dict_segment[y].sort(key = lambda segment: segment.x)

			x_segment = []
			for index, el in enumerate(x_dict_segment[y]):
				if index not in remove_index:
					x_segment.append(x_dict_segment[y][index])
			x_dict_segment[y] = x_segment
			# print([segment.x for segment in x_segment])

	# result_segments = {}
	# coords_y = []
	# for i in range(len(y_coords)):
	# 	if (y_coords[i] - y_coords[1]) % size[1] == 0:
	# 		coords_y.append(y_coords[i])
	# 		result_segments[y_coords[i]] = x_dict_segment[y_coords[i]]

	return [x_dict_segment, y_coords]

def get_coords(segments, size, y_coords, y_coords_vertex):
	coords_photo = {}
	for j in range(1, len(y_coords)):
		cur_y = y_coords[j] - size[1] / 2.
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
		count = 0
		result = 0
		c = 0
		if j == 3:
			print('Y:', cur_y)
			print(coords)
		for i in range(len(coords)):
			# if coords[i][1]:
			# 	count += 1
			# 	if count == 1:
			# 		coords_photo[cur_y].append(coords[i][0])
			# else:
			# 	count -= 1
			# 	if count == 0:
			# 		coords_photo[cur_y].append(coords[i][0])
			# 	if count < 0:
			# 		count = 0
			if c and i:
				result += (coords[i][0] - coords[i - 1][0]);
			if coords[i][1]:
				c += 1
				if j == 3:
					print(coords[i][0])
			else:
				if c != 0:
					c -= 1
		if j == 3:
			# print(coords_photo[cur_y])
			print(result)
	return coords_photo

def algorithm():
	#Coords of polygon without last element(it is exactly first)
	# polygon_input = [[-91.87083756449519, 42.76116131487211], [-91.86988936752181, 42.76069720847619],
	# 			[-91.8687641737798, 42.76086428717932], [-91.86827111135369, 42.7612355715728],
	# 			[-91.86947216085335, 42.76148618728021], [-91.86849867862757, 42.76210808113947],
	# 			[-91.86975029863248, 42.761773929991506], [-91.87028761025014, 42.762108080995546],
	# 			[-91.87131482363858, 42.76191780073228], [-91.870562587373, 42.76163469974355]]
	# polygon_input = [[[3, 1], [2, 4], [4, 6], [5, 4], [6, 3]]]
	polygon_input = [[[4, 1], [2, 3], [3, 6], [4, 4], [6, 8], [8, 3], [11, 5], [12, 3]]]
	size = [2, 1]

	# convert polygon to comfortable use
	polygon_input = convert_polygon(polygon_input)
	y_coords_vertex = add_y_vertex(polygon_input)
	for i in range(1):
		# radian = random.uniform(-math.pi, math.pi)
		# polygon = turn_polygon(polygon_input, radian)
		segments, y_coords = get_segments(polygon_input, size)
		coords = get_coords(segments, size, y_coords, y_coords_vertex)
		# print(radian)

algorithm()