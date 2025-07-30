# media.py
import os
from pickle import NONE
from IPython.display import display, Javascript
from IPython.core.display import HTML
import time
import datetime
import random
import requests
from IPython.display import Image
from urllib.request import urlopen
from google.colab.output import eval_js
from base64 import b64decode, b64encode
import base64
import urllib.request

from string_table import *

class colors:
    """
    A class representing various color codes in RGB format.

    Attributes:
        RED (tuple): A tuple representing the RGB values for red color.
        ORANGE (tuple): A tuple representing the RGB values for orange color.
        YELLOW (tuple): A tuple representing the RGB values for yellow color.
        GREEN (tuple): A tuple representing the RGB values for green color.
        BLUE (tuple): A tuple representing the RGB values for blue color.
        PURPLE (tuple): A tuple representing the RGB values for purple color.
        WHITE (tuple): A tuple representing the RGB values for white color.
    """
    RED = (234, 50, 31)
    ORANGE = (245, 170, 66)
    YELLOW = (245, 252, 71)
    GREEN = (0, 183, 77)
    BLUE = (71, 177, 252)
    PURPLE = (189, 71, 252)
    WHITE = (255, 255, 255)

def print_color(text, rgb):
    """
    Prints the given text in the specified RGB color to the console.

    Parameters: 
    ----------    
        text (str): The text to be printed.
        rgb (tuple): A tuple of three integers representing the Red, Green, and Blue color components (e.g., (255, 0, 0) for red).

    Returns:
    ----------            
        str: The formatted string with ANSI escape codes for color.
    """
    #return "\033[38;2;{};{};{}m{}\033[0m".format(str(rgb[0]), str(rgb[1]), str(rgb[2]), text)
    r, g, b = rgb
    return (f"\033[38;2;{r};{g};{b}m{text}\033[0m")

def print_background(text, rgb):
    """
    Prints the given text with a colored background.

    Parameters: 
    ----------    
        text (str): The text to be printed.
        rgb (tuple): A tuple of three integers representing the Red, Green, and Blue color components for the background color.

    Returns:
    ----------   
        str: The formatted string with ANSI escape codes for background color.
    """
    return "\033[48;2;{};{};{}m{}\033[0m".format(str(rgb[0]), str(rgb[1]), str(rgb[2]), text)

# banners = ["https://data.cyber.org.il/OnTopTech/school_bell/images/colab_celebrate_1.gif",
           # "https://data.cyber.org.il/OnTopTech/school_bell/images/colab_celebrate_2.gif",
           # "https://data.cyber.org.il/OnTopTech/school_bell/images/colab_celebrate_3.gif",
           # "https://data.cyber.org.il/OnTopTech/school_bell/images/colab_celebrate_4.gif"]
# greetings=["כל הכבוד! אנחנו שולטיםםםם",
           # "אליפות! סיימנו עוד משימה",
           # "נהדר! זה כבר כמעט הסוף",
           # "כל הכבוד לי! סיימתי עוד שלב",
           # "כל הכבוד לי!"]


def run_banner_rnd():
    """
    Randomly selects a greeting and banner from the provided lists and runs the banner display.

    Steps:
        1. Reads greetings from a text file.
        2. Reads banner GIFs from a source (not specified in the code).
        3. Randomly selects a greeting and a banner.
        4. Calls the `run_banner` function to display the selected greeting and banner.

    Returns:
    ----------          
        None
    """
    greetings = read_greeting_txt()
    banners = read_banner_gifs()
    banner_num = random.randint(0, len(banners)-1)
    greetings_num = random.randint(0, len(greetings)-1)
    run_banner(greetings, banners[banner_num] )

def run_banner_manual(greetings_str):
    """
    Displays a banner with a specific greeting string.

    Parameters: 
    ----------    
        greetings_str (str): The desired greeting message.

    Steps:
        1. Reads banner GIFs from a source (not specified in the code).
        2. Randomly selects a banner.
        3. Calls the `run_banner` function to display the selected banner with the provided greeting.

    Returns:
    ----------   
        None
    """
    banners = read_banner_gifs()
    banner_num = random.randint(0, len(banners)-1)
    run_banner(greetings_str, banners[banner_num] )

#def read_greeting_txt():
#    url = "https://ontopnew.s3.il-central-1.amazonaws.com/library/greetings01.txt"
#    response = urllib.request.urlopen(url)
#    data = response.read().decode("utf-8")  # Decode bytes to string
#    list = []
#    for line in data.splitlines():
#        list.append(line.strip())
#    return list


def read_greeting_txt():
    """
    Reads greetings from a source (not specified in the code) and returns a random greeting.

    Steps:
        1. Retrieves a list of greetings from a source.
        2. Randomly selects a greeting from the list.
        3. Returns the selected greeting.

    Returns:
    ----------   
        str: A randomly selected greeting.
    """
    list = get_banners_strings()
    banner_num = random.randrange(len(list))  # שינוי ל-random.randrange
    return list[banner_num]

def read_banner_gifs():
    """
    Fetches a list of banner GIF URLs from a remote source.

    Parameters: 
    ----------    
        None

    Steps:
        1. Defines the URL pointing to a text file containing banner GIFs.
        2. Opens the URL using `urllib.request.urlopen`.
        3. Reads the response content as bytes.
        4. Decodes the bytes to a UTF-8 string.
        5. Splits the string into lines.
        6. Iterates through each line:
            - Removes leading/trailing whitespace using `strip()`.
            - Appends the cleaned line (assumed to be a banner GIF URL) to a list.
        7. Returns the list of banner GIF URLs.

    Returns:
    ----------   
        list: A list of strings containing banner GIF URLs.
    """
    url = "https://ontopnew.s3.il-central-1.amazonaws.com/library/banners.txt"
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")  # Decode bytes to string
    list = []
    for line in data.splitlines():
        list.append(line.strip())
    return list

def read_gifs():
    """
    Fetches a list of GIF URLs from a remote source.

    Steps:
        1. Defines the URL pointing to a text file containing GIF URLs.
        2. Opens the URL using `urllib.request.urlopen`.
        3. Reads the response content as bytes.
        4. Decodes the bytes to a UTF-8 string.
        5. Splits the string into lines.
        6. Iterates through each line:
            - Removes leading/trailing whitespace using `strip()`.
            - Appends the cleaned line (assumed to be a GIF URL) to a list.
        7. Returns the list of GIF URLs.

    Returns:
    ----------   
        list: A list of strings containing GIF URLs.
    """
    url = "https://ontopnew.s3.il-central-1.amazonaws.com/library/gifs.txt"
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")  # Decode bytes to string
    list = []
    for line in data.splitlines():
        list.append(line.strip())
    return list


def run_banner(greetings_str, banner_link="" ):
    """
    Displays a banner with a greeting and optional background image.

    Parameters: 
    ----------    
        greetings_str (str): The greeting message to display on the banner.
        banner_link (str, optional): The URL of a banner image to display in the background. Defaults to an empty string (no background image).

    Returns:
    ----------   
        None

    Displays an HTML banner with the following elements:
        - Background color (aliceblue)
        - Banner image (if provided) with a gaussian blur filter
        - Greeting text with:
            - Bold font style
            - Blue color (#1F33BE)
            - Centered alignment
            - Two lines:
                - Top line: Provided greeting message
                - Bottom line: Today's date (format: DD.MM.YYYY)
    """
    html = '''
    <svg width='970'  style="background-color:aliceblue">
     <image href={banner} />
     <defs>
      <filter id="f3" x="0" y="0" width="100%" height="100%">
        <feOffset result="offOut" in="SourceAlpha" dx="0" dy="0" />
        <feGaussianBlur result="blurOut" in="offOut" stdDeviation="10" />
        <feBlend in="SourceGraphic" in2="blurOut" mode="normal" />
      </filter>
    </defs>
     <text x="50%" y="80" dominant-baseline="middle" text-anchor="middle" font-size="30" fill="#1F33BE" font-weight="bold" filter="url(#f3)">{*}</text>
     <text x="50%" y="45" dominant-baseline="middle" text-anchor="middle" font-size ="20" fill="#1F33BE"  filter="url(#f3)">{date}</text>
    /svg>
    '''
    today = datetime.date.today()
    html = html.replace("{*}", greetings_str)
    html = html.replace("{date}", str(today.day) + "." +  str(today.month) + "." +  str(today.year))
    html = html.replace("{banner}", banner_link)
    display(HTML(html))
    
def show_gif(gif_url, gif_width=None, gif_height=None):
      """
      Displays a GIF image from the given URL with optional width and height.

      Parameters: 
      ----------    
      gif_url (str): The URL of the GIF image to be displayed.
      gif_width (int, optional): The desired width of the GIF image. If not provided, the image will be displayed at its original width.
      gif_height (int, optional): The desired height of the GIF image. If not provided, the image will be displayed at its original height.

      Returns:
      ----------   
      None

      Displays an HTML image tag with the specified GIF URL and dimensions. If width and height are not provided, the image will be displayed at its original size.
      """
      if gif_width != None and gif_height != None:
          display(Image(url = gif_url, width = int(gif_width), height=int(gif_height)))
      else:
          display(Image(url = gif_url))


def show_image(gif_url):
    """
    Displays an image in the output using HTML.

    This function creates an HTML structure to display an image
    specified by the given URL.

    Parameters:
    ----------
    gif_url : str
        The URL of the image to be displayed.

    Returns:
    -------
    None
        The function doesn't return a value, but displays the image
        in the output using IPython's display function.
    """
    html = '''
    <html>
  <head>
    <title>הצגת תמונה</title>
  </head>
  <body>
    <img src="{image_url}">
  </body>
  </html>
  '''
    html = html.replace("{image_url}", gif_url)
    display(HTML(html))

def play_video_from_to(video_width, video_path, from_time, to_time):
    """
    Displays a video clip within a specified time range.

    This function generates an HTML5 video player that plays a portion of a video
    file, starting and ending at specified times.

    Parameters:
    ----------
    video_width : int
        The width of the video player in pixels.
    video_path : str
        The URL or file path of the video to be played.
    from_time : float
        The start time of the video clip in seconds.
    to_time : float
        The end time of the video clip in seconds.
    Returns:
    -------
    HTML
        An HTML object containing the video player with the specified clip.

    Notes:
    ------
    The function modifies the video_path by appending a time range specifier
    (#t={from},{to}) to control the playback range.
    """
    video_path = video_path+'#t={from},{to}'
    video_path = video_path.replace('{from}', str(from_time))
    video_path = video_path.replace('{to}', str(to_time))
    return HTML(f"""<video width={video_width} controls autoplay><source src="{video_path}"></video>""")



def selfie(timer):
    """
    Captures and displays a selfie after a specified delay.

    This function initiates a video stream, waits for the specified time,
    captures a photo, and then displays it.

    Parameters:
    ----------
    timer : int or float
        The number of seconds to wait before capturing the photo.
        If timer > 0, a score of 6 is set (though not used in the function).

    Returns:
    -------
    None
        The function doesn't return a value, but displays the captured image.

    Note:
    -----
    This function relies on external functions 'show_video()', 'take_photo()',
    and the 'Image' class from an unspecified module (likely PIL or IPython.display).
    """
    if (timer > 0): 
        score = 6
    show_video()
    time.sleep(timer)
    display(Image.open(take_photo()))


def show_video():
  """
  Displays a video stream in a web browser using HTML5 and JavaScript.

  This function creates an HTML5 video element and initializes it with a video stream
  obtained from the user's webcam. The video element is appended to a div element,
  which is then added to the body of the HTML document. The video stream is played
  automatically, and the output is resized to fit the video element.

  Parameters:
  ----------
  None

  Returns:
  -------
  None

  The function does not return a value, but it displays a video stream in the web browser.
  """
  js = Javascript('''
    var stream;
    async function showVideo() {
      const div = document.createElement('div');
      div.id = 'VideoContainer';
      const video = document.createElement('video');
      video.id = 'CaptureVideo';
      video.style.display = 'block';
      stream = await navigator.mediaDevices.getUserMedia({video: true});

      document.body.appendChild(div);
      div.appendChild(video);
      video.srcObject = stream;
      await video.play();

      // Resize the output to fit the video element.
      google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);

      // Wait for Capture to be clicked.
      // await new Promise((resolve) => capture.onclick = resolve);
    }

    function takePhoto(quality) {
      const div = document.getElementById('VideoContainer');
      const video = document.getElementById('CaptureVideo');
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      stream.getVideoTracks()[0].stop();
      div.remove();
      return canvas.toDataURL('image/jpeg', quality);
    }
    ''')
  display(js)
  eval_js('showVideo()')


def download_image_from_web(url):
    """
    Downloads an image from the specified URL and saves it locally.

    Parameters: 
    ----------    
    url : str
        The URL of the image to be downloaded.

    Steps:
        1. Sends a GET request to the specified URL using the requests library.
        2. Calls the save_photo function to save the downloaded image locally.

    Returns:
    ----------   
    None

    The function does not return a value, but it downloads and saves the image.
    """
    response = requests.get(url)
    save_photo(response.content)

def save_photo(binary, filename='photo.jpg'):
  """
  Saves binary image data to a specified file.

  Parameters: 
    ----------    
    binary: Binary data representing the image.
    filename (str, optional): The desired filename for the saved image. Defaults to 'photo.jpg'.

  Returns:
    ----------   
    str: The filename of the saved image.

  This function takes binary image data and writes it to a file. It opens the specified filename in write-binary mode ('wb') and writes the binary data to the file. 
  """
  with open(filename, 'wb') as f:
    f.write(binary)
  return filename


def take_photo(filename='photo.jpg', quality=0.8):
    """
    This function captures a photo from a webcam and saves it as a JPEG file.

    Parameters:
    ----------
    filename : str, optional
        The name of the file where the photo will be saved.
        Default is 'photo.jpg'.
    quality : float, optional
        The quality of the JPEG image. A value of 0.8 means an 80% quality image.
        Default is 0.8.

    Returns:
    -------
    str
        The name of the file where the photo was saved.

    The function uses JavaScript to capture a photo from the webcam,
    encodes the photo as a base64 string, decodes the base64 string,
    and saves the photo as a JPEG file.
    """
    data = eval_js('takePhoto({})'.format(quality))
    binary = b64decode(data.split(',')[1])
    return save_photo(binary, filename)

def convert_img_to_base64(url):
    """
    Converts an image file located at the specified URL to a base64 encoded string.

    Parameters:
    ----------
    url : str
        The URL of the image file to be converted.

    Returns:
    -------
    str
        The base64 encoded string representation of the image file.

    The function reads the image file from the specified URL, opens it in binary mode,
    reads the file data, encodes the data as a base64 string, and returns the encoded string.
    """
    with open('/content/photo.jpg', 'rb') as f:
        image_data = f.read()
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    return encoded_image


def is_file_exist(file_name):
    """
    Checks if a file exists at the specified path.

    Parameters:
    ----------
    file_name : str
        The path to the file to be checked.

    Returns:
    -------
    bool
        True if the file exists, False otherwise.
    """
    if os.path.exists(file_name):
        return True
    else:
        return False
    
    
    
#*** TRIVIA
def trivia_run_banner_rnd():
    """
    This function randomly selects a greeting and a banner from the provided lists,
    and runs the banner display.

    Parameters:
    ----------
    None

    Steps:
        1. Calls the `trivia_read_greeting_txt` function to retrieve a random greeting.
        2. Calls the `read_banner_gifs` function to retrieve a list of banner GIF URLs.
        3. Randomly selects a banner from the list.
        4. Calls the `run_banner` function to display the selected greeting and banner.

    Returns:
    -------
    None
    """
    greetings = trivia_read_greeting_txt()
    banners = read_banner_gifs()
    banner_num = random.randint(0, len(banners)-1)
    greetings_num = random.randint(0, len(greetings)-1)
    run_banner(greetings, banners[banner_num] )



def trivia_read_greeting_txt():
    """
    Retrieves a random greeting from a predefined list of trivia greetings.

    Parameters:
    ----------
    None

    Returns:
    -------
    str
        A randomly selected greeting from the predefined list of trivia greetings.

    The function uses the `get_banners_strings` function to retrieve a list of trivia greetings.
    It then selects a random greeting from the list using the `random.randrange` function.
    Finally, it returns the selected greeting.
    """
    list = get_banners_strings("trivia_banner")
    banner_num = random.randrange(len(list))  # שינוי ל-random.randrange
    return list[banner_num]