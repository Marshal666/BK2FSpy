import os


def full_path(path: str):
	return os.path.abspath(path).lower().replace("\\", "/")


def formatted_path(path: str):
	return path.lower().replace("\\", "/")


def decode_bytes_string(string: bytes):
	encoding = "utf-8"
	# UTF-16 LE BOM detection
	if string[0] == 255 and string[1] == 254:
		encoding = "utf-16-le"
	return string.decode(encoding)
