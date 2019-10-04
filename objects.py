import collections.abc

def equality(a, b):
	if (a > 0 and b > 0) or (a < 0 and b < 0):
		return abs(abs(a) - abs(b)) < 10 ** (-4)
	return 0

class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __repr__(self):
		return "{}, {}".format(self.x, self.y)

class Vertex():
	def __init__(self, polygon, number, x):
		self.polygon = polygon
		self.number = number
		self.x = x

	def __repr__(self):
		return "{} ".format(self.number)

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

	def __lt__(self, other):
		if equality(self.x, other.x):
			return self.edge.vector.x * other.edge.vector.y - other.edge.vector.x * self.edge.vector.y < 10 ** (-8)
		return self.x < other.x

	def __repr__(self):
		return "SEGMENT: {}, {}, {}, {}, {}\n".format(self.x, self.edge.x0, self.edge.y0, self.edge.vector.x, self.edge.vector.y)

class TransformedDict(collections.abc.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        print(self.store)
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __lt__(self, other):
    	return len(self.store) < len(other.store)

    def __keytransform__(self, key):
        return key

class MyTransformedDict(TransformedDict):
    def __keytransform__(self, key):
        return round(key, 2)

    def __repr__(self):
    	return "{}".format(self.store)

    def get_path(self, start):
    	segments = self.store
    	path = [start]
    	for index, y in enumerate(segments.keys()):
    		coords = segments[y]
    		# print(coords)
    		if index % 2:
    			coords.reverse()
    		for point in coords:
    			path.append([point, y])
    	path.append(start)
    	return path