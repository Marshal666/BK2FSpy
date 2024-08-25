import io

from virtual_file_system import VirtualFileSystemBaseClass
import bk2_xml_utils
import os
from PIL import Image, ImageTk

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
				ret.append(("MechUnit", unit.MechUnit.attrib["href"]))
				continue
			if unit.Squad.attrib["href"]:
				ret.append(("Squad", unit.Squad.attrib["href"]))
				continue

	ret = list(set(ret))

	return ret

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
