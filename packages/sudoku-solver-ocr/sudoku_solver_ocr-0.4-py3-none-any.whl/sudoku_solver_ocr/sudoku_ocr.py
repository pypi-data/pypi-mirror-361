import cv2
import pytesseract
import numpy as np
from . import sudoku_utils

def load_and_prepare_image(path_to_image:str)->np.ndarray:
    """
    first loads the image, then continue to prepare it for further manipulation

    path_to_image (str): the relative path to the sudoku image

    return: opencv image (NumPy array)
    """
    img = cv2.imread(path_to_image)

    # converts it to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # converts it to black and white
    thresh = cv2.adaptiveThreshold(gray,
                            255, # make the background white to the highest intensity 
                            cv2.ADAPTIVE_THRESH_MEAN_C, # not sure what the rest of these does...
                            cv2.THRESH_BINARY_INV,
                            11,
                            2) 
    return thresh
        
    
def crop_image(uncropped_img:np.ndarray)->np.ndarray:
    """
    Crops the image based on the surrouding, external bounding box

    uncropped_img (NumPy array for opencv images): uncropped image of the sudoku grid

    return: opencv image 
    """
    # first find the external contours of the image

    surrounding_contour, _ = cv2.findContours(uncropped_img,
                                cv2.RETR_EXTERNAL,# only return the external contour
                                cv2.CHAIN_APPROX_SIMPLE) # probably some algorithm to find contours
                                    
    # surrounding contour should only be of length one
    # gets the bounding rectangle of the surrounding borders
    if len(surrounding_contour) == 1: 
        x, y, w, h = cv2.boundingRect(surrounding_contour[0])
        
        # crop the image
        # this syntax just says, get the pixel from y until y + h, from x until x + w
        cropped_image = uncropped_img[y:y+h, x:x+h]

        return cropped_image
    else:
        raise Exception("Please retake the picture. Can't find external borders. ")      
                

def split_grid(sudoku_img:np.ndarray)->list:
    """
    Given an image of a sudoku puzzle, this function will split the image into 81 images of its cells. 

    sudoku_img (NumPy array for opencv images): an image of the sudoku puzzle

    return: a 2d list representing the grid of a sudoku puzzle
    """
    contours, _ = cv2.findContours(sudoku_img,
                                cv2.RETR_LIST, # returns list of all contours
                                cv2.CHAIN_APPROX_SIMPLE)
    sudoku_img_height, sudoku_img_width = sudoku_img.shape[:2]
    image_area = sudoku_img_height * sudoku_img_width
    
    def filter_contours(contour_to_check):
        contour_area = cv2.contourArea(contour_to_check)
        
        # a bit arbitrary but decide that contour isn't a grid if:
        # - size is bigger than 0.9 of image size (filter out surrounding border contour)
        is_surrounding_border = (contour_area > image_area*0.9) 
        # - size is smaller than image_area/81 * 0.75 which is the theoretical size but add 0.75 error tolerance (to filter out numbers) or has aspect ratio that isn't "square enough"
        is_too_small = (contour_area < (image_area/81)*0.75)

        width, height = cv2.boundingRect(contour_to_check)[2:]
        aspect_ratio = width/float(height)
        
        is_square_enough = (0.8 < aspect_ratio < 1.2)

        return (not is_surrounding_border) and (not is_too_small) and (is_square_enough)
        
    grid_contour = list(filter(filter_contours, contours))

    # after filtering contour, order the pictures into a 2d list representing a grid 
    if len(grid_contour) == 81:
        # check that there are 81 cells in the grids

        # sort the list of grids
        list_of_coord_and_cell = []
        for cell in grid_contour:
            x, y, w, h = cv2.boundingRect(cell)
            # first find the centroid of the cell. (y, x) instead of (x, y) for sorting purposes
            # then normalize it to 9x9 (floor it to fit)
            coordinates_of_centroid = (int(((y+(h/2))/sudoku_img_height)*9), 
                                        int(((x+(w/2))/sudoku_img_width)*9))

            # get the image cropped via contour
            y1 = max(0, y + int(0.075 * h))
            y2 = min(sudoku_img_height, y + int(0.925 * h))
            x1 = max(0, x + int(0.075 * w))
            x2 = min(sudoku_img_width, x + int(0.925 * w))
            
            image_of_cell = sudoku_img[y1:y2, x1:x2]
            
            list_of_coord_and_cell.append((*coordinates_of_centroid, image_of_cell))

        
        # sort the list
        list_of_coord_and_cell.sort()

        # remove the temporary coordinate of centroid used for sorting
        list_of_sorted_cells = [cell[2] for cell in list_of_coord_and_cell]

        # turn the list into a 2d list which contains 9 list of 9 elements and zreturns it

        return [list_of_sorted_cells[i * 9:(i + 1) * 9] for i in range(9)]
        
    else:
        raise Exception("Please take another picture. Make sure the sudoku grid is square.")

def image_to_num_grid(grid_of_img:list, path_to_pytesseract:str="/sbin/tesseract") -> list:
    """
    Inputs a 2d, 9x9 list containing opencv images which represents a sudoku cell.

    grid_of_img (list): a 2d list of opencv images (NumPy array)

    path_to_pytesseract (str): a path to either pytesseract.exe or just pytesseract. Can be found using "find / -type d -name tessdata 2>/dev/null" for UNIX systems

    For UNIX systems, make sure to export TESSDATA_PREFIX=/path/to/tessdata to ~/.bashrc
    And download eng.traineddata into /path/to/tessdata/
    From: https://github.com/tesseract-ocr/tessdata
    
    return: a 2d list of numbers (0 to 9)
    """
    pytesseract.pytesseract.tesseract_cmd = path_to_pytesseract
    # assume 9x9 grid. Can't bother to check...

    def str_to_int(text):
        # print(text)
        if text == '':
            return 0
        else:
            # in case it detects a number as 2 digit numbers
            return int(text[0])
    
    grid_of_num = grid_of_img.copy()
    
    for y in range(9):
        for x in range(9):        
            # inverting the image back to white background

            if cv2.countNonZero(img:=grid_of_img[y][x]) == 0:
                # if the image is all white (blank), don't feed it into OCR 
                grid_of_img[y][x] = 0
            else:
                inverted_img = cv2.bitwise_not(img)
                text = pytesseract.image_to_string(inverted_img,
                lang='eng',
                config='--psm 10 -c tessedit_char_whitelist=123456789')
                grid_of_num[y][x] = str_to_int(text.strip())        

    return grid_of_num
