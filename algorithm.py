import copy
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

def add_coords(y_coords, size):
	y_min = min(y_coords)
	y_max = max(y_coords)
	y_min += size[1] / 2.0
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
		for vertex in range(len(polygon)):
			if equality(polygon[vertex].y, el):
				y_dict_vertex[el].append(vertex)
		y_dict_vertex[el].sort()

	return y_dict_vertex

def convert_polygon(polygon_input):
	polygon = []
	for point in polygon_input:
		polygon.append(Point(point[0], point[1]))
	# for i in range(len(polygon)):
	# 	polygon[i].x *= 111 * 1000
	# 	polygon[i].y *= 111 * 1000

	return polygon

def equality(a, b):
	return abs(a - b) < 10 ** (-8)

def algorithm():
	#Coords of polygon without last element(it is exactly first)
	# polygon_input = [[-91.87083756449519, 42.76116131487211], [-91.86988936752181, 42.76069720847619],
	# 			[-91.8687641737798, 42.76086428717932], [-91.86827111135369, 42.7612355715728],
	# 			[-91.86947216085335, 42.76148618728021], [-91.86849867862757, 42.76210808113947],
	# 			[-91.86975029863248, 42.761773929991506], [-91.87028761025014, 42.762108080995546],
	# 			[-91.87131482363858, 42.76191780073228], [-91.870562587373, 42.76163469974355]]
	polygon_input = [[3, 1], [2, 4], [4, 6], [5, 4], [6, 3]]
	size = [2, 1]

	# convert polygon to comfortable use
	polygon = convert_polygon(polygon_input)
	# y coords of the vertexs
	y_coords = [polygon[i].y for i in range(len(polygon))]
	# add other coords
	y_coords = add_coords(y_coords, size)
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
	# check each y_coords
	last_y = y_coords[0]
	for iterator, y in enumerate(y_coords):
		# print('Y: ', y)
		if iterator == 0:
			# add new edges from the first vertex
			for vertex in y_dict_vertex[y]:
				vertex1 = (vertex + 1) % len(polygon)
				vertex2 = (vertex - 1) % len(polygon)
				x_dict_segment[y].append(Segment(polygon[vertex], polygon[vertex1], polygon[vertex].x))
				x_dict_segment[y].append(Segment(polygon[vertex], polygon[vertex2], polygon[vertex].x))

			result_segments.append(x_dict_segment[y])
		else:
			x_dict_segment[y] = copy.deepcopy(x_dict_segment[y_coords[iterator - 1]])
			# do step on the each edge
			for index, segment in enumerate(x_dict_segment[y]):
				x_dict_segment[y][index].x = x_dict_segment[y][index].edge.x0 + x_dict_segment[y][index].edge.vector.x * ((y - x_dict_segment[y][index].edge.y0) / x_dict_segment[y][index].edge.vector.y)
			# delete edge if it him end and create new new from to other vertex
			remove_index = []
			for vertex in y_dict_vertex[y]:
				for index, segment in enumerate(x_dict_segment[y]):
					if equality(segment.x, polygon[vertex].x):
						vertex1 = (vertex + 1) % len(polygon)
						vertex2 = (vertex - 1) % len(polygon)
						# print(vertex1, vertex2)
						if polygon[vertex1].y > polygon[vertex].y and polygon[vertex2].y > polygon[vertex].y:
							# it is a new vertex
							x_dict_segment[y].append(Segment(polygon[vertex1], polygon[vertex], polygon[vertex].x))
							x_dict_segment[y].append(Segment(polygon[vertex2], polygon[vertex], polygon[vertex].x))
						elif polygon[vertex1].y > polygon[vertex].y:
							# it is a new edge
							x_dict_segment[y][index] = Segment(polygon[vertex], polygon[vertex1], polygon[vertex].x)
						elif polygon[vertex2].y > polygon[vertex].y:
							# it is a new edge
							x_dict_segment[y][index] = Segment(polygon[vertex], polygon[vertex2], polygon[vertex].x)
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

	result_segments = {}
	for i in range(len(y_coords)):
		if (y_coords[i] - y_coords[1]) % size[1] == 0:
			result_segments[y_coords[i]] = x_dict_segment[y_coords[i]]
	for y in result_segments:
		print('Y=', y, [segment.x for segment in result_segments[y]])
	# for y in result_segments:
	# 	for i in range(len(result_segments[y])):
	# 		if i % 2 == 0:


algorithm()