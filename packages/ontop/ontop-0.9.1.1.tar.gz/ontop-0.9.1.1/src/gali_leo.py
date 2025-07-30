from media import *
from html_helper import *
from messages import *
from string_table import *
from maps import *


def compare_list(list_color, lst):
    """
    This function compares a given list with an integer list fetched from a remote server.
    The function fetches the integer list from a file named "<list_color>_list.txt" located in a specific S3 bucket.
    If the fetched list matches the given list, it shows a success image. Otherwise, it shows a failure image.

    Parameters:
    list_color (str): The color of the list to fetch from the server. This is used to construct the file name.
    lst (list): The list to compare with the fetched list.

    Returns:
    bool: True if the fetched list matches the given list, False otherwise.
    """
    #file_url =  "https://ontopnew.s3.il-central-1.amazonaws.com/TEST/int_list.txt"
    try:
        file_name = list_color + "_list.txt"
        file_url = "https://ontopnew.s3.il-central-1.amazonaws.com/gali_leo/" + file_name
        #file_url = "https://ontopnew.s3.il-central-1.amazonaws.com/TEST/int_list.txt"
        response = requests.get(file_url)
        response.raise_for_status()
        fixed_list = response.text.strip().split(',')
        fixed_list = [int(item.strip()) for item in fixed_list]
        if lst == fixed_list:
            s = get_string_from_string_table('gali_leo', 'correct')
            
            show_image("https://ontopnew.s3.il-central-1.amazonaws.com/library/gifs/37.gif")
            print(s)
            return True
        else:
            s = get_string_from_string_table('gali_leo', 'wrong')
            
            show_image("https://ontopnew.s3.il-central-1.amazonaws.com/library/gifs/36.gif")
            print(s)
            return False
    except FileNotFoundError:    
        print("Error: File Not Found Error.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return False
    except ValueError:
        print("Error: File contains non-integer values.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False