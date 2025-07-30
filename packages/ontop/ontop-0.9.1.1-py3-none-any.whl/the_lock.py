from media import *
from html_helper import *
from messages import *
from string_table import *

from io import StringIO
import os
from IPython.display import HTML
from base64 import b64encode

html_close = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_01_closet.png">
</body>
</html>'''
html_open_1 = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_02_safe.png"">
</body>
</html>'''
html_open_1_ar = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_02_safe_ara.png" ">
</body>
</html>'''
html_open_2 = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_03_candies.png" >
</body>
</html>'''
html_open_2_ar = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_03_candies_ara.png">
</body>
</html>'''
html_bag = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_bonus_bag.png">
</body>
</html>'''
html_hat = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_bonus_hat.png">
</body>
</html>'''
html_medal = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_bonus_medal.png">
</body>
</html>'''
html_vacation = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_bonus_vacation.png">
</body>
</html>'''
html_vacation_ar = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_bonus_vacation_ara.png">
</body>
</html>'''
html_top = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/lock_bonus_top.png" >
</body>
</html>'''
html_fireworks = '''
<html>
<body>
<img src="https://ontopnew.s3.il-central-1.amazonaws.com/TheLock/fireworks.gif" width="587" height="263">
</body>
</html>'''


#The result_list initialization uses False values for all elements, but the index-based checks in the unlock function assume a 1-based index.
result_list = [False, False, False, False, False, False, False, False, False, False, False, False]
score = 0


def unlock(index, result):
  """
  Handles the unlocking logic for a series of lock challenges based on the provided index and result.
  This function checks if the provided index and result correspond to the correct answer for a specific challenge.
  It updates the global score and result_list accordingly, provides feedback messages, and triggers UI updates.
  Parameters:
    index (int): The index of the current lock challenge (should be between 1 and 11 inclusive).
    result (int): The user's answer to the current challenge.
  Returns:
    str: A message string from the string table if the index is invalid, otherwise None.
  Side Effects:
    - Modifies the global variables `score` and `result_list`.
    - Calls functions to print or display messages and update the UI.
    - Provides feedback to the user based on their answer and current score.
  Notes:
    - Each index corresponds to a specific challenge with a unique correct answer.
    - The function enforces sequential progression by requiring the score to match the expected value for each index.
    - Uses external functions such as `get_string_from_string_table`, `html_print`, `correct_answer_msg`, and `new_display_visual_result`.
  """
  global result_list
  global score
  #print('index = ', index, ', score = ', score)
  message = ""
  if index < 1 or index > 11:
     s = get_string_from_string_table('the_lock', 'msg16')
     return s

  if index == 1:
    if score != 0:
      s = get_string_from_string_table('the_lock', 'msg18')
      html_print(s)
    else:
      if result == 67:
        if result_list[index] == False:
          score += 1
        result_list[index] = True
        s = get_string_from_string_table('the_lock', 'msg3')
        html_print(s)
        correct_answer_msg(score)
        new_display_visual_result()
      else:
        s = get_string_from_string_table('the_lock', 'msg17')
        html_print(s)#("תשובה לא נכונה, נסו לתקן את הקוד")

  if index == 2:
    if score != 1:
      s = get_string_from_string_table('the_lock', 'msg18')
      html_print(s)
    else:
      if result == 340:
        if result_list[index] == False:
          score += 1
        result_list[index] = True
        s = get_string_from_string_table('the_lock', 'msg3')
        html_print(s)
        correct_answer_msg(score)
        new_display_visual_result()
      else:
        s = get_string_from_string_table('the_lock', 'msg17')
        html_print(s)

  if index == 3:
    if score != 2:
      s = get_string_from_string_table('the_lock', 'msg18')
      html_print(s)
    else:
      if result == 995:
        if result_list[index] == False:
          score += 1
        result_list[index] = True
        s = get_string_from_string_table('the_lock', 'msg3')
        html_print(s)
        correct_answer_msg(score)
        new_display_visual_result()
      else:
        s = get_string_from_string_table('the_lock', 'msg17')
        html_print(s)

  if index == 4:
    if score != 3:
        s = get_string_from_string_table('the_lock', 'msg18')
        print(s)
    else:
      if result == 4950:

        if result_list[index] == False:
          score += 1
        result_list[index] = True
        s = get_string_from_string_table('the_lock', 'msg4')
        html_print(s)
        correct_answer_msg(score)
        new_display_visual_result()
      else:
        s = get_string_from_string_table('the_lock', 'msg17')
        html_print(s)

  if index == 5:
    if score != 4:
      s = get_string_from_string_table('the_lock', 'msg18')
      html_print(s)
    else:
      if result == 2304:
        if result_list[index] == False:
          score += 1
        result_list[index] = True
        s = get_string_from_string_table('the_lock', 'msg5')
        html_print(s)
        correct_answer_msg(score)
        new_display_visual_result()
      else:
        s = get_string_from_string_table('the_lock', 'msg17')
        html_print(s)

  if index == 6:
    if score != 5:
      s = get_string_from_string_table('the_lock', 'msg18')
      html_print(s)
    else:
      if result == 19:
        if result_list[index] == False:
          score += 1
        result_list[index] = True
        s = get_string_from_string_table('the_lock', 'msg19')
        html_print(s)#("מי גאון/נה של אמא?")
        correct_answer_msg(score)
        new_display_visual_result()
      else:
        s = get_string_from_string_table('the_lock', 'msg17')
        html_print(s)#("תשובה לא נכונה, נסו לתקן את הקוד")

  if index == 7:
    if score != 6:
      s = get_string_from_string_table('the_lock', 'msg18')
      html_print(s)
    else:
      if result == 118098:
        if result_list[index] == False:
          score += 1
        result_list[index] = True
        s = get_string_from_string_table('the_lock', 'msg6')
        html_print(s)
        #correct_answer_msg(score)
        new_display_visual_result()
      else:
        s = get_string_from_string_table('the_lock', 'msg17')
        html_print(s)

  if index == 8:
    if score != 7:
      s = get_string_from_string_table('the_lock', 'msg18')
      html_print(s)
    else:
      if result == 100:
        if result_list[index] == False:
          score += 1
        result_list[index] = True
        s = get_string_from_string_table('the_lock', 'msg7')
        html_print(s)
        #correct_answer_msg(score)
        new_display_visual_result()
      else:
        s = get_string_from_string_table('the_lock', 'msg17')
        html_print(s)
  if index == 9:
    if score != 8:
        s = get_string_from_string_table('the_lock', 'msg18')
        html_print(s)
    else:
      if result == 1683:
          if result_list[index] == False:
            score += 1
          result_list[index] = True
          s = get_string_from_string_table('the_lock', 'msg8')
          html_print(s)
          #correct_answer_msg(score)
          new_display_visual_result()
      else:
          s = get_string_from_string_table('the_lock', 'msg17')
          html_print(s)
  if index == 10:
      if score != 9:
        s = get_string_from_string_table('the_lock', 'msg18')
        html_print(s)
      else:
        if result == 7:
          if result_list[index] == False:
            score += 1
          result_list[index] = True
          s = get_string_from_string_table('the_lock', 'msg9')
          html_print(s)
          #correct_answer_msg(score)
          new_display_visual_result()
        else:
          s = get_string_from_string_table('the_lock', 'msg17')
          html_print(s)
  if index == 11:
      if score != 10:
        s = get_string_from_string_table('the_lock', 'msg18')
        html_print(s)
      else:
        if result == 225:
          if result_list[index] == False:
            score += 1
          result_list[index] = True
          s = get_string_from_string_table('the_lock', 'msg10')
          html_print(s)
          #correct_answer_msg(score)
          new_display_visual_result()

        else:
          s = get_string_from_string_table('the_lock', 'msg17')
          html_print(s)




def new_display_visual_result():
  """
  Displays a visual result based on the user's score and language preference.

  The function selects and displays different HTML visual elements depending on the value of the global variable `score` (ranging from 1 to 11) and the user's language, as determined by `get_language()`. For certain scores, the displayed HTML varies between Hebrew and other languages. The function uses the `display` and `HTML` functions to render the appropriate visual feedback.

  Returns:
    None
  """
  language = get_language()
  if score == 1 or score == 2 or score == 3:
    display(HTML(html_close))
  elif score == 4 or score == 5:
    if language == 'hebrew':
      display(HTML(html_open_1))
    else:
      display(HTML(html_open_1_ar))
  elif score == 6 :
    if language == 'hebrew':
      display(HTML(html_open_2))
    else:
      display(HTML(html_open_2_ar))
  elif score == 7 :
    #if language == 'hebrew':
      display(HTML(html_hat))
    #else:
    #  display(HTML(html_open_2_ar))
  elif score == 8 :
    #if language == 'hebrew':
      display(HTML(html_bag))
    #else:
    #  display(HTML(html_open_2_ar))
  elif score == 9 :
    #if language == 'hebrew':
      display(HTML(html_medal))
    #else:
    #  display(HTML(html_open_2_ar))
  elif score == 10 :
    if language == 'hebrew':
      display(HTML(html_vacation))
    else:
      display(HTML(html_vacation_ar))
  elif score == 11 :
    #if language == 'hebrew':
      display(HTML(html_top))
    #else:
    #  display(HTML(html_open_2_ar))

#  else:
#    display(HTML(html_fireworks))


def correct_answer_msg(score):
  """
  Displays a message indicating the correct answer along with the user's score.

  Args:
    score (int): The score to display in the message.

  Retrieves two message strings from the string table using 'the_lock' as the category,
  concatenates them with the score, and prints the result as HTML.
  """
  s1 = get_string_from_string_table('the_lock', 'msg1')
  s2 = get_string_from_string_table('the_lock', 'msg2')
  html_print(s1 + " " + str(score)+ " " +  s2 + " ")



'''def display_visual_result():
  language = get_language()
  if score >= 8:
    #print("פתרתם נכון " + str(score)+ " תרגילים מתוך 8 תרגילים ")
    s = get_string_from_string_table('the_lock', 'msg10')
    print(s)#("זהו זה, פתרתם את כל תרגילי הריענון,")
    s = get_string_from_string_table('the_lock', 'msg11')
    print(s)#("מתחילים את שנה ב' ברגל ימין")
    display(HTML('<h1><font color="red"> בהצלחה</font></h1>'))
    if language == 'hebrew':
      display(HTML(html_open_2))
    else:
      display(HTML(html_open_2_ar))
    display(HTML(html_fireworks))
  #elif score >= 8:
    #print("פתרתם נכון " + str(score)+ " תרגילים מתוך 8 תרגילים ")
    #print("איזה תותחיות ותותחים הצלחתם לפתוח את הכספת :-)")
    #print("איזה עוד הפתעות מחכות לנו בארון?")
    #display(HTML(html_open_2))'
  elif score == 6 :
    #print("פתרתם נכון " + str(score)+ " תרגילים מתוך 8 תרגילים")
    s = get_string_from_string_table('the_lock', 'msg13')
    print(s)#("כל הכבוד, הצלחתם לפרוץ את המנעול ולפתוח את הארון.")
    s = get_string_from_string_table('the_lock', 'msg14')
    print(s)#("וואוווו ... יש בפנים כספת, מה יש בה? איך פותחים אותה?")
    if language == 'hebrew':
      display(HTML(html_open_1))
    else:
      display(HTML(html_open_1_ar))
  elif score == 7 :
    #print("פתרתם נכון " + str(score)+ " תרגילים מתוך 8 תרגילים")
    #s = get_string_from_string_table('the_lock', 'msg13')
    #print(s)#("כל הכבוד, הצלחתם לפרוץ את המנעול ולפתוח את הארון.")
    s = get_string_from_string_table('the_lock', 'msg17')
    print(s)#("וואוווו ... יש בפנים כספת, מה יש בה? איך פותחים אותה?")
    if language == 'hebrew':
      display(HTML(html_open_1))
    else:
      display(HTML(html_open_1_ar))
  else:
    #print("פתרתם נכון " + str(score)+ " תרגילים מתוך 8 תרגילים, הארון עדיין נעול")
    display(HTML(html_close))'''


