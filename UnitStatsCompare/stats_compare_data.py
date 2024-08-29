import tkinter
import virtual_file_system_abstract

file_system: virtual_file_system_abstract.VirtualFileSystemBaseClass = None

root: tkinter.Tk = None

folders_pick: tkinter.Tk = None

menu_bar: tkinter.Menu = None

attacker_frame: tkinter.Frame = None
comparison_frame: tkinter.Frame = None
defender_frame: tkinter.Frame = None

simulation_iterations: tkinter.IntVar|None = None #tkinter.IntVar(value=100000)
simulation_rng_seed: tkinter.IntVar|None = None #tkinter.IntVar(value=1337)
