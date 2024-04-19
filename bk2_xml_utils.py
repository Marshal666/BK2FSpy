import lxml.etree
from lxml import objectify
from lxml.etree import tostring
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
