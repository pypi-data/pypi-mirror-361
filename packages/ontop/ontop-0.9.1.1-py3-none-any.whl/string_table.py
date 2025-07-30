from pandas.core.frame import DataFrame
import pandas as pd
#from google.colab import data_table
import numpy as np
import time
import datetime

language = 'hebrew'

def set_language(lang):
  """
  This function is used to set the language preference  
  in the application. Once set, the `language` variable can be 
  used throughout the program.

  Parameters:
  ----------
  lang : str
  The language code or name to set (e.g., 'hebrew' or 'arabic').
  """  
  global language
  language = lang


def get_language():
  """
    Retrieves the current global language setting.

    Returns:
    -------
    str
        The current value of the global `language` variable.
  """
  global language
  try:
    return language
  except NameError:
    raise NameError("The global variable 'language' is not defined. Please set it using set_language().")

def read_table(url):
    """
        Reads a CSV file containing Hebrew strings and their Arabic translations.
        This function reads a CSV file from the specified URL or file path and 
        returns the content as a pandas DataFrame. It assumes the file uses 
        UTF-8 encoding to handle Hebrew and Arabic characters correctly.

        Parameters:
        ----------
        url : str
            The file path or URL of the CSV file to read.

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing the data from the CSV file.

        Notes:
        ------
        - Ensure the CSV file is properly formatted with UTF-8 encoding.
        - The CSV is expected to have Hebrew strings and their Arabic translations.
        - This function requires the `pandas` library to be installed.

        Examples:
        ---------
        >>> df = read_table("translations.csv")
        >>> print(df.head())
    """  
    return pd.read_csv(url, encoding='utf-8')

def filter_data(data, field, value, to_value=None):
  """
    Filters a DataFrame based on a specified field and value range.
    This function filters the input DataFrame `data` by selecting rows where
    the specified `field` equals a given value (`value`) or falls within a 
    range defined by `value` and `to_value`.

    Parameters:
    ----------
    data : pandas.DataFrame
        The DataFrame to be filtered.
    field : str
        The name of the column to filter on.
    value : int or str
        The starting value or exact match value for the filtering. Strings that 
        are numeric are converted to integers.
    to_value : int or str, optional
        The ending value for range filtering. Strings that are numeric are 
        converted to integers. If not provided, filtering will be based only on `value`.

    Returns:
    -------
    pandas.DataFrame
        A filtered DataFrame containing rows that match the filter criteria.
  """
# Check if 'value' is numeric (string representation of a number) and convert to int
  if str(value).isnumeric():
    value = int(value)
# If 'to_value' is not provided, filter based on exact match with 'value'
  if to_value is None:
    return data[data[field].eq(value)]
  else:
# If 'to_value' is provided, check if it is numeric (string representation of a number) and convert to int
    if str(to_value).isnumeric():
       to_value = int(to_value)
# Filter for rows where the field value is greater than or equal to 'value'
  ge = data[data[field].ge(value)]
# Filter for rows where the field value is greater than or equal to 'value'
  ge = data[data[field].ge(value)]  # 'ge' is for "greater than or equal"
# Further filter for rows where the field value is less than or equal to 'to_value'
  return ge[ge[field].le(to_value)]  # 'le' is for "less than or equal"  

def get_columns(data, field):
  """
    Retrieves a column from the DataFrame.

    Parameters:
    ----------
    data : pandas.DataFrame
        The DataFrame containing the column.
    field : str
        The name of the column to retrieve.

    Returns:
    -------
    pandas.Series
        The specified column as a pandas Series.
  """
  return data[field]

def get_string_from_string_table(project, name):
  """ 
    Retrieves a string from the string table based on the project and name. 
    
    Parameters:
    ----------
        project (str): The project name to filter the table. 
    name (str): The name to filter the data within the project. 
    
    Returns:
    -------    
        str: The string corresponding to the given project and name. 
    Returns '0' if not found. 
  """    
  global language
# Read the string table from the provided URL
  table = read_table('https://ontopnew.s3.il-central-1.amazonaws.com/library/StringTable/string_table_utf.csv')
# Filter the table for the specified project
  project_table = table.query("project == @project")
# Filter the data within the project for the specified name  
  result = filter_data(project_table, "name", name)
# Get the column data for the current language  
  column = get_columns(result, language)

# Return the first item in the column, if it exists
  for item in column:
    return item

# Return '0' if no item was found    
  return '0'


def get_banners_strings(project_name='banner'):
  """ 
    Retrieves the list of strings from the string table for the 'banner' project.

    Parameters: 
    ----------    
    project_name (str): The name of the project to filter the table (default is 'banner'). 
    
    Returns: 
    -------    
    list: A list of strings corresponding to the given project name. 
  """    
  global language
  project_name = 'banner'
  csv_file='https://ontopnew.s3.il-central-1.amazonaws.com/library/StringTable/string_table_utf.csv'
  table = pd.read_csv(csv_file, encoding='utf-8')
  project_data = table.query("project == @project_name")
  strings = project_data[language].tolist()
  return strings
 
 
 
 