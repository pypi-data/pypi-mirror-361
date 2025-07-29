import sys

from . import sudoku_solver as ss
from . import sudoku_utils as su
from . import sudoku_ocr as so

def main():
    if len(sys.argv) != 3:
            sys.exit(f"""Please input an {su.color_text('image path', su.ANSI_CODE['YELLOW'])} and the path to {su.color_text('tesseract', su.ANSI_CODE['YELLOW'])}
    To check where tesseract program is located, type {su.color_text('which tesseract', su.ANSI_CODE['YELLOW'])}
    {su.color_text('Example syntax:', su.ANSI_CODE['CYAN'])} python main.py ./path/to/image.png /path/to/tesseract
            """)
    print("Loading image...")
    sudoku_img = so.load_and_prepare_image(sys.argv[1])
    print("Cropping image...")
    sudoku_img = so.crop_image(sudoku_img)    
    print("Splitting image...")
    # list of split images as a 2d list
    list_of_cells_as_images = so.split_grid(sudoku_img)
    print("Using OCR...")
    # gets list of cell as number
    sudoku_grid = so.image_to_num_grid(list_of_cells_as_images, sys.argv[2])
    # double check the grid
    su.double_check(sudoku_grid)

    is_animated = ""
    while (is_animated:=input("Animate?(y/n) ").lower()) not in {'y', 'n'}:
        pass

    # get the coordinates of the cells that are already given
    given_cells = su.get_non_empty_coord(sudoku_grid)

    # for collecting the solutions
    solutions_list = []

    if is_animated == 'y':
        ss.solve_sudoku_animated(sudoku_grid)
        # the animated algorithm only returns on solution, in the case of possible multiple solutions (the nearest solution)
        solutions_list.append(sudoku_grid)
    else:
        ss.solve_sudoku(sudoku_grid, solutions_list)

    # in case of multiple solutions
    for solutions in solutions_list:
        su.print_board(su.format_grid(solutions, given_cells))

    is_saved = ""
    while (is_saved:=input("Save solution as CSV file?(y/n) ").lower()) not in {'y', 'n'}:
        pass

    if is_saved == "n":
        sys.exit()

    # save and then exit
    save_to_path = ""
    for i, solution in enumerate(solutions_list):        
        while True:
            try:
                save_to_path = input(f"Specify path (solution {i+1}/{len(solutions_list)}): ")
                su.write_sudoku_csv(solution, save_to_path)
            except FileExistsError:
                print("file already exists")
            except FileNotFoundError:
                print("a directory specifed can't be found")
            except KeyboardInterrupt:
                sys.exit("exitting...")
            except:
                print("something went wrong... check your path...")
            
            else:
                break
            
if __name__ == "__main__":
    main()
