#@title קוד נסתר של לומדה { display-mode: "form" }
#@markdown <div dir="rtl" align="left"> show_gif - מתוך רשימה סגורה של גיפים שמוצגת לחניכים, לפי אינדקס
#@markdown <div dir="rtl" align="left"> show_general_gif - לפי כתובת אינטרנט
#from IPython.display import Image, display
#from IPython.display import HTML
#from IPython.core.display import HTML
#import datetime
from IPython.display import clear_output
#import random
from media import *
from messages import *
from string_table import *
 
# ===========================
#
# ===========================

# gifs = ('https://data.cyber.org.il/OnTopTech/courseware/images/tenor1.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor2.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor3.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor4.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor5.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor6.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor7.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor8.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor9.gif',
        # 'https://data.cyber.org.il/OnTopTech/courseware/images/tenor10.gif')

def is_integer(value):
    """
    Check if a given value is an integer.

    Parameters:
    value (any): The value to be checked.

    Returns:
    bool: True if the value is an integer, False otherwise.
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def show_gif_num(value):
    """
    Display a specific GIF from a list or by URL based on the given value.

    Parameters:
    value (int or str): The index of the GIF in the list (1-based) or the URL of the GIF.
        If the value is an integer, it should be within the range of the available GIFs.
        If the value is a string, it should be a valid URL.

    Returns:
    None: The function does not return any value. It displays the GIF using the IPython.display module.
    """
    gifs = read_gifs()
    if is_integer(value):
        display(Image(url=gifs[value-1]))
    else:
        display(Image(url=value))