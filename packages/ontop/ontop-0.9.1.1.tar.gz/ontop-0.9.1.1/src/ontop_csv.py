
from IPython.core.display import display, HTML
import pandas as pd
from io import StringIO
import os
#from google.colab import files
from random import randint
#from chardet import *
import requests

# def fix_apostrophes(df):
#     """
#     This function replaces single and double quotes in a pandas DataFrame with their escaped versions.

#     Parameters:
#     df (pandas.DataFrame): The DataFrame to be processed.

#     Returns:
#     pandas.DataFrame: The DataFrame with replaced apostrophes.
#     """
#     return df.map(lambda x: x.replace("'", "\\'").replace('"', '\\"') if isinstance(x, str) else x)

# def check_encoding(file_path):
#     """
#     This function checks the encoding of a file.

#     Parameters:
#     file_path (str): The path to the file.

#     Returns:
#     str: The detected encoding of the file.
#     """
#     with open(file_path, 'rb') as f:
#         result = chardet.detect(f.read())
#         encoding = result['encoding']
#     return encoding

def read_table(url: str) -> pd.DataFrame:
    """
    This function reads a CSV file from the given URL and returns it as a pandas DataFrame.
    If the file is not found, it prints an error message and returns None.

    Parameters:
    url (str): The URL of the CSV file to be read.

    Returns:
    pandas.DataFrame: The CSV file as a pandas DataFrame. If the file is not found, returns None.
    """
    try:
        return pd.read_csv(url, encoding='utf-8')
        #return fix_apostrophes(pd.read_csv(url, encoding='utf-8'))
    except FileNotFoundError:
        print(f"Error: File not found at {url}")
        return None  # Or handle the error differently
 

    
'''def filter_data(data, field, value, to_value=None):

    if str(value).isnumeric():
      value = int(value)
    if to_value is None:
        return data[data[field].eq(value)]
    else:
        if str(to_value).isnumeric():
          to_value = int(to_value)
        ge = data[data[field].ge(value)]
        return ge[ge[field].le(to_value)]'''

def filter_data(data, field, value, to_value=None, ignore_case=False):
    matching_columns = [col for col in data.columns if col.lower() == field.lower()]
    if not matching_columns:
        return data.iloc[0:0]

    actual_field = matching_columns[0]
    col_series = data[actual_field]
    col_clean = col_series.fillna("").astype(str)
    value_str = str(value)
    to_str = str(to_value) if to_value is not None else None

    if pd.api.types.is_string_dtype(col_series) or col_series.dtype == "object":
        if ignore_case:
            col_to_filter = col_clean.str.lower()
            value_str = value_str.lower()
            to_str = to_str.lower() if to_str else None
            if to_str:
                mask = (col_to_filter >= value_str) & (col_to_filter <= to_str)
            else:
                mask = col_to_filter == value_str
        else:
            if to_str:
                return data.iloc[0:0]
            mask = col_clean == value_str
    elif pd.api.types.is_numeric_dtype(col_series):
        if to_value is not None:
            mask = (col_series >= value) & (col_series <= to_value)
        else:
            mask = col_series == value
    else:
        return data.iloc[0:0]

    return data[mask]






# def filter_data(data, field, value, to_value=None, ignore_case=False):
#     """
#     This function filters a pandas DataFrame based on a specific field and value range.

#     Parameters:
#     data (pandas.DataFrame): The DataFrame to be filtered.
#     field (str): The name of the column to filter on.
#     value (int, float, str): The value to filter on. If the field is numeric, this value should be numeric as well.
#     to_value (int, float, str, optional): The end of the range to filter on. If provided, the function will filter on the range [value, to_value]. Defaults to None.
#     ignore_case (bool, optional): If True, the function will ignore case when comparing string values. Defaults to False.

#     Returns:
#     pandas.DataFrame: The filtered DataFrame.
#     """
#     processed_field = field.lower() if ignore_case and isinstance(field, str) else field

#     processed_value = str(value).lower() if ignore_case and isinstance(value, str) else value
#     processed_to_value = str(to_value).lower() if ignore_case and isinstance(to_value, str) and to_value is not None else to_value

#     if ignore_case and data[processed_field].dtype == "object":
#         data[processed_field] = data[processed_field].str.lower()

#     if to_value is None:
#         return data[data[processed_field].eq(processed_value)]
#     else:
#         ge = data[data[processed_field].ge(processed_value)]
#         return ge[ge[processed_field].le(processed_to_value)]

'''def print_column(data, field):
    print('\n'.join(data[field]))

def print_column_no_duplicates(data, field):
    print('\n'.join(data[field].unique()))'''

'''def print_csv_top(data, count):
    data['link'] = data['link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
    data.style.set_properties(**{'text-align': 'center'}).set_table_styles(  [{'selector': 'th', 'props': [('font-size', '16px'), ('text-align', 'center')]}])
    display(HTML(data.head(count).to_html(escape=False)))'''
    
def print_csv_top(data, count):
    """
    Prints the top 'count' rows of the given DataFrame 'data' in a formatted manner.

    Parameters:
    data (pandas.DataFrame): The DataFrame from which to extract the top rows.
    count (int): The number of rows to display.

    Returns:
    None
    """
    df_head = data.head(count).copy()
    display(df_head)

def return_data(df, start_index, end_index):
    """
    This function returns a subset of rows from a pandas DataFrame based on the specified start and end indices.

    Parameters:
    df (pandas.DataFrame): The DataFrame from which to extract the subset of rows.
    start_index (int): The index of the first row to include in the subset.
    end_index (int): The index of the last row to include in the subset. This index is exclusive, meaning the row at this index is not included in the subset.

    Returns:
    pandas.DataFrame: A subset of rows from the input DataFrame, starting from 'start_index' and ending at 'end_index' (exclusive).
    """
    return df.iloc[start_index:end_index]


def return_top(data, count):
    """
    This function returns the top 'count' rows from a pandas DataFrame.

    Parameters:
    data (pandas.DataFrame): The DataFrame from which to extract the top rows.
    count (int): The number of rows to display. This value should be a positive integer.

    Returns:
    pandas.DataFrame: A new DataFrame containing the top 'count' rows from the input DataFrame.
    """
    return data.head(count)

def count_data(data):
    """
    This function counts the number of rows in a pandas DataFrame.

    Parameters:
    data (pandas.DataFrame): The DataFrame for which to count the number of rows.

    Returns:
    int: The number of rows in the DataFrame.
    """
    return len(data)

def return_column_values(df: pd.DataFrame, column_name: str):
    """
    This function retrieves all values from a specified column in a pandas DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame from which to retrieve the column values.
    column_name (str): The name of the column from which to retrieve the values.

    Returns:
    List[Any]: A list containing all values from the specified column. If the column does not exist in the DataFrame, a ValueError is raised.
    """
    if column_name in df.columns:
        return df[column_name].tolist()
    else:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

def print_column_values(df: pd.DataFrame, column_name: str):
    """
    Prints the values of a specified column in a pandas DataFrame as an unordered list in HTML format.

    Parameters:
    df (pandas.DataFrame): The DataFrame from which to retrieve the column values.
    column_name (str): The name of the column from which to retrieve the values.

    Returns:
    None

    Raises:
    ValueError: If the specified column does not exist in the DataFrame.

    The function iterates over the values in the specified column, encloses each value in an HTML list item tag,
    and appends it to a string. The resulting string is then displayed as HTML using the IPython.display.HTML function.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

    html_content = "<ul>"
    for value in df[column_name]:
        html_content += f"<li>{value}</li>"
    html_content += "</ul>"
    display(HTML(html_content))

def return_sorted_by_column(df: pd.DataFrame, column_name: str, ascending: bool = False) -> pd.DataFrame:
        """
        This function sorts a pandas DataFrame based on a specified column and returns the sorted DataFrame.
    
        Parameters:
        df (pandas.DataFrame): The DataFrame to be sorted.
        column_name (str): The name of the column to sort by. If the column does not exist in the DataFrame, a ValueError is raised.
        ascending (bool, optional): If True, the DataFrame will be sorted in ascending order. If False, the DataFrame will be sorted in descending order. Defaults to False.
    
        Returns:
        pandas.DataFrame: The sorted DataFrame. The original index is reset to a new index starting from 0.
        """
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")
        return df.sort_values(by=column_name, ascending=ascending).reset_index(drop=True)

def print_sorted_by_column(df: pd.DataFrame, column_name: str, ascending: bool = True):
    """
    Prints a pandas DataFrame sorted by a specified column in ascending or descending order.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be sorted. The DataFrame must not be empty.
    column_name (str): The name of the column to sort by. If the column does not exist in the DataFrame, a ValueError is raised.
    ascending (bool, optional): If True, the DataFrame will be sorted in ascending order. If False, the DataFrame will be sorted in descending order. Defaults to True.

    Returns:
    None

    The function sorts the DataFrame based on the specified column and displays the sorted DataFrame in HTML format.
    The original index is reset to a new index starting from 0.
    The function also applies CSS styles to center the text in the table headers and cells.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")
    sorted_df = df.sort_values(by=column_name, ascending=ascending).reset_index(drop=True)
    sorted_df.style.set_properties(**{'text-align': 'center'}).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '16px'), ('text-align', 'center')]}]
    )
    display(HTML(sorted_df.to_html(index=False)))
