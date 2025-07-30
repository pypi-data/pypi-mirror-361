from IPython.display import display, clear_output, IFrame, HTML, Javascript
import requests
from IPython.core.display import display, HTML
import pandas as pd
from io import StringIO
import os
#from google.colab import files
from random import randint


labels = []
data = []
expected_list = []
excpected_num = 0

def fix_str_apostrophes(input_string):
    """
    This function replaces single and double quotes in a string with their escaped versions.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be processed.

    Returns:
    pandas.DataFrame: The DataFrame with replaced apostrophes.
    """
    string_without_quotes = input_string.replace("'", "").replace('"', '')
    return string_without_quotes


def new_graph():
    """
    Initializes the global variables used for creating a graph.

    This function is responsible for resetting the graph data and expected values.
    It sets the 'labels', 'data', 'expected_list', and 'excpected_num' global variables to their initial states.

    Parameters:
    None

    Returns:
    None
    """
    global labels
    labels = []
    global data
    data = []
    global expected_list
    expected_list = [0]*1000  # shany (was 13)
    global excpected_num
    excpected_num = 0

def add_bar_to_graph(label, value):
    """
    Adds a bar to the graph with the given label and value.

    This function takes a label and a value as input, cleans the label by removing single and double quotes,
    and converts the value to an integer if it is numeric. The cleaned label and the converted value are then
    appended to the global 'labels' and 'data' lists, respectively.

    Parameters:
    label (str): The label for the bar to be added to the graph.
    value (str or int): The value for the bar to be added to the graph.

    Returns:
    None
    """
    global labels
    global data
    label = fix_str_apostrophes(label)
    if str(value).isnumeric():
        value = int(value)
    labels.append(label)
    data.append(value)

def create_graph(title, x_title, y_title):
    """
    This function creates a bar chart with a line chart overlay using Chart.js.
    It takes in the chart's title, x-axis title, and y-axis title as parameters.
    The function uses global variables 'labels', 'data', 'expected_list', and 'excpected_num' to populate the chart.
    The function fetches an HTML template from a URL and replaces placeholders with actual values.
    itws use graph.js to create a bar chart with a line chart overlay.
    The chart is then returned as an HTML string.
    Parameters:
    title (str): The title of the chart.
    x_title (str): The title of the x-axis.
    y_title (str): The title of the y-axis.

    Returns:
    str: The HTML code for the chart, which can be displayed in an IPython notebook or web page.
    """
    global labels
    global data
    global expected_list
    global excpected_num

    # Initialize strings for labels, data, and expected values
    label_str = ""
    data_str = ""
    expected_str = ""

    # Fetch the HTML template for the chart from a URL
    url = 'http://data.cyber.org.il/OnTop/HtmlTests/chartjs_bar_with_line_template1.html'
    response = requests.get(url)
    html = response.text

    # Populate the label string with labels from the 'labels' list
    for item in labels:
        label_str += "'" + item + "',"

    # Populate the data string with data from the 'data' list
    for item in data:
        data_str += str(item) + ","

    # Populate the expected string with expected values from the 'expected_list'
    if len(expected_list) > 1:
        for item in range(2, excpected_num + 2):
            expected_str += str(expected_list[item]) + ","
    else:
        for item in excpected_num:
            expected_str += str(item) + ","

    # Remove trailing commas from the strings
    label_str = label_str[:-1]
    data_str = data_str[:-1]
    expected_str = expected_str[:-1]

    # Replace placeholders in the HTML template with the actual values
    html = html.replace('*labels*', label_str)
    html = html.replace("*data*", data_str)
    html = html.replace("*title*", title)
    html = html.replace("*x_title*", x_title)
    html = html.replace("*y_title*", y_title)
    html = html.replace("*expected*", expected_str)

    return html;


def draw_graph(title, x_title, y_title):
    """
    This function draws a bar chart with a line chart overlay using Chart.js.
    It takes in the chart's title, x-axis title, and y-axis title as parameters.
    The function uses the `create_graph` function to generate the HTML code for the chart.
    The chart is then displayed in an IPython notebook using the `display` function from the `IPython.display` module.

    Parameters:
    title (str): The title of the chart.
    x_title (str): The title of the x-axis.
    y_title (str): The title of the y-axis.

    Returns:
    None
    """
    html = create_graph(title, x_title, y_title)
    display(HTML(html))
  #display(HTML(f'<iframe srcdoc="{html}" width="500" height="200"></iframe>'))
  #display(HTML(f'<iframe srcdoc="{html2}" width="500" height="200"></iframe>'))
  #with open('graph ' + str(randint(1,1000)) + '.html', 'w') as f: # Changed random to randint
  #  f.write(html)
  #files.download('text_file' + str(randint(200,300))+'.html') # Changed random to randint

