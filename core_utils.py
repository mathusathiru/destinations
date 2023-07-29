import time, bcrypt
import requests
import config, database_utils

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def signup():
    print()
    while True:
        username = input("Enter username: ")
        if len(username) < 3:
            print("Error: username must be at least three characters\n")
        else:
            break
    while True:
        password = input("Enter password: ")
        if len(password) < 8:
            print("Error: password must be at least eight characters\n")
        else:
            break
    password = hash_password(password)
    return username, password


def enter_query():
    query = input("\nEnter location: ")
    if len(query) < 2:
        print("\nError: query is too short (2+ characters needed)")
        time.sleep(0.65)
        return None
    else:
        return query


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
    }
    categories_str = ""
    print("\nLocation Categories:")
    print("Select location categories (or none) to refine your results\n")
    for category_name, category_id in categories_dict.items():
        print(f"{category_id}: {category_name}")
    time.sleep(0.65)
    while True:
        user_choice = input("\nEnter an ID to add (or \"F\" to finish): ")
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
            print("Invalid input: please enter an ID or \"F\" to finish")
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
            print("\nError: location not found\n-enter a valid location")
            time.sleep(0.65)
        else:
            print("\nError: multiple locations or invalid location found")
            print("-check for mispellings")
            print("-provide a more specific location")
            time.sleep(0.65)
    else:
        print("\nError", str(status_code) + ":", data["status"]["message"])
    return None


def get_destinations(c, conn, latitude, longitude, categories_str, user_id=None):
    url = "https://api.foursquare.com/v3/places/search"
    header = {"accept": "application/json", "Authorization": config.key2}
    param_dict = {"ll": str(latitude) + "," + str(longitude),
                  "sort": "DISTANCE",
                  "radius": 5000,
                  "categories": categories_str}
    response = requests.get(url, params=param_dict, headers=header)
    data = response.json()
    if response.status_code == 200:
        display_locations(data["results"])
    else:
        print(data["message"])

    if user_id is not None:
        database_utils.save_search_history(c, conn, user_id, data["results"])


def display_locations(results):
    if len(results) == 0:
        print("No destinations found")
    else:
        print("\n" + str(len(results)), "Locations found:\n")
        for index, result in enumerate(results):
            name = result["name"]
            address = result["location"]["formatted_address"]
            print("Place Name:", name)
            print("Address:", address)
            if index < len(results):
                print()  

