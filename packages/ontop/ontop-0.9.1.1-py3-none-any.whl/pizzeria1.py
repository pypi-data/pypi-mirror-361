from media import *
from html_helper import *
from messages import *
from string_table import *




def run_me():
    """
    This function runs the random banner animation.

    Parameters:
    None

    Returns:
    None
    """
    run_banner_rnd()


def draw_pizza(num_slices, topping):
    """
    Draws a pizza image with the specified number of slices and topping.

    Parameters:
    num_slices (int): The number of pizza slices to be displayed. If the number is not an integer,
                      an error message will be displayed and the function will return without drawing the pizza.
                      The number of slices should be between 1 and 8. If the number is less than or equal to 0,
                      no pizza will be drawn. If the number is greater than 8, it will be reduced to 8.
    topping (str): The topping to be displayed on the pizza. If the topping is not in the predefined list,
                   it will be set to 'blank'. If the topping is an empty string, it will also be set to 'blank'.

    Returns:
    None
    """
    topping_list = ["blank", "mushrooms", "olives","pineapple", "tomato"]
    if not type(num_slices) is int:
        s = get_string_from_string_table('pizzeria1', 'draw_pizza_1')
        error_msg("draw_pizza", s)
        return
    topping = topping.lower()
    if(topping==''):
     topping = 'blank'
    elif not topping in topping_list:
     topping = 'blank'
    if num_slices <= 0:
        return
    if num_slices > 8:
        num_slices = 8
    pizza_img_url = 'https://ontopnew.s3.il-central-1.amazonaws.com/pizzeria1/Images/pizza_topping/pizza_' + topping + '_' + str(num_slices)+'.png'
    show_image(pizza_img_url)


def download_pic(url):
    """
    Downloads an image from the specified URL and saves it locally.

    Parameters:
    url (str): The URL of the image to be downloaded. The URL should be a valid and accessible image file.

    Returns:
    None
    """
    download_image_from_web(url)

def print_order(my_name, num_slices, topping, total_price, order_number=101):
  """
      This function generates and displays an HTML order receipt for a pizza order.
      The receipt includes the customer's name, pizza topping, number of slices, total price,
      and an image of the pizza.

      Parameters:
      my_name (str): The customer's name.
      num_slices (int): The number of pizza slices. Must be an integer between 1 and 8.
                        If not an integer, an error message will be displayed.
      topping (str): The pizza topping. Must be one of the predefined toppings.
                     If not a predefined topping, it will be set to 'blank'.
      total_price (float): The total price of the order.
      order_number (int, optional): The order number. Defaults to 101.

      Returns:
      None
  """
  if not type(num_slices) is int:
    s = get_string_from_string_table('pizzeria1', 'print_order_1')
    error_msg("print_order", s)
    return
  html = '''
  <html>
<head>
<meta charset="utf-8">
</head>
<body>
<div style="width: 500px; height: 380px; padding: 10px; font-family: Arial; position: relative;text-align:center; background-color:#FFFBDB">
    <span style="font-size: 30px; font-weight: bold;">{***print_order_2***}</span><br>
		<span style="font-size: 15px; font-weight: bold;">{*order_date*}</span><br>
	<span style="font-size: 20px; font-weight: bold;"> {*order_num*} {***print_order_3***}</span><br>
	<span style="font-size: 20px; font-weight: bold;">{***print_order_41***} {*name1*} </span><br><br>
	{*img*}<br><br>
	<span style="font-size: 20px; font-weight: bold;"> {*topping*} {***print_order_5***}</span><br>
	<span style="font-size: 20px; font-weight: bold;"> {*slices*} {***print_order_6***}</span><br>
	<span style="font-size: 20px; font-weight: bold;"> {*price*} {***print_order_7***}</span><br><br>
</div>
</body>
</html>'''
  today = datetime.date.today()
  html = html.replace('{*order_date*}', str(today.day) + "." +  str(today.month) + "." +  str(today.year))
  html = html.replace('{*order_num*}', str(order_number))
  html = html.replace('{*name*}', my_name)
  html = html.replace('{*name1*}', my_name)
  html = html.replace('{*topping*}', topping)
  html = html.replace('{*slices*}', str(num_slices))
  html = html.replace('{*price*}', str(total_price))
  html_img_tag = ''
  encoded_image = ''
  if not is_file_exist('/content/photo.jpg'):
    download_image_from_web("https://ontopnew.s3.il-central-1.amazonaws.com/pizzeria1/Images/intro1_pizza_box.png")
	
  
  encoded_image = convert_img_to_base64('/content/photo.jpg')
  html_img_tag = f"""
<img src="data:image/jpeg;base64,{encoded_image}" width="220" height="160"/>
"""
  html = html.replace('{*img*}', str(html_img_tag))

  s = get_string_from_string_table('pizzeria1', 'print_order_2')
  html = html.replace('{***print_order_2***}', s)
  s = get_string_from_string_table('pizzeria1', 'print_order_3')
  html = html.replace('{***print_order_3***}', s)
  s = get_string_from_string_table('pizzeria1', 'print_order_4')
  html = html.replace('{***print_order_4***}', s)
  html = html.replace('{***print_order_41***}', s)
  s = get_string_from_string_table('pizzeria1', 'print_order_5')
  html = html.replace('{***print_order_5***}', s)
  s = get_string_from_string_table('pizzeria1', 'print_order_6')
  html = html.replace('{***print_order_6***}', s)
  s = get_string_from_string_table('pizzeria1', 'print_order_7')
  html = html.replace('{***print_order_7***}', s)
  display(HTML(html))
  if os.path.exists('/content/photo.jpg'):
    # Delete the file
    os.remove('/content/photo.jpg')

def take_selfie(timer):
  selfie(timer)
