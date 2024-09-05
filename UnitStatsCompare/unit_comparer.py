import math
from enum import Enum
import game_data_loader
import probability_calculation
from Vector2 import Vector2
import numpy as np
import stats_compare_data as data
from game_data_loader import UnitStats, StatsBonuses

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

K_EPSILON = 1e-9

def get_piercing_probability(attacker_frame, defender_frame, attack_direction: AttackDirection) -> float:

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell : UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	try:
		armors = defender_frame.unit_stats.armors_float_array[attack_direction.value]
		piercing = weapon_shell.Piercing.get()
		piercing_random = weapon_shell.PiercingRandom.get()
	except Exception:
		return float("NaN")
	return probability_calculation.piercing_probability(armors[0], armors[1], piercing, piercing_random, attacker_frame.applied_bonuses.WeaponPiercing.add_bonus, attacker_frame.applied_bonuses.WeaponPiercing.mult_bonus)


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

	dispersion = attacker_frame.applied_bonuses.WeaponDispersion.apply_bonus(dispersion)
	aabb_coef = defender_frame.applied_bonuses.SmallAABBCoeff.apply_bonus(aabb_coef)

	#print(f"defender aabb_coef: {aabb_coef}, modifiers: {defender_frame.applied_bonuses.SmallAABBCoeff}")

	return probability_calculation.get_hit_count(aabb_half_size, aabb_center, dir, aabb_coef, dispersion, iters, rng_seed)


def get_one_shot_probability(attacker_frame, defender_frame):
	defender: game_data_loader.UnitStats = defender_frame.unit_stats
	attacker: game_data_loader.UnitStats = attacker_frame.unit_stats

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell : UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	defender_hp = defender.MaxHP.get()
	damage = weapon_shell.DamagePower.get()
	damage_random = weapon_shell.DamageRandom.get()

	bonus_add = attacker_frame.applied_bonuses.WeaponDamage.add_bonus
	bonus_mult = attacker_frame.applied_bonuses.WeaponDamage.mult_bonus

	durability_add = defender_frame.applied_bonuses.Durability.add_bonus
	durability_mult = defender_frame.applied_bonuses.Durability.mult_bonus

	return probability_calculation.one_shot_probability(defender_hp, damage, damage_random, bonus_add, bonus_mult,
														durability_add, durability_mult)


def average_amount_of_damage_shots_needed_for_killing(attacker_frame, defender_frame):
	defender: game_data_loader.UnitStats = defender_frame.unit_stats
	attacker: game_data_loader.UnitStats = attacker_frame.unit_stats

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	hp = defender.MaxHP.get()

	damage_min, damage_max = weapon_shell.min_max_damage

	attacker_bonuses: StatsBonuses = attacker_frame.applied_bonuses
	defender_bonuses: StatsBonuses = defender_frame.applied_bonuses

	damage_min = attacker_bonuses.WeaponDamage.apply_bonus(damage_min)
	damage_max = attacker_bonuses.WeaponDamage.apply_bonus(damage_max)

	damage_min = defender_bonuses.Durability.apply_bonus_as_durability(damage_min)
	damage_max = defender_bonuses.Durability.apply_bonus_as_durability(damage_max)

	avg_damage = (damage_min + damage_max) / 2.0

	if abs(avg_damage) <= K_EPSILON:
		return float("Inf")

	return int(math.ceil(hp / avg_damage))



def get_average_amount_of_shots_needed_for_kill(attacker_frame, defender_frame, total_chance: float):

	ret = float("Inf")

	if total_chance <= K_EPSILON:
		return ret

	dmg_amount = average_amount_of_damage_shots_needed_for_killing(attacker_frame, defender_frame)

	if abs(total_chance - 1.0) <= K_EPSILON:
		return dmg_amount

	#count = int(math.ceil(math.log(1 - criteria) / math.log(1 - total_chance)))
	count = 1.0 / total_chance

	return int(round((dmg_amount * count)))

