from enum import Enum
import game_data_loader
import probability_calculation
from Vector2 import Vector2
import numpy as np
import stats_compare_data as data
from game_data_loader import UnitStats

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


def get_piercing_probability(attacker_frame, defender_frame, attack_direction: AttackDirection) -> float:

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell : UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	armors = defender_frame.unit_stats.armors_float_array[attack_direction.value]
	try:
		piercing = weapon_shell.Piercing.get()
		piercing_random = weapon_shell.PiercingRandom.get()
	except Exception:
		return float("NaN")
	return probability_calculation.piercing_probability(armors[0], armors[1], piercing, piercing_random)


def get_aabb_hit_probability(attacker_frame, defender_frame, range: float, attack_direction: int) -> tuple[float, float, float]:

	dir = Vector2.direction_to_vector(np.uint16(attack_direction % 65536))

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell : UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	try:
		dispersion = (weapon_shell.Dispersion.get() / weapon_shell.RangeMax.get() * range) * 32
		aabb_coef = defender_frame.unit_stats.SmallAABBCoeff.get()

		aabb_half_size = defender_frame.unit_stats.aabb_half_size
		aabb_center = defender_frame.unit_stats.aabb_center
	except Exception:
		return float("NaN"), float("NaN"), float("NaN")

	iters = data.simulation_iterations.get()

	rng_seed = data.simulation_rng_seed.get()

	return probability_calculation.get_hit_count(aabb_half_size, aabb_center, dir, aabb_coef, dispersion, iters, rng_seed)
