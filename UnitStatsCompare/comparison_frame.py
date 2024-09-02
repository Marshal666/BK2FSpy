import  stats_compare_data as data
import tkinter as tk
from tkinter import *
import consts
import tk_utils
from UnitStatsCompare import unit_comparer
from UnitStatsCompare.game_data_loader import UnitStats
from UnitStatsCompare.unit_comparer import AttackDirection
from tk_utils import RowBuilder
from idlelib.tooltip import Hovertip
import unit_frame

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

		unit_frame.init_unit_frame(data.attacker_frame, consts.ATTACKER_FRAME_TITLE, defender_unit, defender_weapon)
		unit_frame.init_unit_frame(data.defender_frame, consts.DEFENDER_FRAME_TITLE, attacker_unit, attacker_weapon)

		tk_utils.enable_frame(data.attacker_frame)
		tk_utils.enable_frame(data.defender_frame)

		init_comparison_frame(frame)

		return

	tk_utils.clear_frame_children(frame)

	frame.grid_columnconfigure(0, weight=1)
	frame.grid(row=0, column=1, padx=5, pady=5, sticky=N+EW)

	row_builder = RowBuilder()

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

	has_weapons = getattr(data.attacker_frame, "has_weapons", False)
	if not has_weapons:
		tk.Label(frame, text="Attacker has no weapon").grid(row=row_builder.next, column=0, padx=5, pady=5, columnspan=2)
		return

	chance_for_good_shot_row = row_builder.next

	attack_directions = AttackDirection.get_str_values()
	attack_direction = getattr(frame, "attack_direction", None)
	if attack_direction is None:
		frame.attack_direction = attack_direction = StringVar()
		attack_direction.set(attack_directions[0])

	attack_direction_label = tk.Label(frame, text="Attack Side: ")
	attack_direction_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	attack_direction_menu = tk.OptionMenu(frame, attack_direction, *attack_directions,
										  command=lambda x: init_comparison_frame(frame))
	attack_direction_menu.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	attacker_weapon = data.attacker_frame.weapons_data.get_weapon_stats(data.attacker_frame.weapon_names.index(data.attacker_frame.selected_weapon.get()))
	weapon_index = data.attacker_frame.weapon_names.index(data.attacker_frame.selected_weapon.get())
	attacker_weapon_shell : UnitStats.WeaponShellStats = data.attacker_frame.unit_stats.WeaponsShells[weapon_index]
	side = AttackDirection[attack_direction.get()]

	piercing_probability_label = tk.Label(frame, text="Piercing Probability: ")
	piercing_probability_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	Hovertip(piercing_probability_label, "The chance that attacker will pierce the defenders armor", hover_delay=400)
	piercing_probability = unit_comparer.get_piercing_probability(data.attacker_frame, data.defender_frame, side)
	piercing = tk.Label(frame, text=f"{(piercing_probability*100):.2f}%")
	piercing.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	tk.Label(frame, text="Attack direction: ").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	if not hasattr(frame, "dir_pick"):
		frame.dir_pick = tk.IntVar(value=0)
	dir_pick_slider = tk.Scale(frame, from_=0, to=65535, orient=tk.HORIZONTAL, variable=frame.dir_pick, command=lambda x: init_comparison_frame(frame))
	dir_pick_slider.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	tk.Label(frame, text="Attack range: ").grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	range_min, range_max = attacker_weapon_shell.range_min_max
	if not hasattr(frame, "range_pick"):
		frame.range_pick = tk.DoubleVar(value=range_max)
	else:
		frame.range_pick = tk.DoubleVar(value=frame.range_pick.get())
	range_pick_slider = tk.Scale(frame, from_=range_min, to=range_max, orient=tk.HORIZONTAL, variable=frame.range_pick, command=lambda x: init_comparison_frame(frame))
	#range_pick_slider = tk_utils.scaler_with_entry(frame, frame.range_pick, range_min, range_max, command=lambda: init_comparison_frame(frame))
	range_pick_slider.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=EW)

	hits, bounce_offs, misses = unit_comparer.get_aabb_hit_probability(data.attacker_frame, data.defender_frame,
																	   frame.range_pick.get(), frame.dir_pick.get())
	hit_probability = hits/data.simulation_iterations.get()

	hit_probability_label = tk.Label(frame, text="AABB Hit probability (approx): ")
	hit_probability_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	Hovertip(hit_probability_label, "The chance for attacker to properly hit defenders AABB (with AABBCoef)", hover_delay=400)
	tk.Label(frame, text=f"{hit_probability*100:.2f}%").grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	bounce_off_label = tk.Label(frame, text="AABB Bounce off probability (approx): ")
	bounce_off_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	Hovertip(bounce_off_label, "The chance for defender to bounce off a shot at take no damage", hover_delay=400)
	tk.Label(frame, text=f"{bounce_offs/data.simulation_iterations.get()*100:.2f}%").grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	miss_probability_label = tk.Label(frame, text="AABB Miss probability (approx): ")
	miss_probability_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	Hovertip(miss_probability_label, "The chance that the attacker will completely miss the defender, area damage might still apply if close enough", hover_delay=400)
	tk.Label(frame, text=f"{misses/data.simulation_iterations.get()*100:.2f}%").grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	total_shot_chance_label = tk.Label(frame, text="Overall shot chance: ", font=("Arial", 12, "bold"))
	total_shot_chance_label.grid(row=chance_for_good_shot_row, column=0, padx=5, pady=5, sticky=W)
	Hovertip(total_shot_chance_label, "Overall chance to get a good shot on defender", hover_delay=400)
	total_chance = piercing_probability * hit_probability
	(tk.Label(frame, text=f"{total_chance*100:.2f}%", fg=tk_utils.lerp_color("#FF0000", "#00FF00", total_chance), font=("Arial", 12, "bold"))
	 .grid(row=chance_for_good_shot_row, column=1, padx=5, pady=5, sticky=E))


	return
