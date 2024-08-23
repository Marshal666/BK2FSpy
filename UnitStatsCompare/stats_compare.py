
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox

import stats_compare_data as data


def open_game_folders_command():

	def open_game_folder_command():
		
		return

	window = data.folders_pick = tk.Toplevel()
	window.title('Open game folders')
	window.geometry('640x400')

	tk.Label(window, text="Game folder: ").grid(row=0, column=0, padx=5, pady=5, sticky=W)
	game_folder_entry = tk.Entry(window, width=80)
	game_folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
	(tk.Button(window, text="...", width=5, command=open_game_folder_command)
	 .grid(row=0, column=2, padx=5, pady=5, sticky=E))

	window.grid_columnconfigure(1, weight=1)  # Makes the Entry widget's column stretchable
	window.grid_columnconfigure(0, weight=0)  # Label column stays at its natural size
	window.grid_columnconfigure(2, weight=0)  # Button column stays at its natural size

	window.grab_set()  # Prevent interaction with the original window until this one is closed
	window.focus_set()  # Give focus to the new window
	#window.transient(window)  # Make the new window always on top of the original

	return


def quit_command():
	data.root.quit()
	return


def main():
	root = data.root = Tk()
	root.title('BK2 Unit Stats Compare')
	root.geometry("1280x720")
	root.iconbitmap("icon.ico")

	data.menu_bar = tk.Menu(root)

	file_menu = tk.Menu(data.menu_bar, tearoff=0)
	file_menu.add_command(label="Open Game Folders", command=open_game_folders_command)
	file_menu.add_separator()
	file_menu.add_command(label="Quit", command=quit_command)
	data.menu_bar.add_cascade(label="File", menu=file_menu)

	#data.open_game_folders_button = ttk.Button(root, text="Open game folder(s)", command=open_game_folders)
	#data.open_game_folders_button.pack(anchor='nw', pady=10, padx=10)

	root.config(menu=data.menu_bar)

	root.mainloop()
	return


if __name__ == "__main__":
	main()