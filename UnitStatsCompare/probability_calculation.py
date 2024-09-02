import scipy.integrate as integrate
import numpy as np
from Vector2 import Vector2
import aabb_hit_calc

def piercing_probability(armor_min, armor_max, piercing, piercing_random):
	# Calculate MinimumPiercing and MaximumPiercing
	min_piercing = piercing - piercing_random  # Using max(0, piercing - piercing_random) doesn't work 100% well.
	max_piercing = piercing + piercing_random

	if max_piercing < armor_min:
		return 0.0

	if min_piercing >= armor_max:
		return 1.0

	if armor_min == armor_max and min_piercing == max_piercing:
		return 1.0 if max_piercing >= armor_max else 0.0

	if armor_min == armor_max and min_piercing != max_piercing:
		return (max_piercing - armor_max) / (max_piercing - min_piercing)

	num = integrate.quad(lambda x: (max(max_piercing, x) - max(min_piercing, x)), armor_min, armor_max)
	div = (armor_max - armor_min) * (max_piercing - min_piercing)

	return num[0] / div


def get_hit_count(aabb_half_size: Vector2,
				  aabb_center: Vector2,
				  dir: Vector2,
				  aabb_coef: np.float32,
				  dispersion: np.float32,
				  tests: int,
				  seed: int=1337) -> tuple[int, int, int]:

	# written in C++ bind for ~50x better performance
	return aabb_hit_calc.get_hit_probabilities(tests, seed,
											 aabb_half_size.x, aabb_half_size.y,
											 aabb_center.x, aabb_center.y,
											 dir.x, dir.y,
											 aabb_coef, dispersion)
