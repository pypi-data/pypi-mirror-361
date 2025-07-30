from media import *
from html_helper import *
from messages import *
from string_table import *


import random
from datetime import datetime

def courseware_game():
  # הגדרת קודים של צבעים שונים
  RED = '\033[31m'
  GREEN = '\033[32m'
  # הגדרת הקוד שמחזיר לצבע ברירת מחדל
  RESET = '\033[0m'
  # אתחול מספר הנסיונות המקסימלי ל-3
  max_chances = 3
  # אתחול מספר התשובות הנכונות ל-0
  points = 0
  # אתחול הבונוס ל-0
  bonus = 0
  min_number = -1
  max_number = -1
  
  print("===================================")
  #print("🎮 ברוכים הבאים למשחק לוח הכפל! 🎮")
  s = get_string_from_string_table('courseware_code', 'welcome')
  print("🎮 " + s + " 🎮")
  print("===================================")
  number_of_questions = int(input("How many questions do you want to answer? "))
  level =  int(input("Choose level (1-3) 1 - EASY 2 - MEDIUM 3 - HARD: "))
  print("Level ", level)
  if level == 1:
    max_chances = 3
    speed = 5
    min_number = 0
    max_number = 5
  elif level == 2:
    max_chances = 2
    speed = 4
    min_number = 2
    max_number = 8
  else:
    max_chances = 1
    speed = 3
    min_number = 5
    max_number = 9
  # לולאה המציגה תרגילי כפל
  for count_questions in range(0, number_of_questions):
    print("-----------------------------------")
    print("Question", count_questions + 1)
    # הגרלת מספרים לתרגיל
    number1 = random.randint(min_number, max_number)
    number2 = random.randint(min_number, max_number)
    print(number1, "X", number2, "=")
    correct_answer = number1 * number2
    start_time = datetime.now()
    student_answer = int(input("what is your answer? "))
    count_chances = 1

    # כל עוד לתלמיד יש עוד נסיונות והתשובה לא נכונה, מדפיסים משוב שלילי וקולטים תשובה נוספת
    while student_answer != correct_answer and count_chances < max_chances:
      print(RED + "oops🤪" + RESET)
      count_chances = count_chances + 1
      # אם זהו מספר הנסיונות האחרון מדפיסים הודעה מתאימה
      if count_chances == max_chances:
        print("last try 👇")
      student_answer = int(input("try again: "))

    # טיפול בתשובה נכונה
    if student_answer == correct_answer:
      print(GREEN + "bravo⭐" + RESET)
      # עדכון מספר התשובות הנכונות
      points = points + 1
      # חישוב המהירות שבה התלמיד ענה
      end_time = datetime.now()
      time_taken = (end_time - start_time).total_seconds()
      # בדיקה האם מגיע בונוס על נסיון ראשון
      if count_chances == 1:
        s = get_string_from_string_table('courseware_code', 'bonus_first')
        print(s + " 🚀")
        #print("בונוס על הצלחה בניסיון ראשון! 🚀")
        bonus = bonus + 1
      # בדיקה האם מגיע בונוס על מהירות
      if time_taken < speed:
        bonus = bonus + 1
        s= get_string_from_string_table('courseware_code', 'bonus_speed')
        print(s + " 🚀")
    # טיפול בתשובה לא נכונה
    else:
      print(RED + "oops🤪" + RESET)
    # אם זאת לא השאלה האחרונה נדפיס שעוברים לשאלה הבאה
    if count_questions < number_of_questions - 1:
      s= get_string_from_string_table('courseware_code', 'next_question')
      print("🔽 " + s)


  # טיפול בסוף המשחק, הצגת ניקוד
  score = (points / number_of_questions) * 100
  score = round(score, 0)
  print("===================================")
  if level == 1:
    print("You get bonus 5 points for level 1")
    bonus = bonus + 5
  elif level == 2:
    print("You get bonus 10 points for level 2")
    bonus = bonus + 10
  else:
    print("You get bonus 15 points for level 3")
    bonus = bonus + 15

  print("===================================")
  print("End Of Game 🎮")
  print("===================================")
  print("Your score:", score)
  print("Bonus:", bonus)
  print("Total:", score + bonus)
  print("===================================")

  # משוב מילולי בסיום
  if points <= number_of_questions * 0.5:
    s= get_string_from_string_table('courseware_code', 'champ2')
    print("🙏 " + s)
    #print("🙏עוד קצת תרגול ותהיו אלופים ואלופות ")
  elif points > number_of_questions * 0.5 and points <= 0.8*number_of_questions:
    s= get_string_from_string_table('courseware_code', 'good_work')
    print("👏 " + s)
    #print("👏!עבודה טובה")
  elif points >= number_of_questions * 0.8 and bonus <= number_of_questions*0.5:
    s= get_string_from_string_table('courseware_code', 'perfect')
    s = print("⭐ " + s)
   # print("⭐!עבודה מצוינת")
  else:
    s= get_string_from_string_table('courseware_code', 'champ1')
    print("🏆 " + s)
    #print("🏆!עבודה של אלופות ושל אלופים")
  print("===================================")

