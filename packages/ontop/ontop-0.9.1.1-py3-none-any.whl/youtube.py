from media import *
from html_helper import *
from messages import *
from string_table import *
from ontop_csv import *
from ontop_graph import *

def column_to_list(df, col_name):
  return return_column_values(df, col_name)

def print_column_to_list(df, col_name):
  print_column_values(df, col_name)

def sort_data(df, col_name, ascending=False):
  return return_sorted_by_column(df, col_name, ascending)

'''def print_sorted_by_column(df, col_name):
  print_sorted_by_column(df, col_name)'''


def print_top(df, count):
  print_csv_top(df, count)  
  #return return_top(df, count)



# def unique_list(li): # יעשו לבד או ניתן להם??
#   result = list(set(li))
#   return result

def unique_list(input_list):

    seen = set()
    result = []
    for item in input_list:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def draw_songs_graph(songs_list, title):
  new_graph()
  for row in songs_list.itertuples(index=True):
    #print(str(row.artist) + " " + str(row.views))
    add_bar_to_graph(row.title, row.views)
  draw_graph(title, "", "צפיות (מיליונים)")