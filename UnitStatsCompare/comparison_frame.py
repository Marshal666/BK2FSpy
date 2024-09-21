import  stats_compare_data as data
import tkinter as tk
from tkinter import *
import consts
import tk_utils
import unit_comparer, game_data_loader
from game_data_loader import UnitStats
from unit_comparer import AttackDirection
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

	row_builder = RowBuilder()

	frame.title = tk.Label(data.comparison_frame, text="Comparison", font=("Arial", 24, "bold"), width=20)
	frame.title.grid(row=row_builder.current, column=0, padx=consts.PAD_X, pady=0, columnspan=2, sticky=EW)

	frame.switch_comparison_button = tk.Button(frame, text="<=Swap=>", width=16, command=swap_command)
	frame.switch_comparison_button.grid(row=row_builder.next, column=0, columnspan=2, padx=consts.PAD_X, pady=consts.PAD_Y)

	attacker = getattr(data.attacker_frame, "unit_path", None)
	if attacker is None:
		(tk.Label(frame, text="No attacker for comparison")
		 .grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2))
		return

	defender = getattr(data.defender_frame, "unit_path", None)
	if defender is None:
		(tk.Label(frame, text="No defender for comparison")
		 .grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2))
		return

	has_weapons = getattr(data.attacker_frame, "has_weapons", False)
	if not has_weapons:
		tk.Label(frame, text="Attacker has no weapon").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, columnspan=2)
		return

	chance_for_good_shot_row = row_builder.next
	chance_for_one_shot_row = row_builder.next
	amount_of_kill_shots_row = row_builder.next
	average_kill_time_row = row_builder.next

	attack_directions = AttackDirection.get_str_values()
	attack_direction = getattr(frame, "attack_direction", None)
	if attack_direction is None:
		frame.attack_direction = attack_direction = StringVar()
		attack_direction.set(attack_directions[0])

	attack_direction_label = tk.Label(frame, text="Attack Side: ")
	attack_direction_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	attack_direction_menu = tk.OptionMenu(frame, attack_direction, *attack_directions,
										  command=lambda x: init_comparison_frame(frame))
	attack_direction_menu.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	weapon_index = data.attacker_frame.weapon_names.index(data.attacker_frame.selected_weapon.get())
	attacker_weapon_shell : UnitStats.WeaponShellStats = data.attacker_frame.unit_stats.WeaponsShells[weapon_index]
	side = AttackDirection[attack_direction.get()]
	data.attacker_frame.applied_bonuses = data.attacker_frame.unit_stats.get_applied_stats_bonuses()
	data.defender_frame.applied_bonuses = data.defender_frame.unit_stats.get_applied_stats_bonuses()

	direction_message = ""
	if attacker_weapon_shell.trajectory.get() == "TRAJECTORY_HOWITZER":
		direction_message = "Current weapon shell uses TRAJECTORY_HOWITZER which can only hit TOP armor"
	if attacker_weapon_shell.trajectory.get() == "TRAJECTORY_CANNON":
		direction_message = "Current weapon shell uses TRAJECTORY_CANNON which can only hit TOP armor"

	if direction_message:
		tk.Label(frame, text=f"ⓘ {direction_message}", wraplength=352).grid(row=row_builder.next, column=0, columnspan=2, padx=consts.PAD_X, pady=consts.PAD_Y, sticky="nsew")

	piercing_probability_label = tk.Label(frame, text="Piercing Probability: ")
	piercing_probability_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(piercing_probability_label, "The chance that attacker will pierce the defenders armor", hover_delay=400)
	piercing_probability = unit_comparer.get_piercing_probability(data.attacker_frame, data.defender_frame, side)
	piercing = tk.Label(frame, text=f"{(piercing_probability*100):.2f}%")
	piercing.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	tk.Label(frame, text="Attack direction: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	if not hasattr(frame, "dir_pick"):
		frame.dir_pick = tk.IntVar(value=32768)
	dir_pick_slider = tk.Scale(frame, from_=0, to=65535, orient=tk.HORIZONTAL, variable=frame.dir_pick, command=lambda x: init_comparison_frame(frame))
	dir_pick_slider.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	tk.Label(frame, text="Attack range: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	range_min, range_max = attacker_weapon_shell.range_min_max
	if not hasattr(frame, "range_pick"):
		frame.range_pick = tk.DoubleVar(value=range_max)
	else:
		frame.range_pick = tk.DoubleVar(value=frame.range_pick.get())
	range_pick_slider = tk.Scale(frame, from_=range_min, to=range_max, orient=tk.HORIZONTAL, variable=frame.range_pick, command=lambda x: init_comparison_frame(frame))
	range_pick_slider.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=EW)

	hits, bounce_offs, area_damages, misses = unit_comparer.get_aabb_hit_probability(data.attacker_frame, data.defender_frame,
																	   frame.range_pick.get(), frame.dir_pick.get())
	hit_probability = hits/data.simulation_iterations.get()

	hit_probability_label = tk.Label(frame, text="AABB Hit probability (approx): ")
	hit_probability_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(hit_probability_label, "The chance for attacker to properly hit defenders AABB (with AABBCoef)", hover_delay=400)
	tk.Label(frame, text=f"{hit_probability*100:.2f}%").grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	bounce_off_label = tk.Label(frame, text="AABB Bounce off probability (approx): ")
	bounce_off_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(bounce_off_label, "The chance for defender to bounce off a shot at take no damage", hover_delay=400)
	tk.Label(frame, text=f"{bounce_offs/data.simulation_iterations.get()*100:.2f}%").grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	area_damage_probability_label = tk.Label(frame, text="Area damage probability (approx): ")
	area_damage_probability_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(area_damage_probability_label, "Chance of doing area damage", hover_delay=400)
	tk.Label(frame, text=f"{area_damages/data.simulation_iterations.get()*100:.2f}%").grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	miss_probability_label = tk.Label(frame, text="AABB Miss probability (approx): ")
	miss_probability_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(miss_probability_label, "The chance that the attacker will completely miss the defender", hover_delay=400)
	tk.Label(frame, text=f"{misses/data.simulation_iterations.get()*100:.2f}%").grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	cover_coeff = data.defender_frame.applied_bonuses.Cover.value()
	cover_coeff = min(1, max(0, cover_coeff))
	cover_text_label = tk.Label(frame, text="Cover coefficient: ", font=("Arial", 10, "bold"))
	Hovertip(cover_text_label, "Probability that determines if unit (defender) will take damage or not,"
							   " no matter how strong the attacker's gun is, "
							   "Cover of 0% means all damage is ignored", hover_delay=400)
	cover_text_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	cover_label = tk.Label(frame, text=f"{cover_coeff*100:.2f}%", font=("Arial", 10, "bold"))
	cover_label.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	durability = data.defender_frame.applied_bonuses.Durability
	durability_text_label = tk.Label(frame, text="Durability: ")
	durability_text_label.grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(durability_text_label, "Damage reduction (percentage and subtraction), Durability of 0% means complete damage reduction.")
	durability_add_str = f" Add: {durability.add_bonus}"
	durability_str = "None" if durability.zero_count != 0 else f"{durability.mult_bonus*100:.2f}%{'' if durability.add_bonus == 0 else durability_add_str}"
	durability_label = tk.Label(frame, text=durability_str)
	durability_label.grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	total_shot_chance_label = tk.Label(frame, text="Overall shot chance: ", font=("Arial", 12, "bold"))
	total_shot_chance_label.grid(row=chance_for_good_shot_row, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(total_shot_chance_label, "Overall chance to get a good shot on defender, shots from area damages are not included", hover_delay=400)
	total_chance = piercing_probability * hit_probability * cover_coeff
	area_chance = area_damages / data.simulation_iterations.get() * cover_coeff # TODO? use max area piercing too?
	(tk.Label(frame, text=f"{total_chance*100:.2f}%", fg=tk_utils.lerp_color("#FF000A", "#00FF0A", total_chance), font=("Arial", 12, "bold"))
	 .grid(row=chance_for_good_shot_row, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E))

	one_shot_label_label = tk.Label(frame, text="One shot chance: ")
	one_shot_label_label.grid(row=chance_for_one_shot_row, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	one_shot_chance = unit_comparer.get_one_shot_probability(data.attacker_frame, data.defender_frame)
	overall_one_shot_chance = one_shot_chance * total_chance
	one_shot_chance_label = tk.Label(frame, text=f"{overall_one_shot_chance*100:.2f}%")
	one_shot_chance_label.grid(row=chance_for_one_shot_row, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	total_damage_shots_needed = unit_comparer.get_average_amount_of_shots_needed_for_kill(data.attacker_frame, data.defender_frame, total_chance, area_chance)
	damage_shots_needed = unit_comparer.average_amount_of_damage_shots_needed_for_killing(data.attacker_frame, data.defender_frame)
	average_time_needed = unit_comparer.get_average_time_needed_for_kill(data.attacker_frame, data.defender_frame, total_damage_shots_needed)

	total_damage_shots_label_text = tk.Label(frame, text="Average shots needed for kill (approx): ")
	total_damage_shots_label_text.grid(row=amount_of_kill_shots_row, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(total_damage_shots_label_text, "Approximate number of shots needed for killing the defender")
	total_damage_shots_label = tk.Label(frame, text=f"{(total_damage_shots_needed if total_damage_shots_needed != float('inf') else '∞')}")
	total_damage_shots_label.grid(row=amount_of_kill_shots_row, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	average_kill_time_label_text = tk.Label(frame, text="Average time needed for killing (approx): ")
	average_kill_time_label_text.grid(row=average_kill_time_row, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	Hovertip(average_kill_time_label_text, "Approximate time needed for killing the defender in seconds")
	average_kill_time_label = tk.Label(frame, text=f"{average_time_needed:.1f} s")
	average_kill_time_label.grid(row=average_kill_time_row, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	tk.Label(frame, text="One shot chance alone: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	tk.Label(frame, text=f"{one_shot_chance * 100:.2f}%").grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y,
															   sticky=E)

	tk.Label(frame, text="Average damage shots needed for kill: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	tk.Label(frame, text=f"{damage_shots_needed}").grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	track_break_chance = unit_comparer.get_track_break_probability(data.attacker_frame, data.defender_frame)
	track_break_chance = min(100.0, max(0.0, track_break_chance))
	tk.Label(frame, text="Track break probability alone: ").grid(row=row_builder.next, column=0, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=W)
	tk.Label(frame, text=f"{track_break_chance:.1f}%").grid(row=row_builder.current, column=1, padx=consts.PAD_X, pady=consts.PAD_Y, sticky=E)

	return
