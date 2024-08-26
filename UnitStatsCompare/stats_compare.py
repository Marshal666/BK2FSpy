import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
from enum import Enum
import bk2_xml_utils
import consts
import stats_compare_data as data
from console_logger import ConsoleLogger
from folder_system import FolderSystem
from pak_loader import PakLoader
from virtual_file_system import VirtualFileSystem
import game_data_loader
import unit_comparer
from unit_comparer import AttackDirection


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


def on_file_system_loaded():
	reset_unit_frames(data.attacker_frame, data.comparison_frame, data.defender_frame, True)
	return

def open_game_folders_command():

	def open_game_folder_command():
		folder = filedialog.askdirectory()
		set_entry_text(game_folder_entry, folder)
		return

	def open_mod_folder_command():
		folder = filedialog.askdirectory()
		set_entry_text(mod_folder_entry, folder)
		return

	def open_given_folders_command():

		if not game_folder_entry.get().strip():
			messagebox.showwarning("Warning", "Please select a game folder")
			return

		game_folder = game_folder_entry.get().strip()
		mod_folder = mod_folder_entry.get().strip()

		paths = { game_folder, mod_folder }
		if "" in paths:
			paths.remove("")

		for path in paths:
			if not os.path.isdir(path):
				messagebox.showerror("Error", f"Invalid path: \"{path}\"")
				return

		paths = list(paths)

		logger = ConsoleLogger()

		dir0 = FolderSystem(paths[0])
		pak0 = PakLoader(paths[0], logger)

		data.file_system = VirtualFileSystem(dir0)
		data.file_system.add_system(pak0)

		for i in range(1, len(paths)):
			paki = PakLoader(paths[i], logger)
			diri = FolderSystem(paths[i])
			data.file_system.add_system(diri)
			data.file_system.add_system(paki)

		window.destroy()
		on_file_system_loaded()

		messagebox.showinfo("Data Loaded", "Data was loaded successfully")
		return

	window = data.folders_pick = tk.Toplevel()
	window.title('Open game folders')
	window.geometry('640x120')
	window.minsize(480,110)

	tk.Label(window, text="Game folder: ").grid(row=0, column=0, padx=5, pady=5, sticky=W)
	game_folder_entry = tk.Entry(window, width=80)
	game_folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
	(tk.Button(window, text="...", width=5, command=open_game_folder_command)
	 .grid(row=0, column=2, padx=5, pady=5, sticky=E))

	tk.Label(window, text="Mod folder: ").grid(row=1, column=0, padx=5, pady=5, sticky=W)
	mod_folder_entry = tk.Entry(window, width=80)
	mod_folder_entry.grid(row=1, column=1, padx=5, pady=5, sticky=EW)
	(tk.Button(window, text="...", width=5, command=open_mod_folder_command)
	 .grid(row=1, column=2, padx=5, pady=5, sticky=E))

	open_folders_button = tk.Button(window, text="Open Given Folders", command=open_given_folders_command)
	open_folders_button.grid(row=2, column=1, padx=5, pady=5)

	window.grid_columnconfigure(1, weight=1)
	window.grid_columnconfigure(0, weight=0)
	window.grid_columnconfigure(2, weight=0)

	window.grab_set()  # Prevent interaction with the original window until this one is closed
	window.focus_set()  # Give focus to the new window
	#window.transient(window)  # Make the new window always on top of the original

	return


def select_unit_command(unit_frame: tk.Frame, title: str):

	def option_selected_command(arg):

		clear_frame_children(option_frame)

		if arg == consts.UNIT_SELECT_OPTIONS[0]:
			# From MP

			def nation_pick_command(arg: StringVar):
				update_reinfs_frame(reinf_pick_frame)
				return

			def tech_level_pick_command(arg: StringVar):
				update_reinfs_frame(reinf_pick_frame)
				return

			def update_reinfs_frame(frame: tk.Frame):

				def update_units_in_reinf(arg: StringVar):
					update_units_frame(units_frame)
					return

				def update_units_frame(frame: tk.Frame):

					def select_unit_button_command(index: int):

						if units[index][0] != game_data_loader.MECH_UNIT_DEF:
							messagebox.showwarning("Not supported", "Infantry is currently not supported.")
							return

						init_unit_frame(unit_frame, title, units[index][1])
						window.destroy()

						return

					clear_frame_children(frame)

					unit_type = reinf_option.get()

					units = game_data_loader.get_nation_reinf_units(data.file_system, nation_inx, tech_level_inx, unit_type)

					if units is None or len(units) == 0:
						tk.Label(frame, text="No units found").pack()
						return

					for index, unit in enumerate(units):
						col = 0
						icon = game_data_loader.get_unit_icon(data.file_system, unit[1])
						if icon is not None:
							img = tk.Label(frame, image=icon)
							img.grid(row=index, column=col, padx=5, pady=5, sticky=W)
							img.icon = icon
							col += 1
							i = int(index)
						(tk.Button(frame, text=f"unit{index}:", command=lambda ix=i: select_unit_button_command(ix))
						 .grid(row=index, column=col, padx=5, pady=5, sticky=W))
						col += 1
						tk.Label(frame, text=unit).grid(row=index, column=col, padx=5, pady=5, sticky=W)

					return

				clear_frame_children(frame)

				nation_inx = nations.index(nation_option.get())
				tech_level_inx = tech_levels.index(tech_level_option.get())

				reinfs = game_data_loader.get_nation_reinfs(data.file_system, nation_inx, tech_level_inx)

				if reinfs is None or len(reinfs) == 0:
					tk.Label(frame, text="No reinfs found").pack()
					return

				tk.Label(frame, text="Reinf Type: ").grid(row=0, column=0, padx=5, pady=5, sticky=W)

				reinf_option = tk.StringVar()
				reinf_option.set(reinfs[0])

				reinf_options = tk.OptionMenu(frame, reinf_option, *reinfs, command=update_units_in_reinf)
				reinf_options.grid(row=0, column=1, padx=5, pady=5, sticky=E)

				units_frame = tk.Frame(frame)
				units_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=W)

				frame.columnconfigure(1, weight=1)

				update_units_frame(units_frame)

				return

			nations = game_data_loader.get_game_nations(data.file_system)
			tech_levels = game_data_loader.get_game_tech_levels(data.file_system)

			if nations is None:
				tk.Label(option_frame, text="No Nations").grid(row=0, column=0, padx=5, pady=5, sticky=W)
				return

			if tech_levels is None:
				tk.Label(option_frame, text="No Tech Levels").grid(row=0, column=0, padx=5, pady=5, sticky=W)
				return

			tk.Label(option_frame, text="Select Nation: ").grid(row=0, column=0, padx=5, pady=5, sticky=W)

			nation_option = tk.StringVar()
			nation_option.set(nations[0])

			nation_options = tk.OptionMenu(option_frame, nation_option, *nations, command=nation_pick_command)
			nation_options.grid(row=0, column=1, padx=5, pady=5, sticky=E)

			tk.Label(option_frame, text="Select Tech Level: ").grid(row=1, column=0, padx=5, pady=5, sticky=W)

			tech_level_option = tk.StringVar()
			tech_level_option.set(tech_levels[0])

			tech_level_options = tk.OptionMenu(option_frame, tech_level_option, *tech_levels, command=tech_level_pick_command)
			tech_level_options.grid(row=1, column=1, padx=5, pady=5, sticky=E)

			option_frame.columnconfigure(1, weight=1)

			reinf_pick_frame = tk.Frame(option_frame)
			reinf_pick_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=EW)

			update_reinfs_frame(reinf_pick_frame)

			pass
		elif arg == consts.UNIT_SELECT_OPTIONS[1]:
			# From files

			pass
		else:
			messagebox.showerror("What the fuck did you select??", "shit happened: bruh")

		return

	window = data.folders_pick = tk.Toplevel()
	window.title('Pick a game unit')
	window.geometry('800x500')
	window.minsize(480, 270)

	selected_option = tk.StringVar()
	selected_option.set(consts.UNIT_SELECT_OPTIONS[0])

	tk.Label(window, text="Where to get the unit from: ").grid(row=0, column=0, padx=5, pady=5, sticky=W)

	option_menu = tk.OptionMenu(window, selected_option, *consts.UNIT_SELECT_OPTIONS, command=option_selected_command)
	option_menu.grid(row=0, column=1, padx=5, pady=5, sticky=W)

	option_frame = tk.Frame(window, bd=2, relief=tk.SUNKEN)
	option_frame.grid(row=1, column=0, padx=5, pady=5, columnspan=2, sticky=EW)

	option_selected_command(selected_option.get())

	window.columnconfigure(1, weight=1)

	window.grab_set()  # Prevent interaction with the original window until this one is closed
	window.focus_set()  # Give focus to the new window

	return


def quit_command():
	data.root.quit()
	return


def init_unit_frame(frame: tk.Frame, title: str, unit: str = None, selected_weapon: StringVar = None):

	def on_weapon_shell_changed_command(arg):
		weapon_index = frame.weapon_names.index(arg)
		weapons_frame = frame.weapons_frame
		weapon_stats = frame.weapons_data.get_weapon_stats(weapon_index)
		frame.shell_stats = shell_stats = frame.weapons_data.get_shell_stats(weapon_index)

		clear_frame_children(weapons_frame)

		row_builder = RowBuilder()

		(tk.Label(weapons_frame, text=f"Weapon: {frame.weapon_names[weapon_index]}").
		 grid(row=row_builder.current, column=0, padx=5, pady=5, columnspan=2))

		tk.Label(weapons_frame, text="Dispersion: ").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		(tk.Label(weapons_frame, text=float(weapon_stats.Dispersion))
		 .grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E))

		tk.Label(weapons_frame, text="Aim Time:").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		(tk.Label(weapons_frame, text=float(weapon_stats.AimingTime))
		 .grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E))

		(tk.Label(weapons_frame, text=f"Shell[{frame.weapons_data.get_shell_index(weapon_index)}]").
		 grid(row=row_builder.next, column=0, padx=5, pady=5, columnspan=2))

		tk.Label(weapons_frame, text="Damage: ").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		(tk.Label(weapons_frame, text=f"{float(shell_stats.DamagePower)}±{float(shell_stats.DamageRandom)}").
		 grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E))
		tk.Label(weapons_frame, text="").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		damage_min, damage_max = frame.weapons_data.get_shell_damage_min_max(weapon_index)
		(tk.Label(weapons_frame, text=f"Min: {damage_min}, Max: {damage_max}")
		 .grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E))

		tk.Label(weapons_frame, text="Piercing: ").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		(tk.Label(weapons_frame, text=f"{float(shell_stats.Piercing)}±{float(shell_stats.PiercingRandom)}").
		 grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E))
		tk.Label(weapons_frame, text="").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		piercing_min, piercing_max = frame.weapons_data.get_shell_piercing_min_max(weapon_index)
		(tk.Label(weapons_frame, text=f"Min: {piercing_min}, Max: {piercing_max}")
		 .grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E))

		init_comparison_frame(data.comparison_frame)

		return

	def create_armors_labels(armors: list[tuple[float, float]]):

		def format_min_max(value: tuple[float, float]) -> str:
			return f"Min: {value[0]}, Max: {value[1]}, Avg: {(value[0] + value[1]) / 2.0}"

		armors_str = AttackDirection.get_str_values()

		armors_label = tk.Label(frame, text=f"Armor {armors_str[0]}: ")
		armors_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		armor_label = tk.Label(frame, text=f"{format_min_max(armors[0])}")
		armor_label.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

		for i, armor_side in enumerate(armors_str[1:]):
			tk.Label(frame, text=f"Armor {armor_side}:").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
			armor_label = tk.Label(frame, text=f"{format_min_max(armors[i+1])}")
			armor_label.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

		return

	clear_frame_children(frame)

	row_builder = RowBuilder()

	frame.title = tk.Label(frame, text=title, width=15, font=("Arial", 24, "bold"))
	frame.title.grid(row=row_builder.current, column=0, padx=10, pady=5, sticky=EW, columnspan=2)

	frame.get_unit_button = (
		tk.Button(frame, text="Select unit...", command=lambda: select_unit_command(frame, title), width=22))
	frame.get_unit_button.grid(row=row_builder.next, column=0, padx=15, pady=10, columnspan=2)

	frame.unit_path = None

	if not unit or not unit.strip():
		disable_frame(frame)
		return

	frame.unit_path = unit
	frame.unit_dir = os.path.dirname(bk2_xml_utils.format_href(unit))
	frame.unit_stats = game_data_loader.get_unit_stats(data.file_system, unit)

	frame.unit_icon = game_data_loader.get_unit_icon(data.file_system, unit)
	frame.icon = tk.Label(frame, image=frame.unit_icon, width=48, height=48)
	frame.icon.grid(row=row_builder.current, column=0, padx=5, pady=5, columnspan=2)

	frame.unit_name = tk.Label(frame, text=game_data_loader.get_unit_name(data.file_system, frame.unit_path))
	frame.unit_name.grid(row=row_builder.next, column=0, padx=5, pady=5, columnspan=2)

	frame.get_unit_button.grid(row=row_builder.next, column=0, padx=15, pady=10, columnspan=2)

	weapon_selection_row = row_builder.next

	max_hp_label = tk.Label(frame, text="MaxHP:")
	max_hp_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)

	max_hp = tk.Label(frame, text=game_data_loader.get_hp_stats(frame.unit_stats))
	max_hp.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	aabb_coef_label = tk.Label(frame, text="AABBCoef:")
	aabb_coef_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	aabb_coef = tk.Label(frame, text=game_data_loader.get_aabb_coef(frame.unit_stats))
	aabb_coef.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	aabb_half_label = tk.Label(frame, text="AABB Half Size:")
	aabb_half_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)

	aabb_half_value = game_data_loader.get_aabb_half(frame.unit_stats)
	aabb_half = tk.Label(frame, text=f"x: {aabb_half_value[0]}, y: {aabb_half_value[1]}")
	aabb_half.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	frame.armors = armors_value = game_data_loader.get_unit_armors(frame.unit_stats)
	create_armors_labels(armors_value)

	frame.weapons_frame = tk.Frame(frame, bd=1)
	frame.weapons_frame.grid(row=row_builder.next, column=0, padx=0, pady=5, columnspan=2)

	frame.weapons_data = weapons_data = game_data_loader.UnitWeaponsData(data.file_system, frame.unit_stats, unit)
	if weapons_data.weapon_count < 1:
		tk.Label(frame, text="No weapons").grid(row=weapon_selection_row, column=0, padx=5, pady=5, columnspan=2)
	else:
		frame.selected_weapon = weapon_selection = StringVar() if selected_weapon is None else selected_weapon
		frame.weapon_names = weapon_names = weapons_data.weapon_names
		weapon = weapon_names[weapons_data.best_piercing_shell_index]
		if selected_weapon is None:
			weapon_selection.set(weapon)
		tk.Label(frame, text="Weapon/Shell:").grid(row=weapon_selection_row, column=0, padx=5, pady=5, sticky=W)
		frame.weapon_option = tk.OptionMenu(frame, weapon_selection, *weapon_names,
											command=on_weapon_shell_changed_command)
		frame.weapon_option.grid(row=weapon_selection_row, column=1, padx=5, pady=5, sticky=E)
		on_weapon_shell_changed_command(weapon_selection.get())

	frame.columnconfigure(0, weight=1)
	frame.columnconfigure(1, weight=1)

	return

def init_comparison_frame(frame: tk.Frame):

	def swap_command():

		attacker_unit = None
		defender_unit = None

		if hasattr(data.attacker_frame, "unit_path"):
			attacker_unit = data.attacker_frame.unit_path

		if hasattr(data.defender_frame, "unit_path"):
			defender_unit = data.defender_frame.unit_path

		attacker_weapon = None
		defender_weapon = None

		if hasattr(data.attacker_frame, "selected_weapon"):
			attacker_weapon = data.attacker_frame.selected_weapon

		if hasattr(data.defender_frame, "selected_weapon"):
			defender_weapon = data.defender_frame.selected_weapon

		init_unit_frame(data.attacker_frame, consts.ATTACKER_FRAME_TITLE, defender_unit, defender_weapon)
		init_unit_frame(data.defender_frame, consts.DEFENDER_FRAME_TITLE, attacker_unit, attacker_weapon)

		enable_frame(data.attacker_frame)
		enable_frame(data.defender_frame)

		init_comparison_frame(frame)

		return

	clear_frame_children(frame)

	row_builder = RowBuilder()

	frame.grid_columnconfigure(0, weight=1)
	frame.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=N)
	frame.title = tk.Label(data.comparison_frame, text="Comparison", font=("Arial", 24, "bold"), width=20)
	frame.title.grid(row=row_builder.current, column=0, padx=5, pady=0, columnspan=2, sticky=EW)

	frame.switch_comparison_button = tk.Button(frame, text="<=Swap=>", width=16, command=swap_command)
	frame.switch_comparison_button.grid(row=row_builder.next, column=0, columnspan=2, padx=5, pady=5)

	attacker = getattr(data.attacker_frame, "unit_path", None)
	if attacker is None:
		(tk.Label(frame, text="No attacker for comparison")
		 .grid(row=row_builder.next, column=0, padx=5, pady=5, columnspan=2))
		return

	defender = getattr(data.defender_frame, "unit_path", None)
	if defender is None:
		(tk.Label(frame, text="No defender for comparison")
		 .grid(row=row_builder.next, column=0, padx=5, pady=5, columnspan=2))
		return

	attack_directions = AttackDirection.get_str_values()
	attack_direction = getattr(frame, "attack_direction", None)
	if attack_direction is None:
		frame.attack_direction = attack_direction = StringVar()
		attack_direction.set(attack_directions[0])

	attack_direction_label = tk.Label(frame, text="Attack Direction: ")
	attack_direction_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	attack_direction_menu = tk.OptionMenu(frame, attack_direction, *attack_directions,
										  command=lambda x: init_comparison_frame(frame))
	attack_direction_menu.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	piercing_probability_label = tk.Label(frame, text="Piercing Probability: ")
	piercing_probability_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	attacker_shell = data.attacker_frame.shell_stats
	defender = data.defender_frame.unit_stats
	side = AttackDirection[attack_direction.get()]
	piercing_probability = unit_comparer.get_piercing_probability(attacker_shell, defender, side)
	piercing = tk.Label(frame, text=f"{(piercing_probability*100):.2f}%")
	piercing.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)


	return

def reset_unit_frames(attacker_frame: tk.Frame, comparison_frame: tk.Frame, defender_frame: tk.Frame, enabled:bool):

	init_comparison_frame(comparison_frame)
	init_unit_frame(data.attacker_frame, consts.ATTACKER_FRAME_TITLE)
	init_unit_frame(data.defender_frame, consts.DEFENDER_FRAME_TITLE)

	if enabled:

		enable_frame(attacker_frame)
		enable_frame(comparison_frame)
		enable_frame(defender_frame)

		return

	disable_frame(attacker_frame)
	disable_frame(comparison_frame)
	disable_frame(defender_frame)

	return


def main():
	root = data.root = Tk()
	root.title('BK2 Unit Stats Compare')
	root.geometry("1280x900")
	root.minsize(800, 600)
	root.iconbitmap("icon.ico")

	data.menu_bar = tk.Menu(root)

	file_menu = tk.Menu(data.menu_bar, tearoff=0)
	file_menu.add_command(label="Open Game Folders", command=open_game_folders_command)
	file_menu.add_separator()
	file_menu.add_command(label="Quit", command=quit_command)
	data.menu_bar.add_cascade(label="File", menu=file_menu)

	data.attacker_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	data.attacker_frame.grid(row=0, column=0, padx=5, pady=5, sticky=NW)
	init_unit_frame(data.attacker_frame, consts.ATTACKER_FRAME_TITLE)

	data.defender_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	data.defender_frame.grid(row=0, column=2, padx=5, pady=5, sticky=NE)
	init_unit_frame(data.defender_frame, consts.DEFENDER_FRAME_TITLE)

	data.comparison_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	init_comparison_frame(data.comparison_frame)

	reset_unit_frames(data.attacker_frame, data.comparison_frame, data.defender_frame, False)

	#data.open_game_folders_button = ttk.Button(root, text="Open game folder(s)", command=open_game_folders)
	#data.open_game_folders_button.pack(anchor='nw', pady=10, padx=10)

	root.grid_columnconfigure(0, weight=1)
	root.grid_columnconfigure(1, weight=3)
	root.grid_columnconfigure(2, weight=1)

	root.config(menu=data.menu_bar)

	root.mainloop()
	return


if __name__ == "__main__":
	main()