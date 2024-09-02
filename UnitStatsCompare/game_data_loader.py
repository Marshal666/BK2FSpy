import io
import tkinter as tk
from virtual_file_system import VirtualFileSystemBaseClass
import bk2_xml_utils
import os
from PIL import Image, ImageTk
from Vector2 import Vector2

GAME_ROOT = "Consts/Game/GameContst_GameConsts.xdb"

def get_game_nations(file_system: VirtualFileSystemBaseClass):

	consts = bk2_xml_utils.load_xml_file(file_system, GAME_ROOT)

	if consts is None:
		return None

	consts_mp = bk2_xml_utils.href_read_xml_object(consts.Multiplayer, file_system)

	if consts_mp is None:
		return None

	if not hasattr(consts_mp.Sides, "Item"):
		return None

	if len(consts_mp.Sides.Item) < 1:
		return None

	consts_mp_path = bk2_xml_utils.actual_href_path(consts.Multiplayer, file_system)
	root_dir = os.path.dirname(consts_mp_path)

	ret = []

	for item in consts_mp.Sides.Item:
		ret.append(bk2_xml_utils.href_get_file_contents(item.NameFileRef, file_system, root_dir))

	return ret


def get_game_tech_levels(file_system: VirtualFileSystemBaseClass):

	consts = bk2_xml_utils.load_xml_file(file_system, GAME_ROOT)

	if consts is None:
		return None

	consts_mp = bk2_xml_utils.href_read_xml_object(consts.Multiplayer, file_system)

	if consts_mp is None:
		return None

	if not hasattr(consts_mp.TechLevels, "Item"):
		return None

	if len(consts_mp.TechLevels.Item) < 1:
		return None

	consts_mp_path = bk2_xml_utils.actual_href_path(consts.Multiplayer, file_system)
	root_dir = os.path.dirname(consts_mp_path)

	ret = []

	for item in consts_mp.TechLevels.Item:
		ret.append(bk2_xml_utils.href_get_file_contents(item.NameFileRef, file_system, root_dir))

	return ret


def get_nation_reinfs(file_system: VirtualFileSystemBaseClass, nation: int, tech_level: int):
	consts = bk2_xml_utils.load_xml_file(file_system, GAME_ROOT)

	if consts is None:
		return None

	consts_mp = bk2_xml_utils.href_read_xml_object(consts.Multiplayer, file_system)

	if consts_mp is None:
		return None

	consts_mp_path = bk2_xml_utils.actual_href_path(consts.Multiplayer, file_system)
	root_dir = os.path.dirname(consts_mp_path)

	ret = []

	for item in consts_mp.Sides.Item[nation].TechLevels.Item[tech_level].Reinforcements.Item:
		reinfs_xml = bk2_xml_utils.href_read_xml_object(item, file_system, root_dir)
		if reinfs_xml is None:
			continue
		ret.append(reinfs_xml.Type)

	return ret



MECH_UNIT_DEF = "MechUnit"
SQUAD_UNIT_DEF = "Squad"


def get_nation_reinf_units(file_system: VirtualFileSystemBaseClass, nation: int, tech_level: int, unit_type: str):
	consts = bk2_xml_utils.load_xml_file(file_system, GAME_ROOT)

	if consts is None:
		return None

	consts_mp = bk2_xml_utils.href_read_xml_object(consts.Multiplayer, file_system)

	if consts_mp is None:
		return None

	consts_mp_path = bk2_xml_utils.actual_href_path(consts.Multiplayer, file_system)
	root_dir = os.path.dirname(consts_mp_path)

	ret = []

	for item in consts_mp.Sides.Item[nation].TechLevels.Item[tech_level].Reinforcements.Item:
		reinfs_xml = bk2_xml_utils.href_read_xml_object(item, file_system, root_dir)

		if reinfs_xml.Type != unit_type:
			continue

		if not hasattr(reinfs_xml.Entries, "Item"):
			return None

		for unit in reinfs_xml.Entries.Item:
			if unit.MechUnit.attrib["href"]:
				ret.append((MECH_UNIT_DEF, unit.MechUnit.attrib["href"]))
				continue
			if unit.Squad.attrib["href"]:
				ret.append((SQUAD_UNIT_DEF, unit.Squad.attrib["href"]))
				continue

	ret = list(set(ret))

	return ret


def get_unit_xml_stats(file_system: VirtualFileSystemBaseClass, unit_path: str):
	unit_path = bk2_xml_utils.format_href(unit_path)
	unit_stats = bk2_xml_utils.load_xml_file(file_system, unit_path)
	return unit_stats


def get_unit_icon(file_system: VirtualFileSystemBaseClass, unit_path: str):

	unit_path = bk2_xml_utils.format_href(unit_path)

	unit_stats = bk2_xml_utils.load_xml_file(file_system, unit_path)

	if not hasattr(unit_stats, "IconTexture"):
		return None

	if not unit_stats.IconTexture.attrib["href"] or not unit_stats.IconTexture.attrib["href"].strip():
		return None

	root_dir = os.path.dirname(unit_path)

	texture_file = bk2_xml_utils.href_read_xml_object(unit_stats.IconTexture, file_system, root_dir)

	texture_path = bk2_xml_utils.actual_href_path(unit_stats.IconTexture, file_system, root_dir)
	texture_path = os.path.dirname(texture_path)

	dds_image: bytes = bk2_xml_utils.href_get_binary_file_contents(texture_file.DestName, file_system, texture_path)

	tkimg = Image.open(io.BytesIO(dds_image))

	photo = ImageTk.PhotoImage(tkimg)

	return photo


def get_unit_name(file_system: VirtualFileSystemBaseClass, unit_path: str):

	unit_path = bk2_xml_utils.format_href(unit_path)

	unit_stats = bk2_xml_utils.load_xml_file(file_system, unit_path)

	if not hasattr(unit_stats, "LocalizedNameFileRef"):
		return None

	root_path = os.path.dirname(unit_path)

	return bk2_xml_utils.href_get_file_contents(unit_stats.LocalizedNameFileRef, file_system, root_path)


def get_hp_stats(unit_stats):
	return float(unit_stats.MaxHP)


def get_aabb_coef(unit_stats):
	return float(unit_stats.SmallAABBCoeff)


def get_aabb_half(unit_stats) -> tuple[float, float]:
	return float(unit_stats.AABBHalfSize.x), float(unit_stats.AABBHalfSize.y)


def get_unit_weapon_stats(file_system: VirtualFileSystemBaseClass, weapon_path: str, unit_path: str):
	weapon_path = bk2_xml_utils.format_href(weapon_path)
	unit_path = bk2_xml_utils.format_href(unit_path)
	unit_path = os.path.dirname(unit_path)
	if file_system.contains_file(os.path.join(unit_path, weapon_path)):
		return bk2_xml_utils.load_xml_file(file_system, os.path.join(unit_path, weapon_path))
	if file_system.contains_file(weapon_path):
		return bk2_xml_utils.load_xml_file(file_system, weapon_path)
	return None


def get_unit_armors(unit_stats) -> list[tuple[float, float]]:
	return [(float(item.Min), float(item.Max)) for item in unit_stats.armors.Item]


class StatsBonuses:


	class StatsBonus:

		def __init__(self):
			self.add_bonus = 0.0
			self.mult_bonus = 1.0
			self.zero_count = 0.0

		@staticmethod
		def from_xml_object(obj):
			ret = StatsBonuses.StatsBonus()
			ret.add_bonus = float(obj.AddBonus)
			ret.mult_bonus = float(obj.MultBonus)
			ret.zero_count = float(obj.ZeroCount)
			return ret

		def __add__(self, other):
			ret = StatsBonuses.StatsBonus()
			ret.add_bonus = self.add_bonus + other.add_bonus
			ret.mult_bonus = self.mult_bonus + other.mult_bonus
			ret.zero_count = self.zero_count + other.zero_count
			return ret

	PROPERTIES = [	"Durability",
					"SmallAABBCoeff",
					"Camouflage",
					"SightPower",
					"SightRange",
					"Speed",
					"RotateSpeed",
					"WeaponDispersion",
					"WeaponDamage",
					"WeaponPiercing",
					"WeaponTrackDamageProb",
					"WeaponRelaxTime",
					"WeaponAimTime",
					"WeaponShellSpeed",
					"WeaponArea",
					"WeaponArea2",
					"Cover"
				]

	def __init__(self):
		for p in StatsBonuses.PROPERTIES:
			setattr(self, p, StatsBonuses.StatsBonus())

	def __add__(self, other):
		ret = StatsBonuses()
		for p in StatsBonuses.PROPERTIES:
			s1 = getattr(self, p, StatsBonuses.StatsBonus())
			s2 = getattr(other, p, StatsBonuses.StatsBonus())
			ret.add_bonus = s1.add_bonus + s2.add_bonus
		return ret

	@staticmethod
	def from_xml_file(obj):
		ret = StatsBonuses()
		for p in StatsBonuses.PROPERTIES:
			bonuses = getattr(obj, p, StatsBonuses.StatsBonus())
			if not isinstance(bonuses, StatsBonuses.StatsBonus):
				bonuses = StatsBonuses.StatsBonus.from_xml_object(bonuses)
			setattr(ret, p, bonuses)
		return


def get_stats_bonuses(file_system: VirtualFileSystemBaseClass, stats_href, root_path: str):
	bonus_xml = bk2_xml_utils.href_read_xml_object(stats_href, file_system, root_path)
	return StatsBonuses.from_xml_file(bonus_xml)


class UnitWeaponsData:

	@staticmethod
	def __get_unit_weapons(unit_stats) -> list[list[str]]:
		if not hasattr(unit_stats.platforms, "Item"):
			return [[]]
		ret = []
		for platform in unit_stats.platforms.Item:
			ret.append([])
			if not hasattr(platform.guns, "Item"):
				continue
			for gun in platform.guns.Item:
				if not gun.Weapon.attrib["href"] or not gun.Weapon.attrib["href"].strip():
					continue
				ret[-1].append(gun.Weapon.attrib["href"])
		return ret

	def __init__(self, file_system: VirtualFileSystemBaseClass, unit_stats, unit_path: str):
		self.__weapons_array = UnitWeaponsData.__get_unit_weapons(unit_stats)
		self.file_system = file_system

		# list[(index:p->w->shell), weapon_path, weapon_name, weapon_stats, shell_stats]
		self.weapons: list[tuple[tuple[int, int, int], str, str, object, object]] = []
		for i, weapon_array in enumerate(self.__weapons_array):
			for j, weapon in enumerate(weapon_array):
				weapon_stats = get_unit_weapon_stats(file_system, weapon, unit_path)
				if weapon_stats is None:
					continue
				if not hasattr(weapon_stats.shells, "Item"):
					continue
				weapon_path = bk2_xml_utils.format_href(weapon)
				weapon_dir = os.path.dirname(weapon_path)
				weapon_name = "<Missing Weapon Name>"
				try:
					weapon_name = bk2_xml_utils.href_get_file_contents(weapon_stats.LocalizedNameFileRef, file_system,
																	   weapon_dir)
				except Exception:
					pass
				for k, shell in enumerate(weapon_stats.shells.Item):
					weapon_index = (i, j, k)
					weapon_shell_name = f"p[{i}]->w[{j}]->shell[{k}]: {weapon_name}"
					self.weapons.append((weapon_index, weapon_path, weapon_shell_name, weapon_stats, shell))

	@property
	def weapon_count(self):
		return len(self.weapons)

	@property
	def weapon_names(self):
		return [weapon[2] for weapon in self.weapons]

	@property
	def best_piercing_shell_index(self):
		if self.weapon_count < 1:
			return None
		best_index = 0
		current_piercing = (float(self.weapons[best_index][4].Piercing) +
							float(self.weapons[best_index][4].PiercingRandom))
		for i in range(1, self.weapon_count):
			i_piercing = float(self.weapons[i][4].Piercing) + float(self.weapons[i][4].PiercingRandom)
			if i_piercing > current_piercing:
				best_index = i
				current_piercing = i_piercing
		return best_index

	def get_weapon_stats(self, index: int):
		return self.weapons[index][3]

	def get_shell_stats(self, index: int):
		return self.weapons[index][4]

	def get_shell_index(self, weapon_index: int):
		return self.weapons[weapon_index][0][2]

	def get_shell_damage_min_max(self, index: int):
		damage = float(self.weapons[index][4].DamagePower)
		damage_random = float(self.weapons[index][4].DamageRandom)
		min_damage = max(0, damage - damage_random)
		max_damage = damage + damage_random
		return min_damage, max_damage

	def get_shell_piercing_min_max(self, index: int):
		piercing = float(self.weapons[index][4].Piercing)
		piercing_random = float(self.weapons[index][4].PiercingRandom)
		min_piercing = max(0, piercing - piercing_random)
		max_piercing = piercing + piercing_random
		return min_piercing, max_piercing


class UnitStats:

	class WeaponShellStats:

		def __init__(self):
			self.weapon_path = ""
			self.Dispersion = tk.DoubleVar()
			self.AimingTime = tk.DoubleVar()
			self.RangeMax = tk.DoubleVar()
			self.RangeMin = tk.DoubleVar()
			self.Ceiling = tk.DoubleVar()

			self.Piercing = tk.DoubleVar()
			self.PiercingRandom = tk.DoubleVar()
			self.DamagePower = tk.DoubleVar()
			self.DamageRandom = tk.DoubleVar()
			self.Area = tk.DoubleVar()
			self.Area2 = tk.DoubleVar()
			self.FireRate = tk.DoubleVar()
			self.RelaxTime = tk.DoubleVar()

		@property
		def min_max_damage(self):
			try:
				min_dmg = max(0.0, self.DamagePower.get() - self.DamageRandom.get())
				max_dmg = self.DamagePower.get() + self.DamageRandom.get()
			except Exception:
				return float("NaN"), float("NaN")
			return min_dmg, max_dmg

		@property
		def min_max_piercing(self):
			try:
				min_piercing = max(0.0, self.Piercing.get() - self.PiercingRandom.get())
				max_piercing = self.Piercing.get() + self.PiercingRandom.get()
			except Exception:
				return float("NaN"), float("NaN")
			return min_piercing, max_piercing

		@property
		def range_min_max(self):
			try:
				return self.RangeMin.get(), self.RangeMax.get()
			except Exception:
				return 0.0, 40.0

		@staticmethod
		def from_xml_weapon_object(xml_weapon_object, shell_index: int, weapon_path: str, on_edit_command):

			ret = UnitStats.WeaponShellStats()

			ret.weapon_path = weapon_path

			ret.Dispersion.set(float(xml_weapon_object.Dispersion))
			ret.Dispersion.trace_add("write", lambda x, y, z: on_edit_command())

			ret.AimingTime.set(float(xml_weapon_object.AimingTime))
			ret.AimingTime.trace_add("write", lambda x, y, z: on_edit_command())

			ret.RangeMax.set(float(xml_weapon_object.RangeMax))
			ret.RangeMax.trace_add("write", lambda x, y, z: on_edit_command())

			ret.RangeMin.set(float(xml_weapon_object.RangeMin))
			ret.RangeMin.trace_add("write", lambda x, y, z: on_edit_command())

			ret.Ceiling.set(float(xml_weapon_object.Ceiling))
			ret.Ceiling.trace_add("write", lambda x, y, z: on_edit_command())

			shell = xml_weapon_object.shells.Item[shell_index]
			ret.Piercing.set(float(shell.Piercing))
			ret.Piercing.trace_add("write", lambda x, y, z: on_edit_command())

			ret.PiercingRandom.set(float(shell.PiercingRandom))
			ret.PiercingRandom.trace_add("write", lambda x, y, z: on_edit_command())

			ret.DamagePower.set(float(shell.DamagePower))
			ret.DamagePower.trace_add("write", lambda x, y, z: on_edit_command())

			ret.DamageRandom.set(float(shell.DamageRandom))
			ret.DamageRandom.trace_add("write", lambda x, y, z: on_edit_command())

			ret.Area.set(float(shell.Area))
			ret.Area.trace_add("write", lambda x, y, z: on_edit_command())

			ret.Area2.set(float(shell.Area2))
			ret.Area2.trace_add("write", lambda x, y, z: on_edit_command())

			ret.FireRate.set(float(shell.FireRate))
			ret.FireRate.trace_add("write", lambda x, y, z: on_edit_command())

			ret.RelaxTime.set(float(shell.RelaxTime))
			ret.RelaxTime.trace_add("write", lambda x, y, z: on_edit_command())

			return ret



	def __init__(self):
		self.unit_path = ""
		self.MaxHP = tk.DoubleVar()
		self.Sight = tk.DoubleVar()
		self.AABBCenter_x = tk.DoubleVar()
		self.AABBCenter_y = tk.DoubleVar()
		self.AABBHalfSize_x = tk.DoubleVar()
		self.AABBHalfSize_y = tk.DoubleVar()
		self.SmallAABBCoeff = tk.DoubleVar()
		self.WeaponsData = None
		self.WeaponsShells: list[UnitStats.WeaponShellStats] = []
		self.Armors = [[tk.DoubleVar(), tk.DoubleVar()] for _ in range(6)]

	@property
	def armors_float_array(self):
		return [(element[0].get(), element[1].get()) for element in self.Armors]

	@property
	def aabb_center(self) -> Vector2:
		return Vector2(self.AABBCenter_x.get(), self.AABBCenter_y.get())

	@property
	def aabb_half_size(self) -> Vector2:
		return Vector2(self.AABBHalfSize_x.get(), self.AABBHalfSize_y.get())

	def load_from_xml_object(self, xml_object, file_system: VirtualFileSystemBaseClass, on_edit_command,
							 unit_path:str=""):
		ret = self

		ret.unit_path = unit_path

		ret.MaxHP.set(float(xml_object.MaxHP))
		ret.MaxHP.trace_add("write", lambda x, y, z: on_edit_command())

		ret.Sight.set(float(xml_object.Sight))
		ret.Sight.trace_add("write", lambda x, y, z: on_edit_command())

		ret.AABBCenter_x.set(float(xml_object.AABBCenter.x))
		ret.AABBCenter_x.trace_add("write", lambda x, y, z: on_edit_command())

		ret.AABBCenter_y.set(float(xml_object.AABBCenter.y))
		ret.AABBCenter_y.trace_add("write", lambda x, y, z: on_edit_command())

		ret.AABBHalfSize_x.set(float(xml_object.AABBHalfSize.x))
		ret.AABBHalfSize_x.trace_add("write", lambda x, y, z: on_edit_command())

		ret.AABBHalfSize_y.set(float(xml_object.AABBHalfSize.y))
		ret.AABBHalfSize_y.trace_add("write", lambda x, y, z: on_edit_command())

		ret.SmallAABBCoeff.set(float(xml_object.SmallAABBCoeff))
		ret.SmallAABBCoeff.trace_add("write", lambda x, y, z: on_edit_command())

		ret.WeaponsData = UnitWeaponsData(file_system, xml_object, unit_path)

		for i in range(ret.WeaponsData.weapon_count):
			shell_index = ret.WeaponsData.weapons[i][0][2]
			weapon_stats = ret.WeaponsData.weapons[i][3]
			weapon_path = ret.WeaponsData.weapons[i][1]
			ret.WeaponsShells.append(
				UnitStats.WeaponShellStats.from_xml_weapon_object(weapon_stats, shell_index, weapon_path,
																  on_edit_command))

		for i in range(len(ret.Armors)):
			armor_min = float(xml_object.armors.Item[i].Min)
			armor_max = float(xml_object.armors.Item[i].Max)

			ret.Armors[i][0].set(armor_min)
			ret.Armors[i][0].trace_add("write", lambda x, y, z: on_edit_command())

			ret.Armors[i][1].set(armor_max)
			ret.Armors[i][1].trace_add("write", lambda x, y, z: on_edit_command())

	@staticmethod
	def from_xml_object(xml_object, file_system: VirtualFileSystemBaseClass, on_edit_command, unit_path:str=""):

		ret = UnitStats()
		ret.load_from_xml_object(xml_object, file_system, on_edit_command, unit_path)
		return ret
