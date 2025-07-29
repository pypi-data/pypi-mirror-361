from setuptools import setup, find_packages

setup(
    name="sudoku_solver_ocr",
    version="0.3",
    packages=find_packages(),
    author="k1m-ch1",
    description="This program first converts a screenshot of a sudoku grid into plain text. Afterwards, it will solve the sudoku puzzle, display the result and save the solution as a .csv file.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/COSC111-sudoku-solver/sudoku-solver",  # Optional
    install_requires=[
        'opencv-python',
        'pytesseract'
    ]
)
