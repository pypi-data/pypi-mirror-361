from functools import reduce
import csv

ANSI_CODE = {
    "BLACK" : "\033[0;30m",
    "RED" : "\033[0;31m",
    "GREEN" : "\033[0;32m",
    "BROWN" : "\033[0;33m",
    "BLUE" : "\033[0;34m",
    "PURPLE" : "\033[0;35m",
    "CYAN" : "\033[0;36m",
    "LIGHT_GRAY" : "\033[0;37m",
    "DARK_GRAY" : "\033[1;30m",
    "LIGHT_RED" : "\033[1;31m",
    "LIGHT_GREEN" : "\033[1;32m",
    "YELLOW" : "\033[1;33m",
    "LIGHT_BLUE" : "\033[1;34m",
    "LIGHT_PURPLE" : "\033[1;35m",
    "LIGHT_CYAN" : "\033[1;36m",
    "LIGHT_WHITE" : "\033[1;37m",
    "BOLD" : "\033[1m",
    "FAINT" : "\033[2m",
    "ITALIC" : "\033[3m",
    "UNDERLINE" : "\033[4m",
    "BLINK" : "\033[5m",
    "NEGATIVE" : "\033[7m",
    "CROSSED" : "\033[9m",
    "END" : "\033[0m"
}


def read_sudoku_csv(file_path:str)->list:
    """
    reads a sudoku puzzle stored as a CSV file

    file_path (str): path to the csv file

    return: 2d list representing a sudoku grid
    """
    sudoku_puzzle = []
    with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                # converting the numbers from string to int
                sudoku_puzzle.append([int(n) if n != '' else 0 for n in row])
    return sudoku_puzzle

def write_sudoku_csv(sudoku_grid:list, file_path:str)->None:
    """
    Writes a sudoku grid to a specified CSV file.

    sudoku_grid (list) a 2d list of integers representing the sudoku grid.

    file_path (str) a path to the file you want to write to

    return: None
    """
    with open(file_path, 'x') as file:
        spamwriter = csv.writer(file)
        for row in sudoku_grid:
            spamwriter.writerow(['' if cell == 0 else str(cell) for cell in row])
        

def print_board(sudoku_grid:list, border_color:str=ANSI_CODE["PURPLE"], grid_color:str=ANSI_CODE["LIGHT_BLUE"]) -> None:
    """
    Simply prints the board with a given a sudoku grid.

    sudoku_grid (list): a 2d list of dimensions 9x9  representing a sudoku grid

    """

    col_index = "  " + reduce(lambda a, b: a + b, [f"\033[0;{31+(i%5)}m{i}   " for i in range(9)]) + "\n"

    top = f"{border_color}╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗\033[0m\n"
    middle_normal = f"{border_color}╟{grid_color}━━━┿━━━┿━━━{border_color}╫{grid_color}━━━┿━━━┿━━━{border_color}╫{grid_color}━━━┿━━━┿━━━{border_color}╢\033[0m\n"
    middle_bold = f"{border_color}╠═══╪═══╪═══╫═══╪═══╪═══╫═══╪═══╪═══╣\033[0m\n"
    bottom = f"{border_color}╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝\033[0m\n"

    # i sure do hope these are only pointers... otherwise rip memory (altho modern computers OP)
    x_grid_list = [
        middle_normal,
        middle_normal,
        middle_bold,
        middle_normal,
        middle_normal,
        middle_bold,
        middle_normal,
        middle_normal,
        bottom,
    ]
    grid = col_index + top
    for i, rows in enumerate(sudoku_grid):
        grid += (f"{border_color}║{grid_color}"+("\033[0m {} "+ f"{grid_color}┃\033[0m" + " {} " + f"{grid_color}┃\033[0m"+" {} " + f"{border_color}║{grid_color}")*3 + "\033[0;{}m{}\n").format(
        *rows,
        31+(i%5), i) + x_grid_list[i]

    print(grid)



#    f"""
# ┏━┳━┳━╥━┳━┳━╥━┳━┳━┓
# ┃ ┃ ┃ ║ ┃ ┃ ║ ┃ ┃ ┃
# ┣━┿━┿━╫━┿━┿━╫━┿━┿━┫
# ┃ ┃ ┃ ║ ┃ ┃ ║ ┃ ┃ ┃
# ╠═╬═╬═╬═╬═╬═╬═╬═╬═╣

# ╚═╩═╩═╩═╩═╩═╩═╩═╩═╝
# ┏━┳━┳━╥━┳━┳━╥━┳━┳━┓
#    """

def show_help():
    help_text = """
📘 SUDOKU GAME HELP

🔢 WHAT IS SUDOKU?
Sudoku is a logic-based number puzzle. The game board is a 9x9 grid divided into nine 3x3 boxes.

🎯 GOAL:
Fill the grid so that:
- Each ROW contains numbers 1 to 9 with no repeats.
- Each COLUMN contains numbers 1 to 9 with no repeats.
- Each 3x3 BOX contains numbers 1 to 9 with no repeats.

🕹️ HOW TO PLAY:
- Use logic to figure out where each number goes.
- You can’t repeat numbers in any row, column, or box.
- Start with the given clues and build from there.

💡 TIPS:
- Look for rows, columns, or boxes that are almost full.
- Use process of elimination.
- No guessing — it's all about logic.

Type 'help' to see this message again.
"""
    print(help_text)

# Color a text in a certain color for display
def color_text(text, color="\033[0;34m") -> str:
    return f"{color}{text}\033[0m"

def double_check(sudoku_grid:list) -> None:
    """
    asks the user to enter a command.
    command list:
    - help: print the command list, give more info
    - ok: exit out of the function
    - replace x y n: replace the number in that given cell
    """
    edited_cells = set()
    while True:
        print_board(format_grid(sudoku_grid, edited_cells))  # your own colorful function
        print('Please recheck your sudoku board:')
        print('- help')
        print('- ok')
        print('- replace <x> <y> <n>')
        user_input = input("input a command: ").strip().lower()

        if user_input == "ok":
            print("✅ Final board accepted.")
            break

        elif user_input == "help":
            show_help()

        elif user_input.startswith("replace"):
            try:
                parts = user_input.split()
                x, y, n = map(int, parts[1:]) # Convert to integers
                if 0 <= x < 9 and 0 <= y < 9 and 0 <= n <= 9: 
                    sudoku_grid[y][x] = n  # update value
                    edited_cells.add((y, x))  # track edited cells
                else:
                    print("❌ Invalid values: x/y must be 0-8, n must be 0-9")
            except:
                print("❌ Format: replace x y n")

        else:
            print("❌ Unknown command. Type 'help'")


# Track edited (user-modified) cells

def format_grid(sudoku_grid:list, highlighted_cells:set=set()) -> list:
    """
    replaces the 2d grid from integers to string, with coloring and removing 0s

    sudoku_grid (list): 2d list of integer representing a sudoku grid

    edited_cells (set): a list of cells that should be highlighted
    It's used to track which cells the user has modified by using the replace x y n command in your Sudoku game.
    Because you want the numbers that the user replaces to show up in blue — so 
    we need a way to remember which cells were changed.

    return: 2d list of string representing a sudoku grid 
    """
    # edited_cells: Keeps track of (y, x) coordinates of any cells you replace.
    
    # updated= [] initializes an empty list that will store the processed Sudoku rows.
    updated = []
    for y, row in enumerate(sudoku_grid):
        #Loops over each row (row) of the Sudoku grid, and y is the row index (0-based).
        updated_row = []
        for x, val in enumerate(row):
            if (y, x) in highlighted_cells:
                updated_row.append(color_text(' ' if val == 0 else val, ANSI_CODE["LIGHT_GREEN"]))
            else:
                updated_row.append(color_text(' ' if val == 0 else val, ANSI_CODE["YELLOW"]))
        updated.append(updated_row)
    return updated

def get_non_empty_coord(sudoku_grid:list) -> set:
    """
    returns a set of coordinates (y, x) where the element is non-zero

    sudoku_grid (list): a 2d list of number representing a sudoku board 
    return: set of tuple 
    """
    non_empty_coord = set()
    for y, row in enumerate(sudoku_grid):
        for x, cell in enumerate(row):
            if cell != 0:
                non_empty_coord.add((y, x))
    return non_empty_coord
