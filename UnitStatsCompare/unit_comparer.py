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


def get_aabb_hit_probability(attacker_frame, defender_frame, range: float, attack_direction: int) -> tuple[float, float, float, float]:

	dir = Vector2.direction_to_vector(np.uint16(attack_direction % 65536))

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell : UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	try:
		dispersion = (weapon_shell.Dispersion.get() / weapon_shell.RangeMax.get() * range) * 32
		aabb_coef = defender_frame.unit_stats.SmallAABBCoeff.get()

		aabb_half_size = defender_frame.unit_stats.aabb_half_size
		aabb_center = defender_frame.unit_stats.aabb_center

		# if unit type is MechUnit...
		area_damage = min(weapon_shell.Area.get(), weapon_shell.Area2.get()) * 32
	except Exception:
		return float("NaN"), float("NaN"), float("NaN"), float("NaN")

	iters = data.simulation_iterations.get()

	rng_seed = data.simulation_rng_seed.get()

	dispersion = attacker_frame.applied_bonuses.WeaponDispersion.apply_bonus(dispersion)
	aabb_coef = defender_frame.applied_bonuses.SmallAABBCoeff.apply_bonus(aabb_coef)

	#print(f"defender aabb_coef: {aabb_coef}, modifiers: {defender_frame.applied_bonuses.SmallAABBCoeff}")

	return probability_calculation.get_hit_count(aabb_half_size, aabb_center, dir, aabb_coef, dispersion, area_damage, iters, rng_seed)


def get_one_shot_probability(attacker_frame, defender_frame):

	defender: game_data_loader.UnitStats = defender_frame.unit_stats
	attacker: game_data_loader.UnitStats = attacker_frame.unit_stats

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell : UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	try:
		defender_hp = defender.MaxHP.get()
		damage = weapon_shell.DamagePower.get()
		damage_random = weapon_shell.DamageRandom.get()
	except Exception:
		return float("NaN"), float("NaN"), float("NaN"), float("NaN")

	bonus_add = attacker_frame.applied_bonuses.WeaponDamage.add_bonus
	bonus_mult = attacker_frame.applied_bonuses.WeaponDamage.mult_bonus

	durability_add = defender_frame.applied_bonuses.Durability.add_bonus
	durability_mult = defender_frame.applied_bonuses.Durability.mult_bonus

	return probability_calculation.one_shot_probability(defender_hp, damage, damage_random, bonus_add, bonus_mult,
														durability_add, durability_mult)


def get_area_one_shot_probability(attacker_frame, defender_frame):

	defender: game_data_loader.UnitStats = defender_frame.unit_stats
	attacker: game_data_loader.UnitStats = attacker_frame.unit_stats

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	try:
		defender_hp = defender.MaxHP.get()
		damage = weapon_shell.DamagePower.get()
		damage_random = weapon_shell.DamageRandom.get()
	except Exception:
		return float("NaN"), float("NaN"), float("NaN"), float("NaN")

	bonus_add = attacker_frame.applied_bonuses.WeaponDamage.add_bonus
	bonus_mult = attacker_frame.applied_bonuses.WeaponDamage.mult_bonus

	durability_add = defender_frame.applied_bonuses.Durability.add_bonus
	durability_mult = defender_frame.applied_bonuses.Durability.mult_bonus

	alpha = data.area_damage_coeff.get()

	return probability_calculation.area_one_shot_probability(defender_hp, damage, damage_random, bonus_add, bonus_mult,
														durability_add, durability_mult, alpha)


def average_amount_of_damage_shots_needed_for_killing(attacker_frame, defender_frame):
	defender: game_data_loader.UnitStats = defender_frame.unit_stats
	attacker: game_data_loader.UnitStats = attacker_frame.unit_stats

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	try:
		hp = defender.MaxHP.get()
	except Exception:
		return float("NaN")

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



def get_average_amount_of_shots_needed_for_kill(attacker_frame, defender_frame, hit_chance: float, area_chance: float):

	ret = float("Inf")

	if abs(hit_chance) <= K_EPSILON:
		return ret

	# NaN check
	if hit_chance != hit_chance:
		return float("NaN")

	if area_chance != area_chance:
		return float("NaN")

	defender: game_data_loader.UnitStats = defender_frame.unit_stats
	attacker: game_data_loader.UnitStats = attacker_frame.unit_stats

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	try:
		hp = defender.MaxHP.get()
	except Exception:
		return float("NaN")

	if hp != hp:
		return float("NaN")

	damage_min, damage_max = weapon_shell.min_max_damage

	attacker_bonuses: StatsBonuses = attacker_frame.applied_bonuses
	defender_bonuses: StatsBonuses = defender_frame.applied_bonuses

	damage_min = attacker_bonuses.WeaponDamage.apply_bonus(damage_min)
	damage_max = attacker_bonuses.WeaponDamage.apply_bonus(damage_max)

	damage_min = defender_bonuses.Durability.apply_bonus_as_durability(damage_min)
	damage_max = defender_bonuses.Durability.apply_bonus_as_durability(damage_max)

	avg_damage = (damage_min + damage_max) / 2.0

	if abs(avg_damage) <= K_EPSILON:
		return ret

	alpha = data.area_damage_coeff.get()

	tries = data.shot_simulation_iterations.get()

	ret = probability_calculation.get_shot_count(tries, data.simulation_rng_seed.get(), hit_chance, area_chance,
												 alpha, hp, damage_min, damage_max)

	return max(1.0, round(ret, 1))


def get_average_time_needed_for_kill(attacker_frame, defender_frame, average_shots_needed: float):

	if average_shots_needed != average_shots_needed:
		return float("NaN")

	ret = float("NaN")

	defender: game_data_loader.UnitStats = defender_frame.unit_stats
	attacker: game_data_loader.UnitStats = attacker_frame.unit_stats

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	attacker_bonuses: StatsBonuses = attacker_frame.applied_bonuses
	defender_bonuses: StatsBonuses = defender_frame.applied_bonuses

	try:
		aim_time = weapon_shell.AimingTime.get()
	except Exception:
		return float("NaN")

	aim_time = attacker_bonuses.WeaponAimTime.apply_bonus(aim_time)

	if average_shots_needed == float("Inf"):
		return float("Inf")

	# Time's a bit more "diverse" without this rounding
	average_shots_needed = round(average_shots_needed)

	try:
		ammo_per_burst = weapon_shell.AmmoPerBurst.get()
		relax_time = weapon_shell.RelaxTime.get()
		fire_rate = weapon_shell.FireRate.get()

		relax_time = attacker_bonuses.WeaponRelaxTime.apply_bonus(relax_time)
	except Exception:
		return float("NaN")

	if fire_rate < K_EPSILON:
		return float("NaN")

	if ammo_per_burst < 2:
		ret = aim_time + (average_shots_needed - 1) * relax_time
	else:
		count = max(1.0, round(average_shots_needed / ammo_per_burst))
		ret = aim_time + (average_shots_needed - 1) * (1.0 / fire_rate) + count * relax_time

	return ret


def get_track_break_probability(attacker_frame, defender_frame) -> float:

	defender: game_data_loader.UnitStats = defender_frame.unit_stats
	attacker: game_data_loader.UnitStats = attacker_frame.unit_stats

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	attacker_bonuses: StatsBonuses = attacker_frame.applied_bonuses
	defender_bonuses: StatsBonuses = defender_frame.applied_bonuses

	try:
		ret = attacker_bonuses.WeaponTrackDamageProb.apply_bonus(weapon_shell.BrokeTrackProbability.get())
	except Exception:
		return float("NaN")

	return ret


def get_overall_piercing_min_max(attacker_frame, defender_frame) -> tuple[float, float]:

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	attacker_bonuses: StatsBonuses = attacker_frame.applied_bonuses
	defender_bonuses: StatsBonuses = defender_frame.applied_bonuses

	try:
		piercing_min = max(0, weapon_shell.Piercing.get() - weapon_shell.PiercingRandom.get())
		piercing_max = max(0, weapon_shell.Piercing.get() + weapon_shell.PiercingRandom.get())
	except Exception:
		return float("NaN"), float("NaN")

	return attacker_bonuses.WeaponPiercing.apply_bonus(piercing_min), attacker_bonuses.WeaponPiercing.apply_bonus(piercing_max)


def get_overall_damage_min_max(attacker_frame, defender_frame) -> tuple[float, float]:

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	attacker_bonuses: StatsBonuses = attacker_frame.applied_bonuses
	defender_bonuses: StatsBonuses = defender_frame.applied_bonuses

	try:
		damage_min = max(0, weapon_shell.DamagePower.get() - weapon_shell.DamageRandom.get())
		damage_max = max(0, weapon_shell.DamagePower.get() + weapon_shell.DamageRandom.get())
	except Exception:
		return float("NaN"), float("NaN")

	damage_min = attacker_bonuses.WeaponDamage.apply_bonus(damage_min)
	damage_max = attacker_bonuses.WeaponDamage.apply_bonus(damage_max)

	damage_min = defender_bonuses.Durability.apply_bonus_as_durability(damage_min)
	damage_max = defender_bonuses.Durability.apply_bonus_as_durability(damage_max)

	return damage_min, damage_max


def get_overall_dispersion(attacker_frame, range: float) -> float:

	weapon_index = attacker_frame.weapon_names.index(attacker_frame.selected_weapon.get())
	weapon_shell: UnitStats.WeaponShellStats = attacker_frame.unit_stats.WeaponsShells[weapon_index]

	attacker_bonuses: StatsBonuses = attacker_frame.applied_bonuses

	try:
		dispersion = attacker_bonuses.WeaponDispersion.apply_bonus(weapon_shell.Dispersion.get())
	except Exception:
		return float("NaN")

	return dispersion / weapon_shell.RangeMax.get() * range
