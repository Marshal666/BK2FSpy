import scipy.integrate as integrate
import numpy as np
from SRect import SRect
from Vector2 import Vector2
import custom_random
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

def will_hit(aabb_half_size: Vector2,
				   aabb_center: Vector2,
				   dir: Vector2,
				   aabb_coef: np.float32,
				   dispersion: np.float32) -> tuple[bool, Vector2]:
	rect = SRect.get_unit_rect(aabb_half_size, aabb_center, dir)
	rect.compress(aabb_coef)

	hit_point = custom_random.rand_quadr_in_circle(dispersion)
	hit_point += aabb_center

	return rect.is_point_inside(hit_point), hit_point


def get_hit_count(aabb_half_size: Vector2,
				  aabb_center: Vector2,
				  dir: Vector2,
				  aabb_coef: np.float32,
				  dispersion: np.float32,
				  tests: int,
				  seed: int=1337) -> tuple[int, int, int]:

	"""
	successes = 0
	bounce_offs = 0
	fails = 0

	rect_full = SRect.get_unit_rect(aabb_half_size, aabb_center, dir)
	rect_scaled = SRect.get_unit_rect(aabb_half_size, aabb_center, dir)
	rect_scaled.compress(aabb_coef)

	for i in range(tests):
		point = custom_random.rand_quadr_in_circle(dispersion)
		if rect_scaled.is_point_inside(point):
			successes += 1
			continue
		if rect_full.is_point_inside(point):
			bounce_offs += 1
			continue
		fails += 1

	return successes, bounce_offs, fails"""

	return aabb_hit_calc.get_hit_probabilities(tests, seed,
											 aabb_half_size.x, aabb_half_size.y,
											 aabb_center.x, aabb_center.y,
											 dir.x, dir.y,
											 aabb_coef, dispersion)

"""
aabb_half_size = Vector2(40, 60)
aabb_center = Vector2(0, 0)
dir = Vector2.up()
aabb_coef = np.float32(0.96)
dispersion = np.float32(1.2) * 32

tests = 100000
hits = 0

s, b, f = get_hit_count(aabb_half_size, aabb_center, dir, aabb_coef, dispersion, tests)

print(f"Successful Hits: {s/tests*100:.2f}%\nBounce Offs: {b/tests*100:.2f}%\nFails: {f/tests*100:.2f}%")
"""

"""
import matplotlib.pyplot as plt

times = 20000
points = []
for i in range(times):
	point = custom_random.rand_quadr_in_circle(dispersion)
	points.append(point)

plt.scatter([point.x for point in points], [point.y for point in points], color="red", s=0.5)
plt.title("Dispersion distribution")
plt.xlabel("X Axis")
plt.ylabel("Y Axis")
plt.gca().set_aspect('equal', adjustable='box')

plt.show(figsize=(9,9))
"""

