import os
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import consts
import stats_compare_data as data
from console_logger import ConsoleLogger
from folder_system import FolderSystem
from pak_loader import PakLoader
from virtual_file_system import VirtualFileSystem
import game_data_loader


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


def select_unit_command(frame: tk.Frame):

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
						# TODO
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
						(tk.Button(frame, text=f"unit{index}:", command=lambda: select_unit_button_command(index))
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
				reinf_options.grid(row=0, column=1, padx=5, pady=5, sticky=W)

				units_frame = tk.Frame(frame)
				units_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=W)

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
			nation_options.grid(row=0, column=1, padx=5, pady=5, sticky=W)

			tk.Label(option_frame, text="Select Tech Level: ").grid(row=1, column=0, padx=5, pady=5, sticky=W)

			tech_level_option = tk.StringVar()
			tech_level_option.set(tech_levels[0])

			tech_level_options = tk.OptionMenu(option_frame, tech_level_option, *tech_levels, command=tech_level_pick_command)
			tech_level_options.grid(row=1, column=1, padx=5, pady=5, sticky=W)

			reinf_pick_frame = tk.Frame(option_frame)
			reinf_pick_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

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


def init_unit_frame(frame: tk.Frame, title: str, unit: str = None):

	clear_frame_children(frame)

	frame.title = tk.Label(frame, text=title, width=15, font=("Arial", 24, "bold"))
	frame.title.grid(row=0, column=0, padx=10, pady=5, sticky=EW)

	if not unit or not unit.strip():
		frame.get_unit_button = (
			tk.Button(frame, text="Select unit...", command=lambda: select_unit_command(frame), width=22))
		frame.get_unit_button.grid(row=1, column=0, padx=15, pady=10)

		disable_frame(frame)

	return

def init_comparison_frame(frame: tk.Frame):

	data.comparison_frame.grid_columnconfigure(0, weight=1)
	data.comparison_frame.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
	data.comparison_frame.title = tk.Label(data.comparison_frame, text="Comparison", font=("Arial", 24, "bold"),
										   width=20)
	data.comparison_frame.title.grid(row=0, column=0, padx=5, pady=0, sticky=EW)

	return

def reset_unit_frames(attacker_frame: tk.Frame, comparison_frame: tk.Frame, defender_frame: tk.Frame, enabled:bool):

	init_comparison_frame(comparison_frame)

	if enabled:

		enable_frame(attacker_frame)
		enable_frame(comparison_frame)
		enable_frame(defender_frame)

		return

	init_unit_frame(data.attacker_frame, consts.ATTACKER_FRAME_TITLE)
	init_unit_frame(data.defender_frame, consts.DEFENDER_FRAME_TITLE)

	disable_frame(attacker_frame)
	disable_frame(comparison_frame)
	disable_frame(defender_frame)

	return


def main():
	root = data.root = Tk()
	root.title('BK2 Unit Stats Compare')
	root.geometry("1280x720")
	root.minsize(800, 600)
	root.iconbitmap("icon.ico")

	data.menu_bar = tk.Menu(root)

	file_menu = tk.Menu(data.menu_bar, tearoff=0)
	file_menu.add_command(label="Open Game Folders", command=open_game_folders_command)
	file_menu.add_separator()
	file_menu.add_command(label="Quit", command=quit_command)
	data.menu_bar.add_cascade(label="File", menu=file_menu)

	data.attacker_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	data.attacker_frame.grid(row=0, column=0, padx=5, pady=5, sticky=W)
	init_unit_frame(data.attacker_frame, consts.ATTACKER_FRAME_TITLE)

	data.defender_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
	data.defender_frame.grid(row=0, column=2, padx=5, pady=5, sticky=E)
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