from media import *
from html_helper import *
from messages import *
from string_table import *
import sys

import datetime
'''banners = ["https://data.cyber.org.il/OnTop/GifBanner/colab_celebrate_1.gif",
           "https://data.cyber.org.il/OnTop/GifBanner/colab_celebrate_2.gif",
           "https://data.cyber.org.il/OnTop/GifBanner/colab_celebrate_3.gif",
           "https://data.cyber.org.il/OnTop/GifBanner/colab_celebrate_4.gif"]
greetings=["יש! סיימתי שלב",
           "איזה כיף, סיימתי את השלב",
           "כל הכבוד לי! ניסיתי והצלחתי",
           "!סיימתי את פיצ'ר 1",
           "!סיימתי עוד פיצ'ר",
           "ישששששששששששש"]'''


class Answer:
  text = ""
  correct_answer = False
class Question:
  text=""
  answers = []


questions = []
#score=0
question_index=0

# html's
intro_html = ""
question_html=""
authors_html=""


def run_me(greetings_num=-1):
    """
    This function runs the trivia game by displaying a random banner.

    Parameters:
    greetings_num (int, optional): The index of the greeting message to display. Defaults to -1, which means no specific greeting message will be displayed.

    Returns:
    None
    """
    trivia_run_banner_rnd()

def new_game():
    """
    This function initializes a new game by resetting the game state and loading the introductory HTML content.

    Parameters:
    None

    Returns:
    None

    Global Variables Modified:
    - question_index: Set to 0 to start the game from the first question.
    - authors_html: Set to an empty string to clear the list of authors.
    - html: Loaded with the content of the introductory HTML file.
    """
    #global score
    global question_index
    global html
    global authors_html
    #score=0
    question_index=0
    authors_html=""
    url = 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/intro.html'
    response = requests.get(url)
    html = response.text

def add_programmer(name, avatar):
    """
    This function adds a programmer's name and avatar to the list of authors for the trivia game.

    Parameters:
    name (str): The name of the programmer.
    avatar (int): The avatar number of the programmer.

    Returns:
    None

    Global Variables Modified:
    - intro_html: The global variable used to store the introductory HTML content.
    - authors_html: The global variable used to store the HTML content for the list of authors.
    """
    global intro_html
    global authors_html
    author_html = '''
    <div style="display:inline-block;margin-left:10px;margin:35px">
    <img src="*emoji*" height="100px" width="100px">
    <div >
    <span style="color:#1F33BE; font-size:25px; font-family:Calibri; font-weight: bold">*name*</span></div>
    </div>
    '''
    author_html = author_html.replace("*emoji*","https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/Emoji/trivia_avatar_"
                                        + str(avatar) + ".png")
    author_html = author_html.replace("*name*",name);
    authors_html = authors_html + author_html

def print_intro(title, description):
    """
    Prints an introduction screen with a given title, authors, and description.

    Parameters:
    title (str): The title of the introduction screen.
    description (str): The description of the introduction screen.

    Returns:
    None
    """
    #global html
    global authors_html
    url = ''
    if get_language() == 'hebrew':
        url = "https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/intro_template_07.html"
    else:
        url = "https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/intro_template_07%20arabic%20.html"  
    response = requests.get(url)
    intro_html = response.text
    #print(intro_html)
    intro_html = intro_html.replace("*title*", title);
    intro_html = intro_html.replace("*authors*", authors_html);
    #intro_html = intro_html.replace("*intro*", intro);
    intro_html = intro_html.replace("*description*", description);
    #print("*************",intro_html,"*****************")
    display(HTML(intro_html))
    #input("")
    url = 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/trivia_start_game.gif'
    s = get_string_from_string_table("trivia","yalla_start")
    start_html = '''
    <div style="width:700px; height:auto; margin-top:30px; margin-bottom:30px">
    <div style="display: flex;text-align:center; justify-content: center;  align-items: center; background-color:white; width:700px; height:280px">
    <img src="https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/trivia_start_game.gif" alt="Computer man" style="width:480px;height:auto;"/>
    </div>
    <div>
    <center style="color:#1F33BE; font-size:22px; font-family:Calibri; font-weight: bold; margin-top:15px">*yalla*</center>
    </div>
    </div>
    '''
    start_html = start_html.replace("*yalla*",s)
    display(HTML(start_html))
    input("")

def read_questions(file_name):
    """
    This function reads a trivia questions file and populates the global list of questions.

    Parameters:
    file_name (str): The name of the trivia questions file. The file should be located in the "/content/" directory.

    Returns:
    None

    Global Variables Modified:
    - questions (list): The global list of questions is populated with the questions read from the file.

    Raises:
    FileNotFoundError: If the specified file is not found in the "/content/" directory.
    """
    global questions
    new_game() # Clear the previous questions global var and reset the game

    questions = []
    text_file = "/content/" + file_name  #build the full path of trivia questions and answers file
    try:
        file1 = open(text_file, "r") #Open the file for reading
    except (FileNotFoundError):
        s = get_string_from_string_table('trivia', 'file_msg') # Returns a language dependent error message - Hebrew or Arabic
        error_msg("read_questions", s + file_name) #Display the error message
        #sys.exit() # Exit the program
        #sys.exit("Stopping execution")
        raise FileNotFoundError(s + file_name)
    
    lines = file1.readlines() # Read all lines from the trivia file

    question = None

    for line in lines:
        if "***" in line: # If the line starts with "***", it indicates the start of a new question
            question = Question() # Create a new Question object
            question.text = line.replace("***", "") # Remove the "***" from the question text
            question.answers = []  # Initialize the list of answers for the question
            questions.append(question) # Add the question to the global list of questions
            first = True # Set the flag to indicate that the first answer has not been encountered yet
        else:
            answer = Answer() # Create a new Answer object
            answer.text = line
            if first == True: # if correct answer
                answer.correct_answer = True
            else:
                answer.correct_answer = False
            first = False
            question.answers.append(answer)

    check_file() # Validate the questions file after reading all questions
  #return questions

def shuffle_trivia():
    """
    Shuffles the global list of questions and their answers.

    Parameters:
    None

    Returns:
    None

    Global Variables Modified:
    - questions (list): The global list of questions is shuffled. Each question's answers are also shuffled.
    """
    global questions
    random.shuffle(questions)
    for q in questions:
        random.shuffle(q.answers)
  #return questions


#def print_trivia(trivia):
#  for q in trivia:
#    print(q.text)
#    for a in q.answers:
#      print(a.text , " - " , a.correct_answer)



def display_question(index):
    """
    Displays a trivia question in an HTML format.

    Parameters:
    index (int): The index of the question to display. If the index is less than or equal to 0, it is set to a large number to display the first question.

    Returns:
    None

    Raises:
    IndexError: If the index is out of range (i.e., greater than the number of questions).

    Global Variables Used:
    - questions (list): A list of Question objects containing the trivia questions.

    Local Variables Used:
    - url (str): The URL of the HTML template for displaying the question.
    - response (requests.Response): The response object containing the HTML template.
    - html (str): The HTML content of the question template.
    - q (Question): The question object to be displayed.
    """
    '''global language
    global questions
    global question_index'''

    #print("language=",language)
    #print("language=",get_language())
    
    if get_language() == 'hebrew':
        url = 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/question_template_16.html'
    else:
        url = 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/question_template_16%20arabic.html'
    response = requests.get(url)
    html = response.text
    try:
        if index <= 0:
            index = 10000000
        q = questions[index - 1]
        html = html.replace("*num*", str(index) + " | ")
        html = html.replace("*question*", q.text)
        html = html.replace("*answer1*", "<b>1.&nbsp; </b>" + q.answers[0].text)
        html = html.replace("*answer2*", "<b>2.&nbsp; </b>" + q.answers[1].text)
        html = html.replace("*answer3*", "<b>3.&nbsp; </b>" + q.answers[2].text)
        html = html.replace("*answer4*", "<b>4.&nbsp; </b>" + q.answers[3].text)
        html = html.replace("*tmp*", "")
        display(HTML(html))
    except IndexError:
        error_msg("display_question", "Index is out of range.")

def wrong_answer_msg():
    """
    Displays a message and an animated GIF to indicate a wrong answer.

    Parameters:
    None

    Returns:
    None

    Local Variables:
    - url (str): The URL of the animated GIF.
    - html_gif (str): The HTML string to display the message and the GIF.
    - s (str): The translated string for the wrong answer message.

    Global Variables Used:
    - language (str): The current language setting.

    External Libraries Used:
    - requests (requests): To make HTTP requests.
    - random (random): To generate random numbers.
    - HTML (IPython.display.HTML): To display HTML content.
    - get_string_from_string_table (function): To retrieve translated strings.
    """
    url = 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/AnswersGif/trivia_wrong_answer_' + str(random.randint(1,4)) + '.gif'
    html_gif='''
    <div >
    <div style="display: flex;text-align:center; justify-content: center;   background-color:'white';width:700px; height:auto">
     <span style=" direction:rtl; color:#1F33BE; font-size:22px; font-family:Calibri;margin-top:50px">*msg*</span>
     <img src="*url*" alt="Computer man" style="width:75px;height:75px;margin-top:30px;">
    <div>
    <div>
    '''
    html_gif = html_gif.replace("*url*", url)
    s=get_string_from_string_table('trivia','wrong_answer')
    html_gif = html_gif.replace("*msg*", s)
    display(HTML(html_gif))

def correct_answer_msg():
  url = 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/AnswersGif/trivia_correct_answer_' + str(random.randint(1,4)) + '.gif'
  #print(url)
  html_gif='''
<div >
<div style="display: flex;text-align:center; justify-content: center;   background-color:'white';width:700px; height:auto">
 <span style=" direction:rtl; color:#1F33BE; font-size:22px; font-family:Calibri;margin-top:50px">*msg*</span>
 <img src="*url*" alt="Computer man" style="width:75px;height:75px;margin-top:30px;">
<div>
<div>
  '''
  html_gif = html_gif.replace("*url*", url)
  s=get_string_from_string_table('trivia','correct_answer')
  html_gif = html_gif.replace("*msg*", s)
  display(HTML(html_gif))

def print_result():
    """
    Prints a result screen displaying a random animated GIF from a specific URL.

    Parameters:
    None

    Returns:
    None

    Local Variables:
    - url (str): The URL of the animated GIF.
    - response (requests.Response): The response object containing the GIF.
    - html (str): The HTML content of the GIF.

    External Libraries Used:
    - requests (requests): To make HTTP requests.
    - HTML (IPython.display.HTML): To display HTML content.
    """
    url = 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/AnswersGif/trivia_wrong_answer_' + str(random.randint(1,4)) + '.gif'
    response = requests.get(url)
    html = response.text
    display(HTML(html))


def print_win(score):
    """
    Prints a winning screen with the given score and the total number of questions.

    Parameters:
    score (int): The score achieved by the player.

    Returns:
    None

    Local Variables:
    url (str): The URL of the HTML template for displaying the game result.
    response (requests.Response): The response object containing the HTML template.
    html (str): The HTML content of the game result template.
    s (str): The translated string for the result title.
    s1 (str): The translated string for the first part of the result message.
    s2 (str): The translated string for the second part of the result message.
    s3 (str): The translated string for the third part of the result message.

    Steps:

    """
    url = 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/game_result14.html'
    response = requests.get(url)
    html = response.text
    html = html.replace("*img*", 'https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/AnswersGif/trivia_win_game.gif')
    s = get_string_from_string_table('trivia','result') 
    html = html.replace("*title*", s)
    s1 = get_string_from_string_table('trivia','general_3') 
    s2 = get_string_from_string_table('trivia','general_2') 
    s3 = get_string_from_string_table('trivia','general_1') 
    s = s1 + " *n1* " + s2 + " *n2* " + s3
    html = html.replace("*result*", s)
    html = html.replace("*n1*", str(score))
    html = html.replace("*n2*", str(get_number_of_questions()))
    display(HTML(html))


def print_lose(score):
    """
    Prints a losing screen with the given score and the total number of questions.

    Parameters:
    score (int): The score achieved by the player.

    Returns:
    None

    Local Variables:
    url (str): The URL of the HTML template for displaying the game result.
    response (requests.Response): The response object containing the HTML template.
    html (str): The HTML content of the game result template.
    s (str): The translated string for the result title.
    s1 (str): The translated string for the first part of the result message.
    s2 (str): The translated string for the second part of the result message.
    s3 (str): The translated string for the third part of the result message.

    Steps:
    - Fetch the HTML template from the specified URL.
    - Replace the placeholders in the HTML template with the appropriate values.
    - Display the HTML content using the IPython.display.HTML function.
    """
    url = "https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/game_result14.html"
    response = requests.get(url)
    html = response.text

    html = html.replace("*img*", "https://ontopnew.s3.il-central-1.amazonaws.com/Trivia/AnswersGif/trivia_lose_game_1.gif")
    s = get_string_from_string_table('trivia','result') 
    html = html.replace("*title*", s)
    s1 = get_string_from_string_table('trivia','general_3') 
    s2 = get_string_from_string_table('trivia','general_2') 
    s3 = get_string_from_string_table('trivia','general_1') 
    s = s1 + "&nbsp;*n1*&nbsp;" + s2 + "&nbsp;*n2*&nbsp;" + s3
    html = html.replace("*result*", s)
    html = html.replace("*n1*", str(score))
    html = html.replace("*n2*", str(get_number_of_questions()))
    display(HTML(html))

# shany fix 28.2.23: worked on global (questions) and not on the parameter (trivia), now fixed
def get_number_of_questions():
    """
    This function returns the total number of questions in the trivia game.

    Parameters:
    None

    Returns:
    int: The total number of questions in the trivia game.
    """
    #global questions
    #return len(questions)
    return len(questions)

def check_answer(quest_num, answer):
    """
    This function checks if the given answer is correct for the specified question number.

    Parameters:
    quest_num (int): The number of the question to check. The question number is 1-indexed.
    answer (int): The number of the answer to check. The answer number is 1-indexed.

    Returns:
    bool: True if the given answer is correct for the specified question number, False otherwise.
    """
    return questions[quest_num - 1].answers[answer - 1].correct_answer


def get_correct_answer(quest_num):
    """
    This function returns the number of the correct answer for a given question number.

    Parameters:
    quest_num (int): The number of the question to check. The question number is 1-indexed.

    Returns:
    int: The number of the correct answer for the specified question number. If no correct answer is found, the function returns None.
    """
    i = 0
    for answer in questions[quest_num - 1].answers:
        i += 1
        if answer.correct_answer:
            return i
    return None

# def input_answer():
  # answer = 0
  # while answer>4 or answer<1:
    # s = get_string_from_string_table('trivia','correct_answer1-4')   
    # print(s)
    # answer = int(input(""))
  # return answer

# def input_number(msg=''):
  # num = input(msg)
  # if num.isnumeric():
    # return int(num)
  # else:
    # return num

def check_file():
    """
    This function checks the validity of the trivia questions file.

    Parameters:
    None

    Returns:
    None

    Steps:
    1. Print the total number of questions in the file.
    2. Iterate through each question in the file.
    3. Check if the number of answers for each question is equal to 4.
    4. If the number of answers is not equal to 4, set the 'valid' flag to False.
    5. If the 'valid' flag is True, print a success message.
    6. If the 'valid' flag is False, print an error message and exit the program.
    """
    s1 = get_string_from_string_table('trivia','genetal_4') 
    s2 = get_string_from_string_table('trivia','general_1') 
    print(s1,len(questions), s2)
    valid = True
    for q in questions:
        if len(q.answers) != 4:
            valid = False
    if(valid):
        s = get_string_from_string_table('trivia','file_ok')    
        print(s)
    else:
        s = get_string_from_string_table('trivia','file_error')    
        error_msg("read_questions", s)
        sys.exit()
