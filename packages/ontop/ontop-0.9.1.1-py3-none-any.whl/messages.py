from string_table import *
from media import *


def error_msg(func, msg):
  """ 
    Prints an error message with a specified function name and message. 
    
    Parameters: 
    ----------    
    func (str): The name of the function where the error occurred. 
    msg (str): The error message to be displayed. 
    
    Returns: 
    -------    
    None 
  """
  print("\n")
  s = get_string_from_string_table("trivia","error")
  print(print_background(print_color(func+" " + s, colors.WHITE), colors.RED))
  print(msg)
  s = get_string_from_string_table("trivia",",msg1")
  print(s)
  print("\n")