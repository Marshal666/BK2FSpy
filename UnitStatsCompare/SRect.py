import numpy as np
from Vector2 import Vector2

class SRect:

	def __init__(self, center: Vector2, dir: Vector2, length_ahead: np.float32, length_back: np.float32, width: np.float32):
		self.center = center.copy
		self.dir = dir.copy
		dir = dir.copy
		dir.normalize()

		self.dir_perp = Vector2(-dir.y, dir.x)

		self.length_back = length_back
		self.length_ahead = length_ahead
		self.width = width

		point_back = center - dir * length_back
		point_forward = center + dir * length_ahead

		self.v1 = point_back - self.dir_perp * width
		self.v2 = point_back + self.dir_perp * width
		self.v3 = point_forward + self.dir_perp * width
		self.v4 = point_forward - self.dir_perp * width

	@staticmethod
	def from_length_width(center: np.array, dir: np.array, length: np.float32, width: np.float32):
		return SRect(center, dir, length, length, width)

	def is_point_inside(self, point: Vector2) -> bool:
		center = Vector2((self.v1.x + self.v2.x + self.v3.x + self.v4.x) / 4, (self.v1.y + self.v2.y + self.v3.y + self.v4.y + self.v4.y) / 4)
		right_sign = np.int16(np.sign(Vector2.s_triangle(self.v1, self.v2, center)))

		if right_sign == 0:
			return (point - center).magnitude_squared < np.float32(0.001)

		return (
				np.sign(Vector2.s_triangle(self.v1, self.v2, point)) == right_sign and
				np.sign(Vector2.s_triangle(self.v2, self.v3, point)) == right_sign and
				np.sign(Vector2.s_triangle(self.v3, self.v4, point)) == right_sign and
				np.sign(Vector2.s_triangle(self.v4, self.v1, point)) == right_sign)

	def compress(self, aabb_coef: np.float32):
		self.length_ahead *= aabb_coef
		self.length_back *= aabb_coef
		self.width *= aabb_coef
		self.__init__(self.center, self.dir, self.length_ahead, self.length_back, self.width)

	@staticmethod
	def get_unit_rect(aabb_half_size: Vector2, aabb_center: Vector2, dir: Vector2):
		length = aabb_half_size.x
		width = aabb_half_size.y

		rect = SRect.from_length_width(aabb_center + Vector2.get_center_shift(dir, aabb_center), dir, length, width)
		return rect
