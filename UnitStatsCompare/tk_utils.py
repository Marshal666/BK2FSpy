from tkinter import *
import tkinter as tk
import game_data_loader
from idlelib.tooltip import Hovertip
import consts

class RowBuilder:

	def __init__(self, value: int=0):
		self.__value = value

	@property
	def next(self):
		self.__value += 1
		return self.__value

	@property
	def current(self):
		return self.__value


def set_entry_text(entry: Entry, text: str):
	entry.delete(0, END)
	entry.insert(0, text)


def disable_frame(frame):
	for widget in frame.winfo_children():
		if isinstance(widget, (tk.Button, tk.Entry, tk.Checkbutton, tk.Radiobutton, tk.Spinbox, tk.Label)):
			widget.config(state='disabled')


def enable_frame(frame):
	for widget in frame.winfo_children():
		if isinstance(widget, (tk.Button, tk.Entry, tk.Checkbutton, tk.Radiobutton, tk.Spinbox,tk.Label)):
			widget.config(state='normal')


def clear_frame_children(frame):
	for widget in frame.winfo_children():
		widget.destroy()


def validate_integer_input(char):
	if char.isdigit() or char == "":
		return True
	else:
		return False


########################################################################################################################


def scaler_with_entry(root, variable: DoubleVar | IntVar, _from: float | int, _to: float | int, command) -> Widget:

	def validate_change(var, index, mode):

		if isinstance(var, DoubleVar):
			try:
				value = float(var.get())
				var.set(value)
			except Exception:
				var.set(variable.get())
			return

		if isinstance(var, IntVar):
			try:
				value = int(var.get())
				var.set(value)
			except Exception:
				var.set(variable.get())
			return

	def command_wrap():
		command()
		return True

	variable.trace_add("write", validate_change)

	frame = tk.Frame(root)

	scaler = tk.Scale(frame, from_=_from, to=_to, variable=variable, command=lambda x: command(), orient=tk.HORIZONTAL)
	scaler.grid(row=0, column=0, sticky=tk.W)

	vcmd = frame.register(lambda x: command_wrap()), "%P"

	entry = tk.Entry(frame, textvariable=variable)#, validate="key", validatecommand=vcmd)
	entry.grid(row=0, column=1, sticky=tk.E)

	frame.columnconfigure(0, weight=2)
	frame.rowconfigure(0, weight=1)

	return frame


########################################################################################################################

def hex_to_rgb(hex_color):
	hex_color = hex_color.lstrip('#')
	return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_color):
	return '#{:02x}{:02x}{:02x}'.format(*rgb_color)


def lerp_color(color1, color2, t):
	t = max(0, min(t, 1))  # Ensure t is clamped between 0 and 1
	rgb1 = hex_to_rgb(color1)
	rgb2 = hex_to_rgb(color2)
	lerped_rgb = tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(rgb1, rgb2))
	return rgb_to_hex(lerped_rgb)

########################################################################################################################


def is_float(new_value):
	if new_value == "":
		return True
	try:
		float(new_value)
		return True
	except ValueError:
		return False


def is_int(new_value):
	if new_value == "":
		return True
	try:
		int(new_value)
		return True
	except ValueError:
		return False



def create_float_entry(root, variable: DoubleVar, width=10):

	vcmd = (root.register(is_float), "%P")

	entry = tk.Entry(root, textvariable=variable, width=width, validate="key", validatecommand=vcmd)

	return entry


def create_int_entry(root, variable: IntVar, width=10):

	vcmd = (root.register(is_int), "%P")

	entry = tk.Entry(root, textvariable=variable, width=width, validate="key", validatecommand=vcmd)

	return entry



def create_2x_float_entry(root, variable1: DoubleVar, variable2: DoubleVar, text_before: str = "", text_middle: str = "", text_after: str = "", width1: int = 10, width2: int = 10):

	ret = tk.Frame(root)

	vcmd = (root.register(is_float), "%P")

	tk.Label(ret, text=text_before).grid(row=0, column=0)

	tk.Entry(ret, textvariable=variable1, validate="key", validatecommand=vcmd, width=width1).grid(row=0, column=1)

	tk.Label(ret, text=text_middle).grid(row=0, column=2)

	tk.Entry(ret, textvariable=variable2, validate="key", validatecommand=vcmd, width=width2).grid(row=0, column=3)

	tk.Label(ret, text=text_after).grid(row=0, column=4)

	return ret


def create_toggle_image_button(root, variable: BooleanVar, on_image, off_image, on_text, off_text):

	def toggle():
		variable.set(not variable.get())

		if variable.get():
			ret.config(image=on_image) if on_image is not None else ret.config(text=on_text)
			return

		ret.config(image=off_image) if off_image is not None else ret.config(text=off_text)
		return

	image = on_image if variable.get() else off_image
	text = on_text if variable.get() else off_text

	ret = tk.Button(root, command=toggle, image=image, text=text if image is None else "")

	return ret


def create_toggle_button(root, variable: BooleanVar, on_text, off_text):

	def toggle():
		variable.set(not variable.get())
		ret.config(text=on_text) if variable.get() else ret.config(text=off_text)

	ret = tk.Button(root, command=toggle, text=on_text if variable.get() else off_text)

	return ret


def create_ability_entry(root, unit_stats: game_data_loader.UnitStats):

	ret = tk.Frame(root)

	if len(unit_stats.Abilities) < 1:
		tk.Label(ret, text="No Special Abilities").grid(row=0, column=0)
		return ret

	for i, ability in enumerate(unit_stats.Abilities):
		on_text = ability.Name + "_ON"
		off_text = ability.Name + "_OFF"

		image_enabled = ability.Icons[0]
		image_disabled = ability.Icons[1]

		variable = ability.Enabled

		button = create_toggle_image_button(ret, variable, image_enabled, image_disabled, on_text, off_text)
		desc = f"{ability.Name}"
		stats_bonuses = getattr(ability, "StatsBonus", None)
		if stats_bonuses:
			desc += f"\n\n{ability.StatsBonus.format_to_desc()}"
			desc = desc.strip()
		Hovertip(button, text=desc, hover_delay=400)
		button.grid(row=0, column=i, padx=2, pady=2, sticky=tk.W)

	return ret

def create_2x_labels(frame: tk.Frame, text1: str, text2: str, row: int, padx=consts.PAD_X, pady=consts.PAD_Y):

	tk.Label(frame, text=text1).grid(row=row, column=0, padx=padx, pady=pady, sticky=tk.W)

	tk.Label(frame, text=text2).grid(row=row, column=1, padx=padx, pady=pady, sticky=tk.E)

	return