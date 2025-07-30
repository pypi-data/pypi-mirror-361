from media import *
from html_helper import *
from messages import *
from string_table import *
import sys



#import pandas as pd
#from IPython.display import HTML, display


def unlock_code(code):
    """
    This function retrieves a GIF file path based on a given code and displays it.
    The function reads a CSV file containing code-to-GIF mapping, creates a dictionary for the mapping,
    and then retrieves the GIF path based on the provided code.
    If a GIF path is found, it displays the GIF using IPython's HTML display.
    If no GIF path is found, it prints a message indicating that no GIF was found for the given code.

    Parameters:
    code (str): The code for which to retrieve and display the corresponding GIF.

    Returns:
    None
    """
    df = pd.read_csv('https://ontopnew.s3.il-central-1.amazonaws.com/CodeHelper/code_for_gif.csv')
    gif_mapping = {}
    for index, row in df.iterrows():
        csv_code = row['קוד']
        gif_name = row['קובץ']
        gif_mapping[csv_code] = f"https://ontopnew.s3.il-central-1.amazonaws.com/CodeHelper/{gif_name}"
    gif_path = gif_mapping.get(code)
    if gif_path:
        display(HTML(f'<img src="{gif_path}" />'))
    else:
        print(f"לא נמצא קובץ GIF עבור קוד {code}")