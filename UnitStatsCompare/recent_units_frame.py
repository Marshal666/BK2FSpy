import stats_compare_data as data
import tkinter as tk
import unit_frame
import comparison_frame
import tk_utils
import bk2_xml_utils


class RecentUnitItem:

	def __init__(self, unit_name: str, unit_path: str, unit_icon: tk.PhotoImage):
		self.unit_name = unit_name
		self.unit_path = unit_path
		self.unit_icon = unit_icon

	def __eq__(self, other):
		self_unit_path = bk2_xml_utils.format_href(self.unit_path)
		other_unit_path = bk2_xml_utils.format_href(other.unit_path)
		return self_unit_path == other_unit_path

	def draw(self, frame: tk.Frame) -> tk.Frame:

		def select_command(frame_of_unit: tk.Frame):

			unit_frame.init_unit_frame(frame_of_unit, frame_of_unit.title, self.unit_path)
			comparison_frame.init_comparison_frame(data.comparison_frame)

			return

		ret = tk.Frame(frame, bd=1, relief=tk.RAISED, width=128)

		tk.Label(ret, image=self.unit_icon).grid(row=0, column=0, columnspan=2)

		tk.Label(ret, text=self.unit_name, wraplength=92).grid(row=1, column=0, columnspan=2)

		tk.Button(ret, text="⚔", width=4, command=lambda x=data.attacker_frame: select_command(x)).grid(row=2, column=0, sticky=tk.SW)

		tk.Button(ret, text="⛨", width=4, command=lambda x=data.defender_frame: select_command(x)).grid(row=2, column=1, sticky=tk.SE)

		tk.Button(ret, text="❌", width=1, height=1, command=lambda x=self: delete_recent_unit(x)).grid(row=0, column=0, columnspan=2, sticky=tk.NE)

		ret.rowconfigure(0, weight=1)
		ret.rowconfigure(1, weight=1)
		ret.rowconfigure(2, weight=1)

		return ret


recent_units: list[RecentUnitItem] = []


def init_recent_units_frame(frame: tk.Frame):

	tk_utils.clear_frame_children(frame)

	if len(recent_units) < 1:
		tk.Label(frame, text="No recent units").grid(row=0, column=0, columnspan=2)
		return

	for unit in recent_units:
		recent_unit_frame = unit.draw(frame)
		recent_unit_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

	return


def add_recent_unit(unit_name: str, unit_path: str, unit_icon: tk.PhotoImage):
	unit_item = RecentUnitItem(unit_name, unit_path, unit_icon)
	if unit_item not in recent_units:
		recent_units.append(unit_item)
		init_recent_units_frame(data.recent_units_frame)


def delete_recent_unit(unit_item: RecentUnitItem):
	if unit_item in recent_units:
		recent_units.remove(unit_item)
		init_recent_units_frame(data.recent_units_frame)
	return


def clear_recent_units_frame():
	recent_units.clear()
	init_recent_units_frame(data.recent_units_frame)
