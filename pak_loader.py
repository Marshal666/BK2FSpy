import datetime
import typing
from folder_system import VirtualFileSystemBaseClass


class PakLoader(VirtualFileSystemBaseClass):

	# TODO
	def __init__(self, *args):
		pass

	def last_modify_time(self, path: str) -> datetime.datetime:
		pass

	def contains_file(self, path: str) -> bool:
		pass

	def __contains__(self, item):
		pass

	def open_file(self, item):
		pass

	def read_text_file(self, path: str):
		pass

	def read_file_bytes(self, path: str) -> bytes:
		pass

	def write_to_file(self, path: str, content: typing.Union[str, bytes, bytearray]):
		pass

	def get_source_file(self, path: str) -> str:
		pass

	def get_all_files(self) -> list[str]:
		pass