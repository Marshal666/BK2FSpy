import scipy.integrate as integrate
import numpy as np
from Vector2 import Vector2
import aabb_hit_calc

def piercing_probability(armor_min, armor_max, piercing, piercing_random, bonus_piercing_add, bonus_piercing_mult):
	# Calculate MinimumPiercing and MaximumPiercing
	min_piercing = piercing - piercing_random  # Using max(0, piercing - piercing_random) doesn't work 100% well.
	max_piercing = piercing + piercing_random

	min_piercing = (min_piercing + bonus_piercing_add) * bonus_piercing_mult
	max_piercing = (max_piercing + bonus_piercing_add) * bonus_piercing_mult

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

	if abs(div) <= 0.00001:
		return float("NaN")

	return num[0] / div


def one_shot_probability(defender_hp, damage, damage_random, bonus_add, bonus_mult, durability_add, durability_mult):
	damage_min = damage - damage_random
	damage_max = damage + damage_random

	if damage_min == damage_max:
		return 1.0 if damage_min >= defender_hp else 0.0

	damage_min = (damage_min + bonus_add) * bonus_mult
	damage_max = (damage_max + bonus_add) * bonus_mult

	damage_min = (damage_min - durability_add) * durability_mult
	damage_max = (damage_max - durability_add) * durability_mult

	if damage_min >= defender_hp:
		return 1.0

	if defender_hp >= damage_max:
		return 0.0

	return 1.0 - (defender_hp - damage_min) / (damage_max - damage_min)



def get_hit_count(aabb_half_size: Vector2,
				  aabb_center: Vector2,
				  dir: Vector2,
				  aabb_coef: float,
				  dispersion: float,
				  area_damage: float,
				  tests: int,
				  seed: int=1337) -> tuple[int, int, int]:

	# written in C++ bind for ~50x better performance
	return aabb_hit_calc.get_hit_probabilities(tests, seed,
											 aabb_half_size.x, aabb_half_size.y,
											 aabb_center.x, aabb_center.y,
											 dir.x, dir.y,
											 aabb_coef, dispersion, area_damage)


def get_shot_count(tests: int,
				   seed: int,
				   hit_chance: float,
				   area_chance: float,
				   area_damage_coef: float,
				   hp_original: float,
				   damage_min: float,
				   damage_max: float):

	# called from C++ bind
	return  aabb_hit_calc.get_average_amount_of_shots_need_for_kill(tests, seed,
																	hit_chance, area_chance,
																	area_damage_coef, hp_original,
																	damage_min, damage_max)
