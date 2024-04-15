from virtual_file_system_abstract import VirtualFileSystemBaseClass
from folder_system import FolderSystem
import io

path1 = "C:\Program Files (x86)\Steam\steamapps\common\Blitzkrieg 2 Anthology\Blitzkrieg 2\Data"
path2 = "C:\Program Files (x86)\Steam\steamapps\common\Blitzkrieg 2 Anthology\Blitzkrieg 2\mods\ModernDayWar"

def main():
    global path1
    global path2
    folder_system = FolderSystem(path2)
    folder_system.add_directory(path1)

    file_text = folder_system.read_text_file("desc.txt")
    print(file_text)

    return 0

if __name__ == '__main__':
    main()
