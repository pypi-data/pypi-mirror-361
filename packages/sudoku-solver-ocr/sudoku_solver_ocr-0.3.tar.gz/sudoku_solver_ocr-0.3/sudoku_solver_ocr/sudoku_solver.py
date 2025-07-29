import numpy as np
import copy
from . import sudoku_utils
import time
import os
import threading
    

def is_possible(sudoku_puzzle:list, x:int, y:int, n:int)->bool:
    """
    Checks whether its possible to place a digit, n at coordinates x, y

    sudoku_puzzle (list): a 2d list of integers representing a sudoku puzzle (9x9)

    x (int): coordinates of the x axis from 0 to 8 

    y (int): coordinates of the y axis from 0 to 8

    n (int): a digit to place at coordinate (x, y)

    return: a boolean that states whether it's possible to put that value n at coordinates x, y
    """
    
    # first check for rows
    fits_rows = not (n in sudoku_puzzle[y])
    # then checks for columns
    fits_columns = not (n in [row[x] for row in sudoku_puzzle])

    # finally, check for squares
    
    # first dividing the grid to 3x3 squares
    x_square = x//3
    y_square = y//3
    
    fits_squares = not (n in [sudoku_puzzle[y_in_square][x_in_square] for x_in_square in range(x_square*3, (x_square+1)*3) for y_in_square in range(y_square*3, (y_square+1)*3)])
    
    return fits_rows and fits_columns and fits_squares

def solve_sudoku(sudoku_puzzle:list, solutions_list:list) -> None:
    """
    solves the sudoku puzzle and returns the list of all possible solutions

    sudoku_puzzle (list) 2d list representing a sudoku grid

    solution_list (list) a list of 2d list that 'collects' the solution
    """

    # first loop through the sudoku grid

    for y in range(9):
        for x in range(9):
            if sudoku_puzzle[y][x] != 0:
                # i kinda hate 'continue' and 'break' but no thanks to nesting hell...
                continue
            for n in range(1, 10):
                # try to continue with n as the solution
                if not is_possible(sudoku_puzzle, x, y, n):
                    continue 
                sudoku_puzzle[y][x] = n
                solve_sudoku(sudoku_puzzle, solutions_list)
                # but now we've traveled crossed dimensions and came back here
                # but now we know... and so, backtracking...
                sudoku_puzzle[y][x] = 0
                
                # now it'll go from left to right with no problems until it reaches this y,x and tries the same thing...
                # but let's just say it has looped through DEEP into the sudoku grid and found out, it can't continue (how???)
            # well, we can say that if it's out of the loop, we've reached a dead end
            # so gotta return...
            return
    solutions_list.append(copy.deepcopy(sudoku_puzzle))



def solve_sudoku_single_solution(sudoku_puzzle:list, x:int=0, y:int=0, delay:float=0) -> bool:
    """
    sudoku_puzzle (list): passing a pointer to a list that's outside the scope of the function. This program will search left to right, top to down.

    x (int): the x coordinates

    y (int): the y coordinates

    return: a bool representing whether the path is value or invalid
    """

    if y == 9:
        # if this program has reached the end. 
        # since the scope of x and y is from 0 to 8, if it reaches 9, then we're done
        return True
    # what a nesting mess...
    elif x == 9:
        # if we've reached the end of the row, drop down by one
        return solve_sudoku_single_solution(sudoku_puzzle, 0, y+1, delay)
    elif sudoku_puzzle[y][x] != 0:
        # now if we're our isn't actually replacable, then go on to the next
        return solve_sudoku_single_solution(sudoku_puzzle, x+1, y, delay)
    else:
        # now if our x, y coordinates have a 0, try to replace it from 1 to 9
        for k in range(1, 10):
            if is_possible(sudoku_puzzle, x, y, k):
                # if k is possible replace the value at that coordinates with k
                sudoku_puzzle[y][x] = k
                time.sleep(delay)
                # now see if we can actually try solve it given that our value of k is of such.

                # move on and assume that our k is valid
                if solve_sudoku_single_solution(sudoku_puzzle, x+1, y, delay):
                    return True
                else:
                    # if the puzzle isn't solved yet, backtrack and try to replace k again
                    
                    sudoku_puzzle[y][x] = 0
        # if we've looped through, we know we didn't return True
        return False


def solve_sudoku_animated(sudoku_puzzle:list, delay:float=1/60) -> None:
    """
    Wrapper function.
    """
    event = threading.Event()
    def print_board_occasionally(sudoku_puzzle:list, delay:float, event):
        while not event.is_set():
            time.sleep(delay)
            os.system("clear")
            sudoku_utils.print_board(sudoku_puzzle)
    printing_thread = threading.Thread(target=print_board_occasionally, args=(sudoku_puzzle, delay, event))
    printing_thread.start()
    solve_sudoku_single_solution(sudoku_puzzle, delay=delay/10)
    event.set()
