from enum import Enum
import game_data_loader
import probability_calculation
from Vector2 import Vector2
import numpy as np
import stats_compare_data as data
import custom_random


class AttackDirection(Enum):
	FRONT=0
	LEFT=1
	BACK=2
	RIGHT=3
	TOP=4
	BOTTOM=5

	@staticmethod
	def get_str_values():
		return ["FRONT", "LEFT", "BACK", "RIGHT", "TOP", "BOTTOM"]


def get_piercing_probability(attacker_shell, defender, attack_direction: int) -> float:
	armors = game_data_loader.get_unit_armors(defender)[attack_direction.value]
	piercing = float(attacker_shell.Piercing)
	piercing_random = float(attacker_shell.PiercingRandom)
	return probability_calculation.piercing_probability(armors[0], armors[1], piercing, piercing_random)


def get_aabb_hit_probability(attacker_gun, defender, range: float, attack_direction: int) -> tuple[float, float, float]:
	dir = Vector2.direction_to_vector(np.uint16(attack_direction % 65536))
	weapon_dispersion = float(attacker_gun.Dispersion)
	weapon_max_range = float(attacker_gun.RangeMax)
	dispersion = np.float32(weapon_dispersion / weapon_max_range * range) * 32
	aabb_half_size = Vector2(np.float32(defender.AABBHalfSize.x.text), np.float32(defender.AABBHalfSize.y.text))
	aabb_center = Vector2(np.float32(defender.AABBCenter.x.text), np.float32(defender.AABBCenter.y.text))
	aabb_coef =  np.clip(np.float32(defender.SmallAABBCoeff.text), np.float32(0), np.float32(1))
	iters = data.simulation_iterations.get()

	rng_seed = data.simulation_rng_seed.get()
	custom_random.init_seed(rng_seed)

	return probability_calculation.get_hit_count(aabb_half_size, aabb_center, dir, aabb_coef, dispersion, iters)
