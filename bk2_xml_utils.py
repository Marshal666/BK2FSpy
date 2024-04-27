import lxml.etree
from lxml import objectify
from lxml.etree import tostring

import utils
from virtual_file_system_abstract import VirtualFileSystemBaseClass
from utils import is_slash
from logger_abstract import LoggerAbstract
import os


def load_xml_file(system: VirtualFileSystemBaseClass, path: str):
	content = system.read_file_bytes(path)
	return objectify.fromstring(content)


def save_object_as_xml(xml_object, system: VirtualFileSystemBaseClass, path: str):
	objectify.deannotate(xml_object)
	lxml.etree.cleanup_namespaces(xml_object)
	content = tostring(xml_object, pretty_print=True, doctype='<?xml version="1.0" encoding="UTF-8" ?>')
	if system is not None:
		system.write_to_file(path, content)
		return
	with open(path, "wb") as file:
		file.write(content)


def format_href(href: str, remove_extension=True):
	if not href.strip():
		return ""
	if is_slash(href[0]):
		href = href[1:]
	href = href.strip().replace("\\", "/").lower()
	if remove_extension and "#" in href:
		index = href.index("#")
		href = href if index < 0 else href[0:index]
	href = href.replace("\\", "/").lower()
	return href


def add_and_write_href_file(system: VirtualFileSystemBaseClass, href_element, file_path: str, file_content: bytes,
							abs_path: str = ""):
	full_path = os.path.join(abs_path, file_path)
	system.write_to_file(full_path, file_content)
	href_element.attrib["href"] = file_path


def add_root_directory(href: str, root_directory: str):
	href = href.replace("\\", "/").lower()
	if not root_directory:
		return href
	dir = os.path.join(root_directory.lower(), href).replace("\\", "/")
	return dir


def href_file_exists(href_object, system: VirtualFileSystemBaseClass, root_directory: str=None, remove_extension=True):
	href = href_object.attrib["href"]
	href = format_href(href, remove_extension)
	directory = add_root_directory(href, root_directory)
	if system.contains_file(directory):
		return True
	if system.contains_file(href):
		return True
	return False


def actual_path(path: str, system: VirtualFileSystemBaseClass, root_directory: str=None, remove_extension=True):
	path = format_href(path, remove_extension)
	directory = add_root_directory(path, root_directory)
	if system.contains_file(directory):
		return directory
	if system.contains_file(path):
		return path
	raise ValueError("href file not found")


def actual_href_path(href_object, system: VirtualFileSystemBaseClass, root_directory: str=None, remove_extension=True):
	href = href_object.attrib["href"]
	return actual_path(href, system, root_directory, remove_extension)


def href_get_file_contents(href_object, system: VirtualFileSystemBaseClass, root_directory: str=None,
							remove_extension=True, logger: LoggerAbstract=None):
	if not root_directory:
		root_directory = ""
	href = href_object.attrib["href"]
	href = format_href(href, remove_extension)
	if not href:
		return None
	directory = add_root_directory(href, root_directory)
	file_content = None
	try:
		file_content = system.read_text_file(directory)
	except Exception as e:
		logger.print(e) if logger is not None else None
	if file_content is not None:
		return file_content
	try:
		file_content = system.read_text_file(href)
	except Exception as e:
		logger.print(e) if logger is not None else None
	if file_content is not None:
		return file_content
	raise Exception(f"File: {href} not found!")


def href_get_binary_file_contents(href_object, system: VirtualFileSystemBaseClass, root_directory: str=None,
									remove_extension=True, logger: LoggerAbstract=None):
	if not root_directory:
		root_directory = ""
	href = href_object.attrib["href"]
	href = format_href(href, remove_extension)
	if not href:
		return None
	directory = add_root_directory(href, root_directory)
	binary_file_content = system.read_file_bytes(directory)
	if binary_file_content is not None:
		return binary_file_content
	binary_file_content = system.read_file_bytes(href)
	if binary_file_content is not None:
		return binary_file_content
	raise Exception(f"File: {href} not found!")


def href_read_xml_object(href_object, system: VirtualFileSystemBaseClass, root_directory: str=None,
						remove_extension=True, logger: LoggerAbstract=None):
	contents = href_get_file_contents(href_object, system, root_directory, remove_extension, logger)
	return objectify.fromstring(contents)


class VisualObjectReader:

	def __init__(self, system: VirtualFileSystemBaseClass, used_file_paths: set[str]=None):
		self.file_system = system
		self.xml_object = None
		self.root_directory = None
		self.used_file_paths = used_file_paths
		self.result: set[str] = None

	def add_used_file_path(self, href_element, root_directory: str=""):
		if self.used_file_paths:
			if type(href_element) is str and href_file_exists(href_element, self.file_system, root_directory):
				self.used_file_paths.add(actual_path(href_element, self.file_system, root_directory))
			self.used_file_paths.add(actual_href_path(href_element, self.file_system, root_directory))

	def read_binaries(self, xml_object, root_directory: str = "", element_path: str=""):
		self.xml_object = xml_object
		self.root_directory = root_directory
		self.result = set()

		# Damage levels
		for item in self.xml_object.DamageLevels.Item:
			self.read_object_graphics(item.VisObj, root_directory)

		# Visual Object
		self.read_object_graphics(xml_object.visualObject, root_directory)

		# info Visual Object
		self.read_object_graphics(xml_object.infoVisualObject, root_directory)

		# Animable Model
		self.read_object_graphics(xml_object.AnimableModel, root_directory)

		# Transportable Model
		self.read_object_graphics(xml_object.TransportableModel, root_directory)

		self.add_used_file_path(element_path, root_directory)
		self.add_used_file_path(xml_object.IconTexture, root_directory)
		self.add_used_file_path(xml_object.LocalizedNameFileRef, root_directory)
		self.add_used_file_path(xml_object.FullDescriptionFileRef, root_directory)

	def read_object_graphics(self, model_reference, root_directory: str= ""):
		if not href_file_exists(model_reference, self.file_system, root_directory):
			return
		graphic_xml = href_read_xml_object(model_reference, self.file_system, root_directory)
		for item in graphic_xml.Models.Item:
			self.read_model(item, root_directory)
		self.add_used_file_path(model_reference, root_directory)


	def read_model(self, vis_obj_reference, root_directory: str= ""):
		if not href_file_exists(vis_obj_reference, self.file_system, root_directory):
			return
		model_xml = href_read_xml_object(vis_obj_reference, self.file_system, root_directory)
		for item in model_xml.Materials.Item:
			self.read_material(item, root_directory)
			self.add_used_file_path(item, root_directory)
		self.read_geometry(model_xml.Geometry, root_directory)
		self.read_skeleton(model_xml.Skeleton, root_directory)

		self.add_used_file_path(model_xml.Skeleton, root_directory)
		self.add_used_file_path(model_xml.Geometry, root_directory)
		self.add_used_file_path(vis_obj_reference, root_directory)

	def read_material(self, material_reference, root_directory: str= ""):
		if not href_file_exists(material_reference, self.file_system, root_directory):
			return
		material_xml = href_read_xml_object(material_reference, self.file_system, root_directory)
		material_texture = href_read_xml_object(material_xml.Texture, self.file_system, root_directory)
		self.result.add(actual_href_path(material_texture.DestName, self.file_system, root_directory))
		self.add_used_file_path(material_xml.Texture, root_directory)
		self.add_used_file_path(material_reference, root_directory)


	def read_geometry(self, geometry_reference, root_directory: str= ""):
		if not href_file_exists(geometry_reference, self.file_system, root_directory):
			return
		geometry_xml = href_read_xml_object(geometry_reference, self.file_system, root_directory)
		self.result.add(f"bin/geometries/{geometry_xml.uid}")
		ai_geometry = href_read_xml_object(geometry_xml.AIGeometry, self.file_system, root_directory)
		self.result.add(f"bin/ai_geometries/{ai_geometry.uid}")
		self.add_used_file_path(geometry_xml.AIGeometry, root_directory)
		self.add_used_file_path(geometry_reference, root_directory)

	def read_skeleton(self, skeleton_reference, root_directory: str= ""):
		if not href_file_exists(skeleton_reference, self.file_system, root_directory):
			return
		skeleton_xml = href_read_xml_object(skeleton_reference, self.file_system, root_directory)
		self.result.add(f"bin/skeletons/{skeleton_xml.uid}")
		for item in skeleton_xml.Animations.Item:
			animation_xml = href_read_xml_object(item, self.file_system, root_directory)
			self.result.add(f"bin/animations/{animation_xml.uid}")
			self.add_used_file_path(item, root_directory)
		self.add_used_file_path(skeleton_reference, root_directory)
