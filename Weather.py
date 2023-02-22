#!/usr/bin/env python3

from sys import argv, exit
from datetime import datetime, date
from getopt import getopt, GetoptError
from os.path import abspath, exists, basename
from csv import writer
from subprocess import run
import sqlite3

additional_modules = ["requests"]
for module in additional_modules:
    run(["pip", "install", module], check=True, timeout=60)

import requests

API_KEY = "YOUR_APIKEY"
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/"
ONE_CALL = "onecall"
HISTORY_CALL = "onecall/timemachine"
    
def get_weather(argv:list)->None:
    """Reads parameters given through standard input and then pass these arguments to further verification.

    Args:
        argv (list): Parameters given through standard input.
    """
    if len(argv) == 1:
        script_help()
    else:
        argv_city = "Wrocław"
        argv_day = str(date.today())
        argv_file = ""
        try:
            opts, args = getopt(argv[1:], "hc:d:f:", ["help", "city=", "date=", "file="])
        except GetoptError as error:
            script_help(error.args[0]) 
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                script_help() 
            elif opt in ("-c", "--city"):
                argv_city = arg.strip().title()
            elif opt in ("-d", "--date"):
                argv_day = str(arg.strip())
            elif opt in ("-f", "--file"):
                argv_file = arg.strip() 
        input_data = [argv_city, argv_day, argv_file]
        if check_input_data(input_data):
            get_weather_information(input_data)
            
def script_help(more_info:str = "")->None:
    """Print to standard output how use of script. Additionally receives and prints information regarding errors. Terminates script.
    
    Keyword arguments:
    more_info -- error message
    """
    basic_message = f"""
    Script prints or saves to file information regarding weather, based on input data.
    
    {basename(argv[0])} -c <city> -d <date> -f <file>

    -c --city       Specify the name of the city.                       Defaults to Wrocław

    -d --date       Specify the date for the weather forecast.           
                    Uses ISO format: yyyy-mm-dd                         Defaults to current day
                    Date can't be lower than January 1, 1979

    -f --file       OPTIONAL. Specify filename to save the response.
                    If not given value then prints forecast to
                    standard output, else saves data to file.           Defaults to empty string
                    Data is saved in CSV format, please note that
                    script accepts only alphanumerical values.
                        
    Examples:       python Weather.py -c Kraków
                    python Weather.py --date 2020-1-12 
                    python Weather.py -f test
                    python Weather.py -c Szczecin -d 2020-12-12 -f test 
    """
    if more_info:
        print("\n" + more_info + "\n" + basic_message)
    else:
        print(basic_message)
    exit(1)

def check_input_data(input_data: list)->bool:
    """Check if input data matches the criteria specified for the script. 

    Args:
        input_data (list): data provided by user durning script invocation.

    Returns:
        bool: True is data matches criteria, else pass error information and control to script_help()
    """
    city = input_data[0].split(" ")
    for part in city:
        if part.isalpha():
            continue
        else:
            script_help(f"{input_data[0]} city name not recognized.")
    try:
        datetime.strptime(input_data[1], "%Y-%m-%d").date()
    except ValueError as error:
        script_help(error.args[0])
    if input_data[2] == "" or input_data[2].isalnum():
        return True
    else:
        script_help(f"{input_data[2]} is not a valid name. Script supports only alphanumeric names. Please use characters that are alphanumeric - alphabet letter (a-z) and numbers (0-9)")

def get_weather_information(valid_input_data:list)->None:
    """Receives verified information from standard input. Based on user choice prints information to standard output or saves data in specified CSV file.

    Args:
        valid_input_data (list): verified data from standard input.
    """
    cities = check_cache("city", valid_input_data[0])
    if cities:
        cities = [{"name": city[0], "country": city[1], "state": city[2], "lat": city[3], "lon": city[4]} for city in cities]
        if len(cities) > 1:
            city_coordinates = select_city(cities)
        else:
            city_coordinates = {"lat": cities[0]["lat"], "lon": cities[0]["lon"], "country": cities[0]["country"], "state": cities[0]["state"]}
    else:
        city_coordinates = get_coordinates(valid_input_data[0])
    weather_for_city = check_cache("weather", valid_input_data[0], valid_input_data[1], city_coordinates["country"], city_coordinates["state"])
    if weather_for_city:
        weather_data = {
            "city": weather_for_city[0][0], 
            "country": weather_for_city[0][1], 
            "state": weather_for_city[0][2], 
            "day": weather_for_city[0][3], 
            "temperature": weather_for_city[0][4], 
            "rainfall": weather_for_city[0][5], 
            "snowfall": weather_for_city[0][6]}
    else:
        day_difference = (datetime.strptime(valid_input_data[1], "%Y-%m-%d").date() - date.today()).days
        if datetime.strptime(valid_input_data[1], "%Y-%m-%d").date() < date.today():
            date_copy = valid_input_data[1]
            valid_input_data[1] = get_date_time(valid_input_data[1])
            weather_data = get_weather_from_api(city_coordinates, valid_input_data[1], valid_input_data[0], date_copy, country=city_coordinates["country"], state=city_coordinates["state"])
        elif day_difference < 8:
            weather_data = get_weather_from_api(city_coordinates, day_difference, valid_input_data[0], valid_input_data[1], country=city_coordinates["country"], state=city_coordinates["state"])
        else:
            script_help("You can only check daily forecast for 8 days ahead.")     
    if valid_input_data[2]:
        add_to_csv_file(valid_input_data[2], weather_data)
    else:
        print_weather(weather_data)

def check_cache(table_name:str, city_name:str = "", current_date:str = "", country:str = "", state:str = "")->list or bool:
    """Check if data regarding city or forecast for given city is already in the script cache. If cache is not found, creates it.

    Args:
        table_name (str): name of table from SQLite database - 'city' or 'weather'
        city_name (str, optional): name of searched city. Defaults to "".
        current_date (str, optional): current date. Defaults to "".
        country (str, optional): name of country where city is located. Defaults to "".
        state (str, optional): name of state where city is located. Defaults to "".

    Returns:
        list or bool: return False if cache does not exist before invocation, else returns searched information in cache or empty list if data is not found.
    """
    cache_name = "weather_cache.db"
    if exists(cache_name):
        print("Browsing cache...")
        connection = sqlite3.connect(cache_name)
        cursor = connection.cursor()
        if table_name == "city":
            cursor.execute(f"SELECT * FROM {table_name} WHERE name LIKE '%{city_name}%'")
            data = cursor.fetchall()
            connection.close()
            return data
        elif table_name == "weather":
            cursor.execute(f"SELECT * FROM {table_name} WHERE city LIKE '%{city_name}%' AND day = '{current_date}' AND country LIKE '%{country}%' AND state LIKE '%{state}%'")
            data = cursor.fetchall()
            connection.close()
            return data
        else:
            script_help("Something went terribly wrong!")
    else:
        create_cache(cache_name)
        return False

def create_cache(name:str)->None:
    """Creates cache for the script.
    
    Args:
        name (str): name of cache
    """
    connection = sqlite3.connect(name)    
    connection.execute("""CREATE TABLE city (
    name text,
    country text,
    state text,
    lat real,
    lon real)""")

    connection.execute("""CREATE TABLE weather (
    city text,
    country text,
    state text,
    day text,
    temperature real,
    rainfall real,
    snowfall real)""")
    print("Creating cache... ")
    connection.commit()
    connection.close()

def get_coordinates(location: str, limit:int = 5)->dict:
    """Ask API for coordinates of given city. If there is found more than 1 city, then pass control to another function to resolve conflict.
    Deletes repetitions.

    Args:
        location (str): name of a city
        limit (int): number or responses from API

    Returns:
        dict: information regarding longitude, latitude, country and state of given city.
    """
    print("Cache for given city not found. Connecting to API...")
    geo_params = {
        "q": location,
        "appid": API_KEY,
        "limit": limit
    }
    try:
        response = requests.get(url = GEOCODE_URL, params = geo_params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        script_help(error.args[0]) 
    else:
        data = response.json()
        filtered_data = []
        if data:
            for city in data:
                if city["name"] != location: 
                    city["name"] = location
                try:
                    del city["local_names"]
                except KeyError:
                    pass
                try:
                    city["state"]
                except KeyError:
                    city.update({"state": "Unknown"})
                finally:
                    filtered_data.append(city)
            data = delete_repetitions(filtered_data)
            add_data_to_cache("city", data)
            if len(data) == 1:
                return {"lat": data[0]["lat"], "lon": data[0]["lon"], "country": data[0]["country"], "state": data[0]["state"]}
            else:
                return select_city(data)
        else:
            script_help(f"{location} city not found in the API Database. Please try to write city name in different language or insert valid name.")
            
def delete_repetitions(cities:list)->list:
    """Loop through list in search of duplicate values.

    Args:
        cities (list): list of cities and their locations

    Returns:
        list: list without duplicates
    """
    new_list = list(filter(lambda city: city["state"] != cities[0]["state"], cities))
    new_list.insert(0, cities[0])
    return new_list

def select_city(cities:list)->dict:
    """Asks user to choose one city from the list.

    Args:
        cities (list): cities with the same names in different locations.

    Returns:
        dict: information regarding longitude, latitude, country and state of chosen city.
    """
    number = -1
    index = 0
    while number < 0 or number >= len(cities):
        print(f"Similarities for {cities[0]['name']} detected. What location do you have in mind?")
        for city in cities:
            print(f"{index}. Country: {city['country']}, State: {city['state']}")
            index += 1
        index = 0 
        try:    
            number = int(input("Please select a number: "))
        except ValueError:
            print("Please follow the instructions", end= "")
        finally:
            print(end= ("\n"*2))
    return {"lat": cities[number]["lat"], "lon": cities[number]["lon"], "country": cities[number]["country"], "state": cities[number]["state"]}

def add_data_to_cache(table:str, data:dict)->None:
    """adds given data to selected table.

    Args:
        table (str): table name
        data (dict): values to input to cache
    """
    cache_name = "weather_cache.db"
    connection = sqlite3.connect(cache_name)
    cursor = connection.cursor()    
    if table == "city":
        for item in data:
            cursor.execute(f"INSERT INTO {table} VALUES (:name, :country, :state, :lat, :lon)",
                        {
                            "name": item["name"],
                            "country": item["country"],
                            "state": item["state"],
                            "lat": item["lat"],
                            "lon": item["lon"]
                        })
        connection.commit()
    elif table == "weather":
        cursor.execute(f"INSERT INTO {table} VALUES (:city, :country, :state, :day, :temperature, :rainfall, :snowfall)",
                    {
                        "city": data["city"],
                        "country": data["country"],
                        "state": data["state"],
                        "day": data["day"],
                        "temperature": data["temperature"],
                        "rainfall": data["rainfall"],
                        "snowfall": data["snowfall"]
                    })
        connection.commit()
    else:
        script_help("Something went terribly wrong!")

def get_date_time(provided_date:str)->int:
    """Convert date in ISO format to timestamp. Pass control to function terminating script if provided with incorrect value.

    Args:
        provided_date (str): date in ISO format: yyy-mm-dd

    Returns:
        int: timestamp created from provided date
    """
    try:
        input_date = int(datetime.strptime(provided_date, "%Y-%m-%d").timestamp())
    except OSError as error:
        script_help("Provided data can't be lower than January 1, 1979")
    else:
        return input_date

def get_weather_from_api(coordinates:dict, given_df:int, city:str, given_date:str, country:str = "", state:str = "")->dict:
    """Based on input receive historical or forecast information regarding weather in given city.

    Args:
        coordinates (dict): latitude and longitude of selected city
        given_df (int): timestamp or difference in days
        city (str): city name
        given_date (str): date in ISO format
        country (str, optional): country in which city is located. Defaults to "".
        state (str, optional): state in which city is located. Defaults to "".

    Returns:
        dict: information regarding city, country, state, date, temperature, rainfall and snowfall
    """
    print("Cached weather info not found. Connecting to API...")
    if given_df < 8:
        city_parameters = {
        "lat": coordinates["lat"],
        "lon": coordinates["lon"],
        "appid": API_KEY,
        "exclude": "current,minutely,hourly,alerts",
        "units": "metric"  
            }
        api_url = WEATHER_BASE_URL + ONE_CALL
        historic = False
    else:
        city_parameters = {
        "lat": coordinates["lat"],
        "lon": coordinates["lon"],
        "dt": given_df,
        "appid": API_KEY,
        "units": "metric"  
            }        
        api_url = WEATHER_BASE_URL + HISTORY_CALL
        historic = True
    try:
        response = requests.get(url = api_url, params= city_parameters)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        script_help(f"{error.args[0]}\nPlease specify date above January 1, 1979")
    else:
        data = response.json()
        data = select_weather_data(data, historic, given_df)
        main_data = {"city": city, "country": country, "state": state, "day": given_date}
        main_data.update(data)
        add_data_to_cache("weather", main_data)
        return main_data

def select_weather_data(data:list, is_historic:bool, day:int=0)->dict:
    """Select interesting information regarding weather.

    Args:
        data (list): raw data from API call
        is_historic (bool): information whether data comes from historic or forecast weather
        day (int, optional): day difference. Only for forecast. Defaults to 0.

    Returns:
        dict: information regarding temperature, rainfall and snowfall
    """
    temp = 0
    rainfall = 0.0
    snowfall = 0.0
    if is_historic:
        temp = data["data"][0]["temp"]
        try:
            rainfall = data["data"][0]["rain"]["1h"]
        except KeyError:
            pass
        try:
            snowfall = data["data"][0]["snow"]["1h"]
        except KeyError:
            pass
        return {"temperature": temp, "rainfall": rainfall, "snowfall": snowfall}
    else:
        temp = data["daily"][day]["temp"]["day"]
        try:
            rainfall = data["daily"][day]["rain"]
        except KeyError:
            pass
        try:
            snowfall = data["daily"][day]["snow"]
        except KeyError:
            pass
        return {"temperature": temp, "rainfall": rainfall, "snowfall": snowfall}

def add_to_csv_file(file_name:str, given_data:dict)->None:
    """Add processed data to chosen CSV file.

    Args:
        file_name (str): name of CSV file
        given_data (dict): information regarding city, country, state, date, temperature, rainfall and snowfall
    """
    if exists(f"{file_name}.csv"):
        with open(f"{file_name}.csv", "a", newline='') as file:
            cursor = writer(file)
            cursor.writerow(given_data.values())
    else:
        with open(f"{file_name}.csv", "a", newline='') as file:
            cursor = writer(file)
            cursor.writerow(given_data.keys())
            cursor.writerow(given_data.values())  
    print(f"Data successfully added to {file_name}.csv.\nYou can find new data located in {abspath(f'{file_name}.csv')}")      

def print_weather(data:dict)->None:
    """Print information to standard output regarding weather in chosen city.
    
    Args:
        data (dict): information regarding city, day, temperature, rainfall and snowfall
    """
    print(f"""
    Weather forecast for the city of {data['city']} for the day: {data['day']}.
    Temperature: {data['temperature']} Celcius Degrees.
    Rainfall: {data['rainfall']} mm.\tSnowfall: {data['snowfall']} mm.
    Have a good day!
    """)

if __name__ == "__main__":
    get_weather(argv)
else:
    print("Use me as main module.")