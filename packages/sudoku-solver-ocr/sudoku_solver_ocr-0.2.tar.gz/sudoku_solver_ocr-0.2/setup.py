from setuptools import setup, find_packages

setup(
    name="sudoku_solver_ocr",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'pytesseract'
    ]
)
