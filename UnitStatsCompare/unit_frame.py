import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
import bk2_xml_utils
from UnitStatsCompare.unit_comparer import AttackDirection
from stats_compare import RowBuilder
import tk_utils
import comparison_frame
import os
import game_data_loader
import stats_compare_data as data
import consts

def select_unit_command(unit_frame: tk.Frame, title: str):

	def option_selected_command(arg):

		tk_utils.clear_frame_children(option_frame)

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
						comparison_frame.init_comparison_frame(data.comparison_frame)
						window.destroy()

						return

					tk_utils.clear_frame_children(frame)

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

				tk_utils.clear_frame_children(frame)

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

def init_unit_frame(frame: tk.Frame, title: str, unit: str = None, selected_weapon: StringVar = None):

	def on_weapon_shell_changed_command(arg):
		weapon_index = frame.weapon_names.index(arg)
		weapons_frame = frame.weapons_frame
		weapon_stats = frame.weapons_data.get_weapon_stats(weapon_index)
		frame.shell_stats = shell_stats = frame.weapons_data.get_shell_stats(weapon_index)

		tk_utils.clear_frame_children(weapons_frame)

		row_builder = RowBuilder()

		(tk.Label(weapons_frame, text=f"Weapon: {frame.weapon_names[weapon_index]}").
		 grid(row=row_builder.current, column=0, padx=5, pady=5, columnspan=2))

		tk.Label(weapons_frame, text="Dispersion: ").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		(tk.Label(weapons_frame, text=float(weapon_stats.Dispersion))
		 .grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E))

		tk.Label(weapons_frame, text="Range: ").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
		(tk.Label(weapons_frame, text=f"Min: {float(weapon_stats.RangeMin)}, Max: {float(weapon_stats.RangeMax)}")
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

		comparison_frame.init_comparison_frame(data.comparison_frame)

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

	tk_utils.clear_frame_children(frame)

	row_builder = RowBuilder()

	frame.title = tk.Label(frame, text=title, width=15, font=("Arial", 24, "bold"))
	frame.title.grid(row=row_builder.current, column=0, padx=10, pady=5, sticky=EW, columnspan=2)

	frame.get_unit_button = (
		tk.Button(frame, text="Select unit...", command=lambda: select_unit_command(frame, title), width=22))
	frame.get_unit_button.grid(row=row_builder.next, column=0, padx=15, pady=10, columnspan=2)

	frame.unit_path = None

	if not unit or not unit.strip():
		tk_utils.disable_frame(frame)
		return

	frame.unit_path = unit
	frame.unit_dir = os.path.dirname(bk2_xml_utils.format_href(unit))
	frame.unit_stats = game_data_loader.get_unit_stats(data.file_system, unit)
	frame.has_weapons = False

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
		frame.has_weapons = True
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