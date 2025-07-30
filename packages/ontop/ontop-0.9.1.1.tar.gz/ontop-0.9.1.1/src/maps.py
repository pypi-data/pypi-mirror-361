from IPython.display import display, HTML
import folium
from media import *
from html_helper import *
from messages import *
from string_table import *



def compare_list_1(lst):
    """
    Compares a given list with a fixed list and checks if they are equal.

    Parameters:
    lst (list): The list to be compared.

    Returns:
    bool: True if the given list is equal to the fixed list, False otherwise.
    """
    fixed_list = [-7,7,8,1,9,9,9,5]
    return lst == fixed_list

def compare_list_2(lst):
    """
    Compares a given list with a fixed list and checks if they are equal.

    Parameters:
    lst (list): The list to be compared. This list should contain integers.

    Returns:
    bool: True if the given list is equal to the fixed list, False otherwise.
    The fixed list is defined as [2,5,7,1,8,9,6,6].
    """
    fixed_list = [2,5,7,1,8,9,6,6,]
    return lst == fixed_list

def list_to_coordinate(fixed_list):
    """
    Converts a list of integers into a single floating-point coordinate.

    The function takes a list of integers as input and converts it into a string.
    It then processes the string to extract a floating-point coordinate.
    If the input list is empty, the function returns 0.0.
    If the first character of the string is '-', the function extracts a coordinate with up to 3 digits before the decimal point.
    Otherwise, it extracts a coordinate with up to 2 digits before the decimal point.

    Parameters:
    fixed_list (list): A list of integers.

    Returns:
    float: A floating-point coordinate derived from the input list.
    """
    str_coordinate = "".join(map(str, fixed_list))
    if not str_coordinate:
        return 0.0
    if str_coordinate[0] == '-':
        if len(str_coordinate) > 3:
            coordinate = float(str_coordinate[:3] + "." + str_coordinate[3:])
        else:
            coordinate = float(str_coordinate)
    else:
        if len(str_coordinate) > 2:
            coordinate = float(str_coordinate[:2] + "." + str_coordinate[2:])
        else:
            coordinate = float(str_coordinate)
    return coordinate

def show_coordinates_on_google_maps(latitude, longitude):
    """
    This function generates a hyperlink to open Google Maps in a new tab,
    given a specific latitude and longitude.

    Parameters:
    latitude (float): The latitude coordinate of the location to be displayed on Google Maps.
    longitude (float): The longitude coordinate of the location to be displayed on Google Maps.

    Returns:
    None: The function does not return any value. It only displays a hyperlink in the Jupyter notebook.
    """
    s = get_string_from_string_table('gali_leo', 'open_in_map')
    url = f"https://www.google.com/maps/place/{latitude},{longitude}"
    display(HTML(f'<a href="{url}" target="_blank"> ' + s + ' </a>'))
    
    
def create_map(latitude, longitude, popup_sign=""):
    """
    This function creates and displays a map using the folium library.
    It places a marker at the specified latitude and longitude coordinates,
    and optionally displays a popup sign when the marker is clicked.

    Parameters:
    latitude (float): The latitude coordinate of the location to be displayed on the map.
    longitude (float): The longitude coordinate of the location to be displayed on the map.
    popup_sign (str, optional): The text to be displayed in the popup when the marker is clicked. Defaults to an empty string.

    Returns:
    None: The function does not return any value. It only displays a map in the Jupyter notebook.
    """
    tzur_moshe_coords = [latitude, longitude]

    m = folium.Map(location=tzur_moshe_coords, zoom_start=15)

    folium.Marker(
        location=tzur_moshe_coords,
        popup=popup_sign,
        icon=folium.Icon(color="blue")
    ).add_to(m)
    display(m)
   