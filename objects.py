class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Vector():
	def __init__(self, point_start, point_end):
		self.x = point_end.x - point_start.x
		self.y = point_end.y - point_start.y

class Edge():
	def __init__(self, point_start, point_end):
		self.x0 = point_start.x
		self.y0 = point_start.y
		self.vector = Vector(point_start, point_end)

class Segment():
	def __init__(self, point_start, point_end, x):
		self.x = x
		self.edge = Edge(point_start, point_end)