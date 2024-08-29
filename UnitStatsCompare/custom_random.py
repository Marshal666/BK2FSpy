from random import Random
from Vector2 import Vector2
import numpy as np

rng: Random = Random()

def init_seed(seed: int):
	rng.seed(seed)

def random(max: int):
	return rng.randint(0, max - 1)

def random_float_01():
	return rng.random()

def rand_quadr_in_circle(dispersion: np.float32, f_ratio: np.float32 = np.float32(0), traj_line: Vector2 = Vector2.zero()) -> Vector2:
	temp = np.uint16(random(65536))
	dir = Vector2.direction_to_vector(temp)
	random_radius = dispersion * random_float_01()

	if f_ratio == np.float32(0):
		return Vector2(dir.x * random_radius, dir.y * random_radius)
	else:
		traj_line = traj_line.copy
		traj_line.normalize()
		return traj_line * random_radius * dir.x * f_ratio + Vector2(-traj_line.y, traj_line.x) * random_radius * dir.y
