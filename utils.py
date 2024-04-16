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


def is_slash(string: str):
	return string == "/" or string == "\\"


def tuple_sum(a: tuple, b: tuple):
	count = max(len(a), len(b))
	ret = [0 for i in range(count)]
	for i in range(count):
		tmp_sum = 0
		if i < len(a):
			tmp_sum += a[i]
		if i < len(b):
			tmp_sum += b[i]
		ret[i] = tmp_sum
	return tuple(ret)


def tuple_scalar_multiply(a: tuple, b: float):
	ret = list(a)
	for i in range(len(ret)):
		ret[i] *= b
	return tuple(ret)
