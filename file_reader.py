from folder_system import FolderSystem
from pak_loader import PakLoader
from console_logger import ConsoleLogger
from virtual_file_system import VirtualFileSystem
from enum import Enum


class Modes(Enum):
	PRINT_TO_CONSOLE = 1
	WRITE_TO_FILE = 2


game_path = r"C:\Program Files (x86)\Blitzkrieg 2 -  Total Conversion\Data"
mode = Modes.WRITE_TO_FILE
out_path = r"tex.dds"
file_path = r"Units/Technics/GB/Tanks/Churchill_MkV_Can/1_Texture.dds"


def print_to_console():
	global game_path

	logger = ConsoleLogger()
	folder = FolderSystem(game_path)
	fs = VirtualFileSystem(folder)
	pk = PakLoader(game_path, logger)
	fs.add_system(pk)

	global file_path
	print(fs.read_text_file(file_path))


def write_to_file():
	global game_path

	logger = ConsoleLogger()
	folder = FolderSystem(game_path)
	fs = VirtualFileSystem(folder)
	pk = PakLoader(game_path, logger)
	fs.add_system(pk)

	global file_path
	global out_path
	with open(out_path, "wb") as file:
		file.write(fs.read_file_bytes(file_path))


modes_dict = {Modes.PRINT_TO_CONSOLE: print_to_console, Modes.WRITE_TO_FILE: write_to_file}


def main():
	global mode
	modes_dict[mode]()
	return 0


if __name__ == "__main__":
	main()
