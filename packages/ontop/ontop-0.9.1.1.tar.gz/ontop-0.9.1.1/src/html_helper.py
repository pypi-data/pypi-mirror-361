
import requests
from IPython.display import HTML, display
import re



def download_html(url):
    """
    Downloads and returns the HTML content of the given URL.

    Parameters:
    url (str): The URL from which to download the HTML content.

    Returns:
    str: The HTML content of the specified URL.
    """
    response = requests.get(url)
    html = response.text
    return html


def html_print(text):
  """
    Displays the given text as an HTML paragraph in a Jupyter notebook, automatically setting the text direction
    to right-to-left (rtl) if Hebrew or Arabic characters are detected, or left-to-right (ltr) otherwise.
    Args:
        text (str): The text to display as HTML.
    Returns:
        None
    Note:
        Requires IPython.display.HTML and display, as well as the re module for regular expressions.
  """
  rtl_pattern = re.compile(r'[\u0590-\u05FF\u0600-\u06FF]')
  if rtl_pattern.search(text):
    direction = "rtl"
  else:
    direction = "ltr"

  html_code = f'<p dir="{direction}" style="text-align: left;">{text}</p>'

  display(HTML(html_code))
