# sudoku-solver
A python program that takes in an image of a sudoku puzzle and outputs its answer.


## Installation

This library uses [`tesseract-ocr`](https://github.com/tesseract-ocr/tesseract) for OCR.


### Installation of python library and tesseract

*Note:* this installation mainly focuses on UNIX based systems. I have absolutely no idea how this setup would go on Windows machines.

First download the package.


```bash
pip install sudoku-solver-ocr
```

On UNIX systems, we need to install `tesseract` through the package manager on your system.

On debian based systems:
```bash
sudo apt-get install tesseract-ocr
```

On Arch based systems:
```bash
sudo pacman -Sy tesseract
```

Verify that it's installed:
```bash
tesseract --version
```

### Configuring `tessdata`

Find `tessdata` directory using `fzf` (can be installed using `apt install fzf` etc...)

```bash
find / -name tessdata |fzf
```

You may get a result like this:

```
/usr/share/tessdata
```

or generally:
```bash
/path/to/tessdata
```

Setup the environmental variable called `TESSDATA_PREFIX` in `~/.bashrc`

```bash
echo "export TESSDATA_PREFIX=/path/to/tessdata" >> ~/.bashrc
```

Source the `~/.bashrc` file

```bash
source ~/.bashrc
```

Verify by recalling the environmental variable.

```bash
echo $TESSDATA_PREFIX
```

Should result in something like this:

```
/path/to/tessdata
```

in my case:

```
/usr/share/tessdata
```

Change directory to `$TESSDATA_PREFIX`

```
cd $TESSDATA_PREFIX
```

Check that `eng.traineddata ` is in the directory using the `ls` command.

If it isn't in the directory, download the file from [here](https://github.com/tesseract-ocr/tessdata) and move it to the `$TESSDATA_PREFIX` directory.


## Using it as a CLI program

**Note**: The computer vision algorithm used to detect and process the sudoku grid isn't very sophisticated. In short, this is the algorithm:

1. load the image
2. crop the image by detecting external borders (no perspective transform)
3. split the cells by detecting contours of the cell in the grid (very error prone)
4. feed the cells one by one into an `tesseract-ocr` (very slow)

As such, it's best not to use it on sudoku puzzles images taken through a camera. From testing, these sudoku sites work best with the program (from best to worst):

1. [websudoku](https://www.websudoku.com/)
2. [printable sudoku](https://sudoku.com/sudoku-printable)
3. [sudoku web](https://www.sudokuweb.org/)
4. [nytimes sodoku](https://www.nytimes.com/puzzles/sudoku/hard)
5. [sudoku.com](https://sudoku.com/)

And from testing, it seems like it's best if the image's resolution is not too high while not being too low either.

First take a screenshot of a sudoku board from an online website as such:

![screenshot of websudoku](https://i.imgur.com/7eHncrJ.png)

Now run the following command:

```bash
python3 -m sudoku_solver_ocr ./path/to/image /path/to/tesseract 
```

- `./path/to/image` is path to the image from your current working directory.
- `/path/to/tesseract` is the path to the tesseract program itself. It can be checked by running `which tesseract`

I've stored it in `web_sudoku.png` in my current working directory and my path to `tesseract` is at `/sbin/tesseract`.
Therefore, I'll run:

```bash
python3 -m sudoku_solver_ocr ./web_sudoku.png /sbin/tesseract
```

If no error arises, a sudoku board should appear in your screen.

```
Loading image...
Cropping image...
Splitting image...
Using OCR...
  0   1   2   3   4   5   6   7   8   
╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗
║   ┃   ┃   ║   ┃ 4 ┃ 6 ║   ┃ 2 ┃   ║0
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║   ┃ 6 ┃ 1 ║ 3 ┃   ┃   ║   ┃ 7 ┃   ║1
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║   ┃   ┃ 7 ║   ┃   ┃   ║   ┃   ┃ 3 ║2
╠═══╪═══╪═══╫═══╪═══╪═══╫═══╪═══╪═══╣
║   ┃   ┃   ║   ┃ 6 ┃ 9 ║   ┃ 3 ┃   ║3
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║   ┃   ┃ 3 ║   ┃   ┃   ║ 4 ┃   ┃   ║4
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║   ┃ 5 ┃   ║ 2 ┃ 1 ┃   ║   ┃   ┃   ║5
╠═══╪═══╪═══╫═══╪═══╪═══╫═══╪═══╪═══╣
║ 5 ┃   ┃   ║   ┃   ┃   ║ 2 ┃   ┃   ║6
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║   ┃ 3 ┃   ║   ┃   ┃ 2 ║ 9 ┃ 1 ┃   ║7
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║   ┃ 2 ┃   ║ 8 ┃ 9 ┃   ║   ┃   ┃   ║8
╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝

Please recheck your sudoku board:
- help
- ok
- replace <x> <y> <n>
input a command: 
```

As suggested, if the board is incorrect, this interface allows us to `replace` a particular cell given an `x`, a `y` and a number to insert `n`.
The command list is of follows:
- `help` simply prints some information about sudoku
- `replace <x> <y> <n>` places a number `n` which can be from `0` to `9` (`0` to place an empty cell) at coordinates (`x`, `y`).
- `ok` command breaks out of the loop and feeds the following board into a sudoku solver.

Once `ok` is entered, we can either solve it while visualizing it or simply solve it and print the solution (animating it intentionally slows the algorithm down).

```
✅ Final board accepted.
Animate?(y/n) 
```

I'll simply type `n`.

If all goes well, we should be greeted with a solved sudoku board.

```
  0   1   2   3   4   5   6   7   8   
╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗
║ 3 ┃ 8 ┃ 5 ║ 7 ┃ 4 ┃ 6 ║ 1 ┃ 2 ┃ 9 ║0
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║ 9 ┃ 6 ┃ 1 ║ 3 ┃ 2 ┃ 5 ║ 8 ┃ 7 ┃ 4 ║1
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║ 2 ┃ 4 ┃ 7 ║ 9 ┃ 8 ┃ 1 ║ 6 ┃ 5 ┃ 3 ║2
╠═══╪═══╪═══╫═══╪═══╪═══╫═══╪═══╪═══╣
║ 8 ┃ 7 ┃ 2 ║ 4 ┃ 6 ┃ 9 ║ 5 ┃ 3 ┃ 1 ║3
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║ 6 ┃ 1 ┃ 3 ║ 5 ┃ 7 ┃ 8 ║ 4 ┃ 9 ┃ 2 ║4
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║ 4 ┃ 5 ┃ 9 ║ 2 ┃ 1 ┃ 3 ║ 7 ┃ 8 ┃ 6 ║5
╠═══╪═══╪═══╫═══╪═══╪═══╫═══╪═══╪═══╣
║ 5 ┃ 9 ┃ 8 ║ 1 ┃ 3 ┃ 4 ║ 2 ┃ 6 ┃ 7 ║6
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║ 7 ┃ 3 ┃ 4 ║ 6 ┃ 5 ┃ 2 ║ 9 ┃ 1 ┃ 8 ║7
╟━━━┿━━━┿━━━╫━━━┿━━━┿━━━╫━━━┿━━━┿━━━╢
║ 1 ┃ 2 ┃ 6 ║ 8 ┃ 9 ┃ 7 ║ 3 ┃ 4 ┃ 5 ║8
╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝

Save solution as CSV file?(y/n) 
```

We can save the solution as a `.csv` file. For instance, if I want to save it in `sudoku_solution.csv`:

```
Save solution as CSV file?(y/n) y
Specify path (solution 1/1): sudoku_solution.csv
```

Now we can check that the solution is saved in `sudoku_solution.csv`.

CSV data as plain text:

```
3,8,5,7,4,6,1,2,9
9,6,1,3,2,5,8,7,4
2,4,7,9,8,1,6,5,3
8,7,2,4,6,9,5,3,1
6,1,3,5,7,8,4,9,2
4,5,9,2,1,3,7,8,6
5,9,8,1,3,4,2,6,7
7,3,4,6,5,2,9,1,8
1,2,6,8,9,7,3,4,5
```

## Using it as a library

Once it's installed, simply import the library:

```python
import sudoku_solver_ocr as sso
```

This is an overview of all the functions, more details can be extracted by reading the source code (as it's not very long).

A sudoku grid is represented a 2d list of integers which has dimensions 9x9.

**Note:** these functions all lie under `sudoku_solver_ocr` when importing. I've divded it only because the functions lie in 3 different files.

### sudoku_utils.py

This file provides useful utility functions used throughout the program.


|function|details|
|---|---|
|`read_sudoku_csv`|opens a sudoku grid in a `.csv` file and outputs 2d list representation of the grid|
|`write_sudoku_csv`|writes a 2d list representation of a sudoku puzzle to `.csv` file|
|`print_board`|prints the 2d list representation of the sudoku puzzle to stdout in a nice sudoku board format|
|`show_help`|simply prints basic info about sudoku to stdout|
|`color_text`|wraps a string with ANSI code to make that string a certain color|
|`double_check`|runs a interactive user interface to edit the given sudoku board|
|`format_grid`|prepares the 2d list of `int` to a 2d list of `str` to print it nicely to stdout (replacing all `0` with `' '`, apply coloring, etc)|
|`get_non_empty_coord`|returns a set of the non empty (non `0`) coordinates as a tuple representing coordinates (`y`, `x`)|

This file also contains a dictionary called `ANSI_CODE` which maps a color to an ANSI code. This is useful for coloring strings.

### sudoku_ocr.py

This file provides tools used to convert sudoku images to plain text.

|function|details|
|---|---|
|`load_and_prepare_image`|loads the sudoku image, grayscale the image and also binarize it|
|`crop_image`|simply detects an external border of the sudoku grid and crops it. Splits out the cropped image|
|`split_grid`|splits the sudoku grid image to 81 images representing cells that either contain a number or nothing. This is all then stored in a 2d list.|
|`image_to_num_grid`|does OCR on the output of `split_grid` which is a 2d list of images. The path to the `tesseract` is also an argument here|

### sudoku_solver.py

This file provides all the functions used to solve a sudoku puzzle.

|function|details|
|---|---|
|`is_possible`|checks whether a number `n` can be placed at a particular cell of coordinates (`x`, `y`)|
|`solve_sudoku`|collects the solution of a sudoku puzzle in a list (in case the sudoku puzzle isn't well designed or you've messed up with editting the cells)|
|`solve_sudoku_single_solution`|is faster than `solve_sudoku` but assume that there's only one solution|
|`solve_sudoku_animated`|solve the sudoku puzzle while also printing the state of the sudoku board to stdout while solving|


