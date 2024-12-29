import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
import consts
import stats_compare_data as data
from console_logger import ConsoleLogger
from folder_system import FolderSystem
from pak_loader import PakLoader
from virtual_file_system import VirtualFileSystem
from idlelib.tooltip import Hovertip
import tk_utils
from tk_utils import RowBuilder
import comparison_frame
import unit_frame
import recent_units_frame
import game_data_loader
import recent_items
from VerticalScrolledFrame import VerticalScrolledFrame


def on_file_system_loaded():
	reset_unit_frames(data.attacker_frame, data.comparison_frame, data.defender_frame, True)
	recent_units_frame.clear_recent_units_frame()
	return


def open_folders(game_folder: str, mod_folder: str) -> bool:
	paths = {game_folder, mod_folder}
	if "" in paths:
		paths.remove("")

	for path in paths:
		if not os.path.isdir(path):
			messagebox.showerror("Error", f"Invalid path: \"{path}\"")
			return False

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

	on_file_system_loaded()

	game_data_loader.load_game_data(data.file_system)

	mod_name = "None"
	if data.file_system.contains_file("name.txt"):
		try:
			mod_name = data.file_system.read_text_file("name.txt")
		except Exception as e:
			pass

	data.root.title(f'BK2 Unit Stats Compare {consts.PROGRAM_VERSION} MOD: {mod_name}')

	recent_items.add_recent_item([mod_name if mod_name != "None" else f"Non-MOD {paths[0]}", game_folder, mod_folder])

	if data.folders_pick:
		data.folders_pick.destroy()

	messagebox.showinfo("Data Loaded", "Data was loaded successfully")


def open_game_folders_command():

	def open_game_folder_command():
		folder = filedialog.askdirectory()
		tk_utils.set_entry_text(game_folder_entry, folder)
		return

	def open_mod_folder_command():
		folder = filedialog.askdirectory()
		tk_utils.set_entry_text(mod_folder_entry, folder)
		return

	def open_given_folders_command():

		if not game_folder_entry.get().strip():
			messagebox.showwarning("Warning", "Please select a game folder")
			return

		game_folder: str = game_folder_entry.get().strip()
		mod_folder: str = mod_folder_entry.get().strip()

		open_folders(game_folder, mod_folder)

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


def quit_command():
	data.root.quit()
	return


def reset_unit_frames(attacker_frame: tk.Frame, comparer_frame: tk.Frame, defender_frame: tk.Frame, enabled:bool):

	unit_frame.init_unit_frame(data.attacker_frame, consts.ATTACKER_FRAME_TITLE)
	unit_frame.init_unit_frame(data.defender_frame, consts.DEFENDER_FRAME_TITLE),
	comparison_frame.init_comparison_frame(comparer_frame)

	if enabled:

		tk_utils.enable_frame(attacker_frame)
		tk_utils.enable_frame(comparer_frame)
		tk_utils.enable_frame(defender_frame)

		return

	tk_utils.disable_frame(attacker_frame)
	tk_utils.disable_frame(comparer_frame)
	tk_utils.disable_frame(defender_frame)

	return


def open_simulation_config_command():

	def on_iterations_edited(arg1, arg2, arg3):
		# print(f"arg1: {arg1}, arg2: {arg2}, arg3: {arg3}, value: {data.simulation_iterations.get()}")

		if not window.iters_input.get() or not window.iters_input.get().strip():
			data.simulation_iterations.set(1)
			window.iters_input.update()
			return

		#print(f"arg1: {arg1}, arg2: {arg2}, arg3: {arg3}, value: {data.simulation_iterations.get()}")

		return

	def on_rng_seed_edited(arg1, arg2, arg3):

		if not window.rng_seed_input.get() or not window.rng_seed_input.get().strip():
			data.simulation_rng_seed.set(0)
			return

		#print(f"arg1: {arg1}, arg2: {arg2}, arg3: {arg3}, value: {data.simulation_rng_seed.get()}")

		return

	def on_shot_iterations_edited(arg1, arg2, arg3):
		# print(f"arg1: {arg1}, arg2: {arg2}, arg3: {arg3}, value: {data.simulation_iterations.get()}")

		if not window.shot_iters_input.get() or not window.shot_iters_input.get().strip():
			data.simulation_iterations.set(1)
			window.iters_input.update()
			return

		#print(f"arg1: {arg1}, arg2: {arg2}, arg3: {arg3}, value: {data.simulation_iterations.get()}")

		return

	def on_close(event):
		data.simulation_iterations = tk.IntVar(value=data.simulation_iterations.get())
		data.simulation_iterations.not_traced = True
		data.simulation_rng_seed = tk.IntVar(value=data.simulation_rng_seed.get())
		data.simulation_rng_seed.not_traced = True
		data.shot_simulation_iterations = tk.IntVar(value=data.shot_simulation_iterations.get())
		data.shot_simulation_iterations.not_traced = True
		return

	if data.simulation_iterations.not_traced:
		data.simulation_iterations.callback = data.simulation_iterations.trace_add("write", on_iterations_edited)
	if data.simulation_rng_seed.not_traced:
		data.simulation_rng_seed.callback = data.simulation_rng_seed.trace_add("write", on_rng_seed_edited)
	if data.shot_simulation_iterations.not_traced:
		data.shot_simulation_iterations.callback = data.shot_simulation_iterations.trace_add("write", on_shot_iterations_edited)

	row_builder = RowBuilder()

	window = tk.Toplevel()
	window.title('Edit simulation configuration')
	window.geometry('320x130')
	window.minsize(300, 120)
	window.bind("<Destroy>", on_close)

	validate_command = window.register(tk_utils.validate_integer_input)

	iter_count_label = tk.Label(window, text="Iteration count: ")
	iter_count_label.grid(row=row_builder.current, column=0, padx=5, pady=5, sticky=W)
	Hovertip(iter_count_label, "The number of iterations for AABB hit probability calculation, the more the better", hover_delay=500)
	window.iters_input = tk.Entry(window, textvariable=data.simulation_iterations, validate="key", validatecommand=(validate_command, "%P"), width=15)
	window.iters_input.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	rng_seed_label = tk.Label(window, text="RNG seed: ")
	rng_seed_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	Hovertip(rng_seed_label, "Seed for RNG for AABB hit probability calculation", hover_delay=500)
	window.rng_seed_input = tk.Entry(window, textvariable=data.simulation_rng_seed, validate="key", validatecommand=(validate_command, "%P"), width=15)
	window.rng_seed_input.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	damage_area_coeff_label = tk.Label(window, text="Damage area coefficient: ")
	damage_area_coeff_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	Hovertip(damage_area_coeff_label, "Area damage reduction for original intended damage", hover_delay=500)
	window.area_damage_coeff_input = tk_utils.create_float_entry(window, data.area_damage_coeff, 5)
	window.area_damage_coeff_input.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	iter_count_label = tk.Label(window, text="Shot Iteration count: ")
	iter_count_label.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=W)
	Hovertip(iter_count_label, "The number of shot iterations for average amount of shots needed calculation, the more the better", hover_delay=500)
	window.shot_iters_input = tk.Entry(window, textvariable=data.shot_simulation_iterations, validate="key", validatecommand=(validate_command, "%P"), width=15)
	window.shot_iters_input.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=E)

	window.grab_set()  # Prevent interaction with the original window until this one is closed
	window.focus_set()  # Give focus to the new window

	return


def main():
	root = data.root = Tk()
	root.title(f'BK2 Unit Stats Compare {consts.PROGRAM_VERSION}')
	root.geometry("1340x1020")
	root.minsize(1024, 620)
	#root.iconbitmap("icon.ico")

	data.simulation_iterations = IntVar(value=100000)
	data.simulation_iterations.not_traced = True
	data.simulation_rng_seed = IntVar(value=1337)
	data.simulation_rng_seed.not_traced = True
	data.shot_simulation_iterations = IntVar(value=4000)
	data.shot_simulation_iterations.not_traced = True
	data.area_damage_coeff = DoubleVar(value=0.3)
	data.auto_compare_units = BooleanVar(value=True)
	recent_items.load_recent_items()

	data.menu_bar = tk.Menu(root)

	data.file_menu = file_menu = tk.Menu(data.menu_bar, tearoff=0)
	file_menu.add_command(label="Open Game Folders", command=open_game_folders_command)
	file_menu.add_separator()

	recent_items_menu = tk.Menu(root, tearoff=0)
	recent_items_list = recent_items.get_recent_items()

	if len(recent_items_list) < 1:
		recent_items_menu.add_command(label="No items..", state=tk.DISABLED)

	for item in recent_items_list:
		recent_items_menu.add_command(label=item[0], command=lambda x=item: open_folders(x[1], x[2]))

	#recent_items_menu.add_command(label="Clear All", command=recent_items.clear_recent_items)

	file_menu.add_cascade(label="Recent Items", menu=recent_items_menu)

	file_menu.add_separator()
	file_menu.add_command(label="Quit", command=quit_command)
	data.menu_bar.add_cascade(label="File", menu=file_menu)

	config_menu = tk.Menu(data.menu_bar, tearoff=0)
	config_menu.add_command(label="Simulation Config", command=open_simulation_config_command)
	data.menu_bar.add_cascade(label="Config", menu=config_menu)

	row_builder = RowBuilder()

	data.recent_units_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	data.recent_units_frame.grid(row=row_builder.current, column=0, padx=5, pady=5, columnspan=3, sticky=N+EW)
	recent_units_frame.init_recent_units_frame(data.recent_units_frame)

	#data.attacker_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	data.attacker_frame = VerticalScrolledFrame(root)
	data.attacker_frame.grid(row=row_builder.next, column=0, padx=5, pady=5, sticky=NW)
	data.attacker_frame = data.attacker_frame.interior
	unit_frame.init_unit_frame(data.attacker_frame, consts.ATTACKER_FRAME_TITLE)

	#data.defender_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	data.defender_frame = VerticalScrolledFrame(root)
	data.defender_frame.grid(row=row_builder.current, column=2, padx=5, pady=5, sticky=NE)
	data.defender_frame = data.defender_frame.interior
	unit_frame.init_unit_frame(data.defender_frame, consts.DEFENDER_FRAME_TITLE)

	data.comparison_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	data.comparison_frame.grid(row=row_builder.current, column=1, padx=5, pady=5, sticky=N+EW)
	comparison_frame.init_comparison_frame(data.comparison_frame)

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