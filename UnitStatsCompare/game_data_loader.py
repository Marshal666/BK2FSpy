import io

from virtual_file_system import VirtualFileSystemBaseClass
import bk2_xml_utils
import os
from PIL import Image, ImageTk
import re
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

def get_unit_stats(file_system: VirtualFileSystemBaseClass, unit_path: str):
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
