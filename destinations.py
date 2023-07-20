import requests
import sqlite3
import config
import time


def create_tables():
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL
                 )""")

    c.execute("""CREATE TABLE IF NOT EXISTS search_history (
                 user_id INTEGER NOT NULL,
                 location TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (user_id) REFERENCES users (user_id)
                 )""")

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    c.execute("SELECT user_id FROM users WHERE username=? AND password=?",
              (username, password))
    user_id = c.fetchone()
    if user_id:
        print("Login successful!")
        return user_id[0]
    else:
        print("Invalid username or password.")
        return None

def print_search_history(user_id):
    c.execute("SELECT location, timestamp FROM search_history WHERE user_id=?", (user_id,))
    search_history = c.fetchall()

    if not search_history:
        print("Search history is empty.")
    else:
        print("\nSearch History:")
        for entry in search_history:
            location, timestamp = entry
            print("Timestamp:", timestamp)
            print("Location:", location)
            print("-" * 20)

def choose_categories():

    categories_dict = {
        "Arts and Entertainment": 10000,
        "Community": 12000,
        "Dining and Drinking": 13000,
        "Events": 14000,
        "Landmarks and Outdoors": 16000,
        "Retail": 17000,
        "Sports": 18000,
        "Travel and Transportation": 19000,
        "Lodging": 19009
    }

    categories_str = ""

    print("\nLocation Categories:")
    print("Select any number of location categories (or none) to refine your results\n")
    
    for category_name, category_id in categories_dict.items():
        print(f"{category_id}: {category_name}")
    time.sleep(0.65)

    while True:
        user_choice = input("\nEnter a category ID to add (or \"F\" to finish): ")
        
        if user_choice.upper() == "F":
            break
        
        try:
            user_id = int(user_choice)
            if user_id in categories_dict.values():
                for category_name, category_id in categories_dict.items():
                    if category_id == user_id:
                        name = category_name
                categories_str += str(user_id) + ","
                print(name, "added!")
            else:
                print("Invalid category ID: please try again")
        except ValueError:
            print("Invalid input: please enter a category ID or \"F\" to finish")

    categories_str = categories_str.rstrip(',')
    return categories_str

def get_coordinates(search):

    base_url = "https://api.opencagedata.com/geocode/v1/json"
    url = base_url + "?q=" + search + "&key=" + config.key1

    response = requests.get(url)
    data = response.json()
    status_code = int(data["status"]["code"])

    if status_code == 200:
        if data["total_results"] == 1:
            result = data["results"][0]
            latitude = result["geometry"]["lat"]
            longitude = result["geometry"]["lng"]
            return latitude, longitude
        elif data["total_results"] == 0:
            print("Error: location not found\n- please enter a valid location\n")
        else:
            print("Error: multiple locations or invalid location found\n- please check for mispellings or provide a more specific location\n")
    else:
        print("Error", str(status_code) + ":", data["status"]["message"])

    return None

def get_destinations(latitude, longitude, categories_str, user_id=None):
    
    url = "https://api.foursquare.com/v3/places/search"

    header = {"accept": "application/json", "Authorization": config.key2}
    param_dict = {"ll": str(latitude) + "," + str(longitude), "sort": "DISTANCE", "radius": 5000, "categories": categories_str}

    response = requests.get(url, params = param_dict, headers = header)
    data = response.json()

    if response.status_code == 200:
        display_locations(data["results"])
    else:
        print(data["message"])

    if user_id != None:
        locations_str = ""
        for result in data["results"]:
            location = result["name"] + ", " + result["location"]["formatted_address"]
            locations_str += location + "\n"

        c.execute("INSERT INTO search_history (user_id, location) VALUES (?, ?)", (user_id, locations_str))
        conn.commit()

def display_locations(results):
    if len(results) == 0:
        print("No destinations found")
    else:
        print("\n" + str(len(results)), "Locations found:\n")
        for result in results:
            name = result["name"]
            address = result["location"]["formatted_address"]
            print("Place Name:", name)
            print("Address:", address + "\n")

def quit_option():
    time.sleep(0.65)
    option = input("Enter any key to continue or 'Q' to quit: ")
    if option.lower() == "q":
        return True
    else:
        print()
        return False


conn = sqlite3.connect("destination_finder.db")
c = conn.cursor()
create_tables()

print("Destination Finder")
print("+-+-+-+-+-+-+-+-+-\n")

print("This destination finder will show tourist destinations in your chosen area")
print("For best results, enter zipcode or postcode followed by country name")
print("Example: 12345 United States of America\n")

time.sleep(0.65)

while True:
    
    user_id = None
    
    print("1: Guest Search")
    print("2: Login")
    print("3: Sign Up")
    print("Q: Quit")

    option = input("Choose an option: ")

    if option == "1":
        query = input("Enter location: ")
        categories_str = choose_categories()
        latitude, longitude = get_coordinates(query)
        get_destinations(latitude, longitude, categories_str, user_id)
        if quit_option():
            break

    elif option == "2":
        
        user_id = login()
        if user_id != None:

            while True:

                print("S: Search")
                print("H: View Search History")
                print("R: Return to Main Menu")

                sub_option = input("Choose an option: ")

                if sub_option.upper() == "S":
                    query = input("Enter location: ")
                    categories_str = choose_categories()
                    latitude, longitude = get_coordinates(query)
                    get_destinations(latitude, longitude, categories_str, user_id)

                elif sub_option.upper() == "H":
                    print_search_history(user_id)

                elif sub_option.upper() == "R":
                    break
        else:
            if quit_option():
                break

    elif option == "3":

        while True:
        
            username = input("Enter username: ")
            password = input("Enter password: ")

            c.execute("SELECT username FROM users WHERE username=?", (username,))
            
            if c.fetchone():
                print("Error: username already exists - please choose a different username")
                if quit_option():
                    break
            else:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                print("Account created successfully!")
                break
        
    elif option.lower() == "q":
        break
    
c.close()
conn.close()
print("\nThank you for using Destination Finder!")
