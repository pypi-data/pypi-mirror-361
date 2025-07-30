from media import *
from html_helper import *
from messages import *
from string_table import *

'''
This variable is used to store the name of the student. 
It is initially set to an empty string.
'''
student_name=''
'''
This variable is used to store the name of the school that the student belongs to. 
It is initially set to an empty string.
'''
student_school = ''
'''
This variable is used to keep track of the progress or score of the student in the program. 
It is initially set to 0. 
The score is incremented as the student completes specific tasks or exercises within the program. 
The score is used to control the flow of the program and to provide feedback to the student
'''
score = 0


def run_me():
    """
    This function is responsible for running the main banner of the program.

    Parameters:
    None

    Returns:
    None
    """
    run_banner_rnd()


name=""
school=""

def print_who_rules(text):
    """
    This function prints a message to the console based on the current score.
    If the score is less than 1, it retrieves a error string from a string table,
    prints it in a red background with white text, and does not perform any further action.
    If the score is 1, it prints the provided text followed by a newline character,
    and then calls the `validate_ex2` function with the provided text.

    Parameters:
    text (str): The text to be printed if the score is 1 or more.

    Returns:
    None
    """
    global score
    if score < 1:
        s = get_string_from_string_table('school_bell', 'print_who_rules')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
    else:
        print(text, "\n")
        validate_ex2(text)


def print_image(w, h):
    """
    This function prints an image to the console based on the current score.
    If the score is less than 2, it retrieves an error string from a string table,
    prints it in a red background with white text, and does not perform any further action.
    If the score is 2 or more, it generates an HTML string to display an image,
    replaces the width and height placeholders with the provided values,
    and displays the image using the IPython display function.
    Finally, if the score is 2, it increments the score by 1.

    Parameters:
    w (int): The width of the image.
    h (int): The height of the image.

    Returns:
    None
    """
    global score
    if score < 2:
        s = get_string_from_string_table('school_bell', 'print_image_2')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
        return
    html = '''
    <img src='https://ontopnew.s3.il-central-1.amazonaws.com/Riddle1.jpg' alt="password" width="*w*" height="*h*">
    '''
    html = html.replace("*w*", str(w))
    html = html.replace("*h*", str(h))
    display(HTML(html))
    if score == 2:
        score = 3  # score + 1

def print_password(text):
    """
    This function prints a password to the console based on the current score.
    If the score is less than 3, it retrieves an error string from a string table,
    prints it in a red background with white text, and does not perform any further action.
    If the score is 3 or more, it prints the provided text followed by a newline character,
    and then calls the `validate_ex4` function with the provided text.

    Parameters:
    text (str): The password to be printed if the score is 3 or more.

    Returns:
    None
    """
    global score
    if score < 3:
        s = get_string_from_string_table('school_bell', 'print_image_3')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
    else:
        print(text, "\n")
        validate_ex4(text)



def play_video(start, end):
    """
    Plays a video from a specific start to end time based on the current score and language settings.

    Parameters:
    start (int): The start time of the video in seconds.
    end (int): The end time of the video in seconds.

    Returns:
    None if the score is less than 4. Otherwise, it returns the result of the `play_video_from_to` function.
    """
    global score
    language = get_language()

    if score < 4:
        s = get_string_from_string_table('school_bell', 'play_video')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
        return

    else:
        if language == 'hebrew':
            if ((start >= 5 and start <= 7) ) and (end >= 42 and end <= 45):
                if score == 4:
                    score = 5
        else: # Arabic
            if ((start >= 5 and start <= 7) ) and (end >= 29 and end <= 31):
                if score == 4:
                    score = 5

    video_width = 700
    if language == 'hebrew':
        video_path = 'https://ontopnew.s3.il-central-1.amazonaws.com/school_bell/video/bell.mp4'
    else: # Arabic
        video_path = 'https://ontopnew.s3.il-central-1.amazonaws.com/school_bell/video/bell_arabic.mp4'

    return play_video_from_to(video_width, video_path, start, end)

def take_selfie(timer):
    """
    This function takes a selfie with a timer and updates the score if the timer is greater than 0.

    Parameters:
    timer (int): The timer value for taking the selfie. If the timer is greater than 0, the score is updated to 6.

    Returns:
    None if the score is less than 5. Otherwise, it calls the `selfie` function with the provided timer value.
    """
    global score

    if score < 5:
        s = get_string_from_string_table('school_bell', 'take_selfie')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
        return

    if (timer > 0):
        score = 6
    selfie(timer);


def download_pic(link):
    """
    Downloads an image from the provided link and displays it.

    Parameters:
    link (str): The URL of the image to be downloaded.

    Returns:
    None if the score is less than 5. Otherwise, it downloads the image from the provided link,
    updates the score to 6, and displays the image using the IPython display function.
    """
    global score

    if score < 5:
        s = get_string_from_string_table('school_bell', 'download_pic')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
        return

    score = 6
    download_image_from_web(link)
    #display(Image.open('photo.jpg'))
    display(Image('photo.jpg'))



def add_greetings():
    """
    This function generates a personalized greeting certificate HTML string by replacing placeholders with actual data.

    Parameters:
    None

    Returns:
    str: The HTML string representing the personalized greeting certificate.
    """
    global student_name, student_school
    html = download_html('https://ontopnew.s3.il-central-1.amazonaws.com/school_bell/HTML/Certificate08.html')
    s = get_string_from_string_table('school_bell', 'add_greetings_1')
    html = html.replace('{*name*}', s + student_name)

    # Convert image to base64
    if is_file_exist('/content/photo.jpg'):
        encoded_image = convert_img_to_base64('/content/photo.jpg')
        html_img_tag = '<img src="data:image/jpeg;base64,' + encoded_image + '" alt="Image description" width="593" height="444"/>'
    else:
        s = get_string_from_string_table('school_bell', 'add_greetings_2')
        error_msg(s)
    html = html.replace('{*image*}', html_img_tag)

    s3 = get_string_from_string_table('school_bell', 'add_greetings_3')
    s4 = get_string_from_string_table('school_bell', 'add_greetings_4')
    html = html.replace('{*school*}', s3 + student_school + s4)

    s5 = get_string_from_string_table('school_bell', 'add_greetings_5')
    html = html.replace('{*content*}', s5)

    return html

def make_certificate():
    """
    This function generates and displays a personalized greeting certificate.

    The function checks the current score. If the score is greater than 5, it calls the `add_greetings` function to generate the HTML string representing the certificate.
    The generated HTML string is then displayed using the IPython display function.

    If the score is not greater than 5, it retrieves an error message from a string table,
    prints it in a red background with white text, and does not perform any further action.

    Parameters:
    None

    Returns:
    None
    """
    global score
    if score > 5:
        display(HTML(add_greetings()))
    else:
        s = get_string_from_string_table('school_bell', 'make_certificate')
        print(print_background(print_color(s, colors.WHITE), colors.RED))



def get_score():
    """
    This function retrieves the current score of the program.

    Parameters:
    None

    Returns:
    int: The current score of the program. The score is a global variable that is updated throughout the program based on the student's progress.
    """
    global score
    return score




def validate_ex1(name, school):
    """
    Validates the input name and school for the program.

    This function checks if the provided name and school are not empty.
    If either of them is empty, it prints an error message in red background with white text.
    If both name and school are provided, it updates the global variables `student_name` and `student_school` with the provided values.
    It also updates the global score variable based on the current score.

    Parameters:
    name (str): The name of the student.
    school (str): The name of the school the student belongs to.

    Returns:
    None
    """
    global score
    global student_name
    global student_school
    if name == "" or school == "":
        if score == 1:
            score = 0  # Shany: lower the score only if students play with current section...
        s = get_string_from_string_table('school_bell', 'validate_ex1_1')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
    else:
        student_name = name
        student_school = school
        if score == 0:
            score = 1
        s = get_string_from_string_table('school_bell', 'validate_ex1_2')
        print(print_background(print_color(s, colors.WHITE), colors.GREEN))


def validate_ex2(text):
    """
    Validates the input text based on specific conditions and updates the global score.

    Parameters:
    text (str): The input text to be validated.

    Returns:
    None. The function prints messages based on the validation results and updates the global score.
    """
    global score
    if text == "OnTop Rules":
        if score == 1:
            score = 2
        s = get_string_from_string_table('school_bell', 'validate_ex2_1')
        print(print_background(print_color(s, colors.WHITE), colors.GREEN))
    # check for spaces
    elif text.strip() != text:
        if score == 2:
            score = 1  # Shany: lower the score only if students play with current section...
        s = get_string_from_string_table('school_bell', 'validate_ex2_2')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
    elif text.lower() == "ontop rules":
        if score == 2:
            score = 1  # Shany: lower the score only if students play with current section...
        s = get_string_from_string_table('school_bell', 'validate_ex2_3')
        print(print_background(print_color(s, colors.WHITE), colors.RED))
    elif text.lower() == "ontop":
        if score == 2:
            score = 1  # Shany: lower the score only if students play with current section...
        s = get_string_from_string_table('school_bell', 'validate_ex2_4')
        print(print_background(print_color(2, colors.WHITE), colors.RED))
    else:
        if score == 2:
            score = 1  # Shany: lower the score only if students play with current section...
        s = get_string_from_string_table('school_bell', 'validate_ex2_5')
        print(print_background(print_color(s, colors.WHITE), colors.RED))


# ex3 - print image
#def validate_ex3(text):
#  global result_list
#  global score

#ex4 - print password
def validate_ex4(text):
    """
    Validates the input text for the password and updates the global score.

    Parameters:
    text (str): The input text to be validated. It should match the password "We are the best".

    Returns:
    None. The function prints messages based on the validation results and updates the global score.
    If the input text matches the password, it increments the score to 4 and prints a success message in green.
    If the input text does not match the password, it decrements the score to 3 and prints an error message in red.
    """
    global score
    if text == "We are the best":
        if score == 3:
            score = 4
        s = get_string_from_string_table('school_bell', 'validate_ex4_1')
        print(print_background(print_color(s, colors.WHITE), colors.GREEN))
    else:
        if score == 4:
            score = 3  # Shany: lower the score only if students play with current section...
        s = get_string_from_string_table('school_bell', 'validate_ex4_2')
        print(print_background(print_color(s, colors.WHITE), colors.RED))