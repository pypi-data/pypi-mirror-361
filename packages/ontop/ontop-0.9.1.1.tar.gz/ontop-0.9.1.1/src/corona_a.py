def print_cities():
    """
    Prints the city population data, ordered by city name.
    """
    print(cities)

def get_population(cities, city_name):
    """
    Return the population of a city.

    Parameters
    ----------
    cities : DataFrame. The cities dataset.

    city_name : str. The city_name from the city population dataset.
    """
    city = filter_data(cities, 'city_name', city_name)
    return city.iloc[0].population
    
def get_column_as_list(data, field):
    return sorted(list(set(data[field].to_list())))    
    
def get_cities_list(cities):
    return cities["city_name"].to_list()    
    
    
    
    
    
    
    
    