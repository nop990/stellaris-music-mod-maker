import shutil
from util import version


# Makes the title look nice in the console
def print_title():
    terminal_width = shutil.get_terminal_size().columns
    title = f"STELLARIS MUSIC MOD MAKER v{version}"
    author = "Created by nop990"
    border = '=' * terminal_width

    print(border.center(terminal_width))
    print(title.center(terminal_width))
    print(author.center(terminal_width))
    print(border.center(terminal_width))