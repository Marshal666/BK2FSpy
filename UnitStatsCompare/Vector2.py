import numpy as np

class Vector2:

	def __init__(self, x: np.float32, y: np.float32):
		self.value = np.array([x, y], dtype=np.float32)

	@property
	def x(self):
		return self.value[0]

	@x.setter
	def x(self, value):
		self.value[0] = np.float32(value)

	@property
	def y(self):
		return self.value[1]

	@y.setter
	def y(self, value):
		self.value[1] = np.float32(value)

	@property
	def magnitude(self):
		return np.sqrt((self.x ** 2) + (self.y ** 2))

	@property
	def magnitude_squared(self):
		return (self.x ** 2) + (self.y ** 2)

	@property
	def copy(self):
		return Vector2(self.x, self.y)

	def swap(self):
		self.value = np.array([self.y, self.x], dtype=np.float32)

	def normalize(self):
		self.value /= self.magnitude

	@staticmethod
	def direction_to_vector(dir: np.uint16):
		f_dir = np.float32((dir % 16384) / np.float32(16384.0))
		result = Vector2(1 - f_dir, f_dir)

		if dir < 16384:
			result.y = -result.y
			result.swap()
		elif dir < 32768:
			result.x = -result.x
			result.y = -result.y
		elif dir < 49152:
			result.x = -result.x
			result.swap()

		result.normalize()
		return result

	@staticmethod
	def zero():
		return Vector2(0, 0)

	@staticmethod
	def up():
		return Vector2(0, 1)

	@staticmethod
	def down():
		return Vector2(0, -1)

	@staticmethod
	def right():
		return Vector2(1, 0)

	@staticmethod
	def left():
		return Vector2(-1, 0)

	@staticmethod
	def s_triangle(p1, p2, p3) -> np.float32:
		return p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)

	@staticmethod
	def get_center_shift(dir, aabb_center):
		real_dir_vec = dir.copy
		dir_perp = Vector2(real_dir_vec.y, -real_dir_vec.x)
		return real_dir_vec * aabb_center.y + dir_perp * aabb_center.x

	def __add__(self, other):
		return Vector2(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return Vector2(self.x - other.x, self.y - other.y)

	def __mul__(self, other):
		if isinstance(other, np.float32) or isinstance(other, int) or isinstance(other, float):
			return Vector2(self.x * other, self.y * other)
		return Vector2(self.x * other.x, self.y * other.y)

	def __truediv__(self, other):
		if isinstance(other, np.float32) or isinstance(other, int) or isinstance(other, float):
			return Vector2(self.x / other, self.y / other)
		return Vector2(self.x / other.x, self.y / other.y)

	def __str__(self):
		return f'({self.x}, {self.y})'




