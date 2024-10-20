from appdirs import user_data_dir
from consts import APP_NAME, APP_AUTHOR
import os
import copy
import json

CAPACITY = 16
RECENT_ITEMS_FILE = 'recent_items.json'

__recent_items: list[list[str]] = []

data_dir = user_data_dir(APP_NAME, APP_AUTHOR)
os.makedirs(data_dir, exist_ok=True)

recent_items_path = os.path.join(data_dir, RECENT_ITEMS_FILE)

def load_recent_items():

	global __recent_items

	if not os.path.exists(recent_items_path):
		with open(recent_items_path, 'w') as recent_items_file:
			json.dump(__recent_items, recent_items_file)

	with open(recent_items_path, 'r') as recent_items_file:
		__recent_items = json.load(recent_items_file)

	return


def save_recent_items():

	global __recent_items

	with open(recent_items_path, 'w') as recent_items_file:
		json.dump(__recent_items, recent_items_file)

	return


def get_recent_items():
	return copy.deepcopy(__recent_items)


def add_recent_item(item: list[str]):

	if item in __recent_items:
		return

	__recent_items.append(item)

	while len(__recent_items) > CAPACITY:
		__recent_items.pop(0)

	save_recent_items()

	return


def clear_recent_items():

	__recent_items.clear()

	save_recent_items()
