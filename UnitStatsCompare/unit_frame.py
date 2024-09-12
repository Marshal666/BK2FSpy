import tkinter as tk
from tkinter import *
from tkinter import messagebox
import bk2_xml_utils
from unit_comparer import AttackDirection
from stats_compare import RowBuilder
import tk_utils
import comparison_frame
import os
import game_data_loader
from game_data_loader import StatsBonuses
import stats_compare_data as data
import recent_units_frame
import consts
from idlelib.tooltip import Hovertip


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

						init_unit_frame(unit_frame, title, units[index][1], reinf_type=unit_type)

						unit_path = units[index][1]
						unit_name = game_data_loader.get_unit_name(data.file_system, unit_path)
						unit_img = game_data_loader.get_unit_icon(data.file_system, unit_path)

						recent_units_frame.add_recent_unit(unit_name, unit_path, unit_img)
						comparison_frame.init_comparison_frame(data.comparison_frame)
						window.destroy()

						return

					def pin_unit_button_command(index: int):

						if units[index][0] != game_data_loader.MECH_UNIT_DEF:
							messagebox.showwarning("Not supported", "Infantry is currently not supported.")
							return

						unit_path = units[index][1]
						unit_name = game_data_loader.get_unit_name(data.file_system, unit_path)
						unit_img = game_data_loader.get_unit_icon(data.file_system, unit_path)

						recent_units_frame.add_recent_unit(unit_name, unit_path, unit_img)

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
							img.grid(row=index, column=col, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
							img.icon = icon
							col += 1
							i = int(index)
						(tk.Button(frame, text=f"unit{index}:", command=lambda ix=i: select_unit_button_command(ix))
						 .grid(row=index, column=col, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W))
						col += 1
						(tk.Button(frame, text="🖈", command=lambda ix=i: pin_unit_button_command(ix))
						 .grid(row=index, column=col, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W))
						col += 1
						tk.Label(frame, text=unit).grid(row=index, column=col, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

					return

				tk_utils.clear_frame_children(frame)

				nation_inx = nations.index(nation_option.get())
				tech_level_inx = tech_levels.index(tech_level_option.get())

				reinfs = game_data_loader.get_nation_reinfs(data.file_system, nation_inx, tech_level_inx)

				if reinfs is None or len(reinfs) == 0:
					tk.Label(frame, text="No reinfs found").pack()
					return

				tk.Label(frame, text="Reinf Type: ").grid(row=0, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

				reinf_option = tk.StringVar()
				reinf_option.set(reinfs[0])

				reinf_options = tk.OptionMenu(frame, reinf_option, *reinfs, command=update_units_in_reinf)
				reinf_options.grid(row=0, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

				units_frame = tk.Frame(frame)
				units_frame.grid(row=1, column=0, columnspan=3, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

				frame.columnconfigure(1, weight=1)

				update_units_frame(units_frame)

				return

			nations = game_data_loader.get_game_nations(data.file_system)
			tech_levels = game_data_loader.get_game_tech_levels(data.file_system)

			if nations is None:
				tk.Label(option_frame, text="No Nations").grid(row=0, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
				return

			if tech_levels is None:
				tk.Label(option_frame, text="No Tech Levels").grid(row=0, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
				return

			tk.Label(option_frame, text="Select Nation: ").grid(row=0, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

			nation_option = tk.StringVar()
			nation_option.set(nations[0])

			nation_options = tk.OptionMenu(option_frame, nation_option, *nations, command=nation_pick_command)
			nation_options.grid(row=0, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

			tk.Label(option_frame, text="Select Tech Level: ").grid(row=1, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

			tech_level_option = tk.StringVar()
			tech_level_option.set(tech_levels[0])

			tech_level_options = tk.OptionMenu(option_frame, tech_level_option, *tech_levels, command=tech_level_pick_command)
			tech_level_options.grid(row=1, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

			option_frame.columnconfigure(1, weight=1)

			reinf_pick_frame = tk.Frame(option_frame)
			reinf_pick_frame.grid(row=2, column=0, columnspan=2, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=EW)

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

	tk.Label(window, text="Where to get the unit from: ").grid(row=0, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

	option_menu = tk.OptionMenu(window, selected_option, *consts.UNIT_SELECT_OPTIONS, command=option_selected_command)
	option_menu.grid(row=0, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

	option_frame = tk.Frame(window, bd=2, relief=tk.SUNKEN)
	option_frame.grid(row=1, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2, sticky=EW)

	option_selected_command(selected_option.get())

	window.columnconfigure(1, weight=1)

	window.grab_set()  # Prevent interaction with the original window until this one is closed
	window.focus_set()  # Give focus to the new window

	return


def unit_is_aviation(unit_xml) -> bool:

	if unit_xml.DBtype.text.strip() in consts.DB_AVIA_TYPES and unit_xml.UnitType.text.strip() in consts.UNIT_AVIA_TYPES:
		return True

	return False


def init_unit_frame(frame: tk.Frame, title: str, unit: str = None, selected_weapon: StringVar = None, reinf_type: str = None):

	def on_weapon_shell_changed_command(arg):
		weapon_index = frame.weapon_names.index(arg)
		weapons_frame = frame.weapons_frame
		weapon_stats = frame.weapons_data.get_weapon_stats(weapon_index)
		frame.shell_stats = shell_stats = frame.weapons_data.get_shell_stats(weapon_index)
		weapon_shell = frame.unit_stats.WeaponsShells[weapon_index]

		tk_utils.clear_frame_children(weapons_frame)

		row_builder = RowBuilder()

		(tk.Label(weapons_frame, text=f"Weapon: {frame.weapon_names[weapon_index]}").
		 grid(row=row_builder.current, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2))

		tk.Label(weapons_frame, text="Dispersion: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		weapon_dispersion = tk_utils.create_float_entry(weapons_frame, weapon_shell.Dispersion, width=7)
		weapon_dispersion.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		tk.Label(weapons_frame, text="Range: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		weapon_ranges = tk_utils.create_2x_float_entry(weapons_frame, weapon_shell.RangeMin, weapon_shell.RangeMax,
													   "Min: ", ", Max:", width1=5, width2=5)
		weapon_ranges.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		tk.Label(weapons_frame, text="Aim Time:").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

		aim_time = tk_utils.create_float_entry(weapons_frame, weapon_shell.AimingTime, width=7)
		aim_time.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		tk.Label(weapons_frame, text="Ammo Per Burst:").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

		ammo_per_burst = tk_utils.create_int_entry(weapons_frame, weapon_shell.AmmoPerBurst, 6)
		ammo_per_burst.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		(tk.Label(weapons_frame, text=f"Shell[{frame.weapons_data.get_shell_index(weapon_index)}]").
		 grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2))

		area1, area2 = weapon_shell.Area, weapon_shell.Area2

		tk.Label(weapons_frame, text="Area Damages: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		weapon_areas = tk_utils.create_2x_float_entry(weapons_frame, area1, area2, "Area1: ", "Area2: ", width1=6, width2=6)
		weapon_areas.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		tk.Label(weapons_frame, text="Damage: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		weapon_damages = tk_utils.create_2x_float_entry(weapons_frame,
														weapon_shell.DamagePower,
														weapon_shell.DamageRandom,
														"", "±", "", width1=6, width2=6)
		weapon_damages.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		tk.Label(weapons_frame, text="").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		damage_min, damage_max = weapon_shell.min_max_damage
		weapon_min_max_damage = tk.Label(weapons_frame, text=f"Min: {damage_min}, Max: {damage_max}")
		frame.weapon_min_max_damage = weapon_min_max_damage
		weapon_min_max_damage.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		tk.Label(weapons_frame, text="Piercing: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

		weapon_piercings = tk_utils.create_2x_float_entry(weapons_frame,
														  weapon_shell.Piercing,
														  weapon_shell.PiercingRandom,
														  "", "±", "", width1=6, width2=6)
		weapon_piercings.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		tk.Label(weapons_frame, text="").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		piercing_min, piercing_max = weapon_shell.min_max_piercing
		weapon_min_max_piercing = tk.Label(weapons_frame, text=f"Min: {piercing_min}, Max: {piercing_max}")
		frame.weapon_min_max_piercing = weapon_min_max_piercing
		weapon_min_max_piercing.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		fire_rate_label_text = tk.Label(weapons_frame, text="Fire Rate: ")
		fire_rate_label_text.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		Hovertip(fire_rate_label_text, "Rate of fire used for bursts (when AmmoPerBurst > 1)", 400)
		fire_rate_entry = tk_utils.create_float_entry(weapons_frame, weapon_shell.FireRate, 6)
		fire_rate_entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		relax_time_label_text = tk.Label(weapons_frame, text="Relax Time: ")
		relax_time_label_text.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		Hovertip(relax_time_label_text, "Actual reload time of the weapon", 400)
		relax_time_entry = tk_utils.create_float_entry(weapons_frame, weapon_shell.RelaxTime, 6)
		relax_time_entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		comparison_frame.init_comparison_frame(data.comparison_frame)

		return

	def place_armor_labels():

		start_row = frame.armor_labels_row

		for i, side_label in enumerate(frame.armor_side_labels):
			side_label.grid(row=start_row + i, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

		for i, armor_label in enumerate(frame.armor_labels):
			armor_label.grid(row=start_row + i, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		return

	def hide_armor_labels():

		for i, side_label in enumerate(frame.armor_side_labels):
			side_label.grid_forget()

		for i, armor_label in enumerate(frame.armor_labels):
			armor_label.grid_forget()

		return

	def create_armors_labels():

		armors_str = AttackDirection.get_str_values()

		frame.avg_armor_labels = []
		frame.armor_labels = []
		frame.armor_side_labels = []
		frame.armor_labels_row = row_builder.next

		armor_side_label = tk.Label(frame, text=f"Armor {armors_str[0]}: ")
		#armor_side_label.grid(row=frame.armor_labels_row, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		min_armor = frame.unit_stats.Armors[0][0]
		max_armor = frame.unit_stats.Armors[0][1]
		avg_armor = (min_armor.get() + max_armor.get()) / 2.0
		armor_label = tk_utils.create_2x_float_entry(frame, min_armor, max_armor, "Min: ", ", Max: ", f", Avg: {avg_armor}", 7, 7)
		#armor_label.grid(row=frame.armor_labels_row, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)
		frame.avg_armor_labels.append(armor_label.children["!label3"])
		frame.armor_labels.append(armor_label)
		frame.armor_side_labels.append(armor_side_label)

		for i, armor_side in enumerate(armors_str[1:]):
			armor_side_label = tk.Label(frame, text=f"Armor {armor_side}:")
			armor_side_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
			min_armor = frame.unit_stats.Armors[i+1][0]
			max_armor = frame.unit_stats.Armors[i+1][1]
			avg_armor = (min_armor.get() + max_armor.get()) / 2.0
			armor_label = tk_utils.create_2x_float_entry(frame, min_armor, max_armor, "Min: ", ", Max: ", f", Avg: {avg_armor}", 7, 7)
			#armor_label.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)
			frame.avg_armor_labels.append(armor_label.children["!label3"])
			frame.armor_labels.append(armor_label)
			frame.armor_side_labels.append(armor_side_label)

		if frame.show_armors:
			place_armor_labels()
		else:
			hide_armor_labels()

		return

	def redraw_frames():
		comparison_frame.init_comparison_frame(data.comparison_frame)
		# init_unit_frame(frame, title, unit, selected_weapon, True)

		# redraw avg armor labels
		avg_armor_labels = getattr(frame, "avg_armor_labels", [])
		for i, label in enumerate(avg_armor_labels):
			try :
				min_armor = frame.unit_stats.Armors[i][0].get()
				max_armor = frame.unit_stats.Armors[i][1].get()
			except Exception as e:
				break
			avg_armor = (min_armor + max_armor) / 2.0
			if label.winfo_exists():
				label.config(text=f", Avg: {avg_armor}")

		if not hasattr(frame, "weapon_names"):
			return

		if len(frame.unit_stats.WeaponsShells) < 1:
			return

		# redraw weapon min max stuff
		weapon_index = frame.weapon_names.index(frame.selected_weapon.get())
		if weapon_index >= len(frame.unit_stats.WeaponsShells):
			return

		weapon_shell = frame.unit_stats.WeaponsShells[weapon_index]

		if frame.weapon_min_max_damage.winfo_exists():
			damage_min, damage_max = weapon_shell.min_max_damage
			frame.weapon_min_max_damage.config(text=f"Min: {damage_min}, Max: {damage_max}")

		if frame.weapon_min_max_piercing.winfo_exists():
			piercing_min, piercing_max = weapon_shell.min_max_piercing
			frame.weapon_min_max_piercing.config(text=f"Min: {piercing_min}, Max: {piercing_max}")

		return

	def invert_armors_show():
		frame.show_armors = not frame.show_armors
		frame.show_armors_button.config(text="Show Armors ▶" if not frame.show_armors else "Hide Armors ▼")

		if frame.show_armors:
			place_armor_labels()
			return

		hide_armor_labels()

		return

	def create_avia_params_labels():

		frame.avia_labels = []
		frame.avia_entries = []

		frame.avia_params_labels_row = row_builder.next

		label = tk.Label(frame, text="Speed")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.Speed, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		label = tk.Label(frame, text="RotateSpeed")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.RotateSpeed, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		label = tk.Label(frame, text="TurnRadius")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.TurnRadius, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		label = tk.Label(frame, text="MaxHeight")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.MaxHeight, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		label = tk.Label(frame, text="DivingAngle")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.DivingAngle, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		label = tk.Label(frame, text="ClimbAngle")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.ClimbAngle, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		label = tk.Label(frame, text="TiltAngle")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.TiltAngle, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		label = tk.Label(frame, text="TiltAcceleration")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.TiltAcceleration, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		label = tk.Label(frame, text="TiltSpeed")
		label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		entry = tk_utils.create_float_entry(frame, frame.unit_stats.TiltSpeed, 7)
		entry.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		frame.avia_labels.append(label)
		frame.avia_entries.append(entry)

		if show_avia_params:
			show_avia_params_labels()
		else:
			hide_avia_params_labels()

		return

	def show_avia_params_labels():

		start_row = frame.avia_params_labels_row

		for i, label in enumerate(frame.avia_labels):
			label.grid(row=start_row + i, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

		for i, entry in enumerate(frame.avia_entries):
			entry.grid(row = start_row + i, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

		return

	def hide_avia_params_labels():

		for label in frame.avia_labels:
			label.grid_forget()

		for entry in frame.avia_entries:
			entry.grid_forget()

		return

	def invert_avia_show():

		frame.show_avia_params = not frame.show_avia_params
		show_avia_params = frame.show_avia_params

		frame.show_avia_params_button.config(text="Show Avia Params ▶" if not show_avia_params else "Hide Avia Params ▼")

		if show_avia_params:
			show_avia_params_labels()
		else:
			hide_avia_params_labels()

		return

	tk_utils.clear_frame_children(frame)

	row_builder = RowBuilder()

	frame.title = title
	frame.title_text = tk.Label(frame, text=title, width=15, font=("Arial", 24, "bold"))
	frame.title_text.grid(row=row_builder.current, column=0, padx=10, pady=consts.PAD_Y, sticky=EW, columnspan=2)

	frame.get_unit_button = (
		tk.Button(frame, text="Select unit...", command=lambda: select_unit_command(frame, title), width=22))
	frame.get_unit_button.grid(row=row_builder.next, column=0, padx=15, pady=10, columnspan=2)

	frame.unit_path = None

	if not unit or not unit.strip():
		tk_utils.disable_frame(frame)
		return

	frame.unit_path = unit
	frame.unit_dir = os.path.dirname(bk2_xml_utils.format_href(unit))
	frame.unit_stats_xml = game_data_loader.get_unit_xml_stats(data.file_system, unit)
	frame.unit_stats = game_data_loader.UnitStats.from_xml_object(
		frame.unit_stats_xml,
		data.file_system,
		lambda: redraw_frames(),
		frame.unit_path)
	frame.has_weapons = False

	if reinf_type:
		frame.unit_stats.ReinfType.set(reinf_type)

	frame.unit_icon = game_data_loader.get_unit_icon(data.file_system, unit)
	frame.icon = tk.Label(frame, image=frame.unit_icon, width=48, height=48)
	frame.icon.grid(row=row_builder.current, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2)

	frame.unit_name = tk.Label(frame, text=game_data_loader.get_unit_name(data.file_system, frame.unit_path))
	frame.unit_name.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2)

	frame.get_unit_button.grid(row=row_builder.next, column=0, padx=15, pady=10, columnspan=2)

	weapon_selection_row = row_builder.next

	tk.Label(frame, text="Abilities:").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	abilities_frame = tk_utils.create_ability_entry(frame, frame.unit_stats)
	abilities_frame.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	tk.Label(frame, text="Entrenched:").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	(tk_utils.create_toggle_button(frame, frame.unit_stats.Entrenched,
								  "Entrenched ✅", "Not Entrenched ❎")
	 .grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E))

	tk.Label(frame, text="Unit Level:").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	(tk.OptionMenu(frame, frame.unit_stats.UnitLevel, *["1", "2", "3", "4"]).
	 grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E))

	tk.Label(frame, text="Reinf Type:").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	(tk.OptionMenu(frame, frame.unit_stats.ReinfType, *game_data_loader.reinf_types)
	 .grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E))

	max_hp_label = tk.Label(frame, text="MaxHP:")
	max_hp_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

	max_hp = tk_utils.create_float_entry(frame, frame.unit_stats.MaxHP)
	max_hp.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	aabb_coef_label = tk.Label(frame, text="AABBCoef:")
	aabb_coef_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	aabb_coef = tk_utils.create_float_entry(frame, frame.unit_stats.SmallAABBCoeff)
	aabb_coef.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	aabb_half_label = tk.Label(frame, text="AABB Half Size:")
	aabb_half_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

	aabb_half = tk_utils.create_2x_float_entry(frame, frame.unit_stats.AABBHalfSize_x, frame.unit_stats.AABBHalfSize_y,
											   "x: ", ", y: ", "", 6, 6)
	aabb_half.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	aabb_center_label = tk.Label(frame, text="AABB Center:")
	aabb_center_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)

	aabb_center = tk_utils.create_2x_float_entry(frame, frame.unit_stats.AABBCenter_x, frame.unit_stats.AABBCenter_y,
											   "x: ", ", y: ", "", 6, 6)
	aabb_center.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	show_armors = getattr(frame, "show_armors", False)
	frame.show_armors = show_armors
	show_armors_button_row = row_builder.next

	create_armors_labels()

	show_armors_button = tk.Button(frame, text="Show Armors ▶" if not show_armors else "Hide Armors ▼",
								   command=lambda: invert_armors_show())
	frame.show_armors_button = show_armors_button
	show_armors_button.grid(row=show_armors_button_row, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2, sticky=W)

	if unit_is_aviation(frame.unit_stats_xml):
		frame.show_avia_params = getattr(frame, "show_avia_params", False)
		show_avia_params = frame.show_avia_params
		frame.show_avia_params_button = tk.Button(frame, text="Show Avia Params ▶" if not show_avia_params else "Hide Avia Params ▼",
												  command=lambda : invert_avia_show())
		frame.show_avia_params_button.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		create_avia_params_labels()

	frame.weapons_frame = tk.Frame(frame, bd=1)
	frame.weapons_frame.grid(row=row_builder.next, column=0, padx=0, pady=consts.PAD_Y, columnspan=2)

	frame.weapons_data = weapons_data = game_data_loader.UnitWeaponsData(data.file_system, frame.unit_stats_xml, unit)
	if weapons_data.weapon_count < 1:
		tk.Label(frame, text="No weapons").grid(row=weapon_selection_row, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2)
	else:
		frame.selected_weapon = weapon_selection = StringVar() if selected_weapon is None else selected_weapon
		frame.weapon_names = weapon_names = weapons_data.weapon_names
		weapon = weapon_names[weapons_data.best_piercing_shell_index]
		frame.has_weapons = True
		if selected_weapon is None:
			weapon_selection.set(weapon)
		tk.Label(frame, text="Weapon/Shell:").grid(row=weapon_selection_row, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
		frame.weapon_option = tk.OptionMenu(frame, weapon_selection, *weapon_names,
											command=on_weapon_shell_changed_command)
		frame.weapon_option.grid(row=weapon_selection_row, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)
		on_weapon_shell_changed_command(weapon_selection.get())

	frame.columnconfigure(0, weight=1)
	frame.columnconfigure(1, weight=1)

	return


def get_stacked_unit_bonuses(frame: tk.Frame):
	ret = StatsBonuses()

	bonuses = getattr(frame, "stats_bonuses", None)
	if not bonuses:
		return ret

	for bonus in bonuses:
		ret += bonus

	return ret
