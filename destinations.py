import sqlite3
import requests
import config
import time
import bcrypt


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def create_tables():
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL
                 )""")

    c.execute("""CREATE TABLE IF NOT EXISTS search_history (
                 search_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 place_name TEXT NOT NULL,
                 address TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (user_id) REFERENCES users (user_id)
                 )""")


def login():
    username = input("\nEnter your username: ")
    password = input("Enter your password: ")

    c.execute("SELECT user_id, password FROM users WHERE username=?",
              (username,))
    user_data = c.fetchone()

    if user_data and bcrypt.checkpw(password.encode("utf-8"),
                                    user_data[1].encode("utf-8")):
        print("\nLogin successful!")
        time.sleep(0.65)
        return user_data[0]
    else:
        print("\nError: invalid username or password")
        time.sleep(0.65)
        return None


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


def delete_user(user_id):
    c.execute("SELECT username FROM users WHERE user_id=?", (user_id,))
    username = c.fetchone()

    c.execute("DELETE FROM search_history WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM users WHERE user_id=?", (user_id,))

    conn.commit()
    print("Account for", username, "has been successfully deleted")
    time.sleep(0.65)


def check_search_history(user_id):
    c.execute("SELECT place_name, address, timestamp FROM search_history "
              "WHERE user_id=?", (user_id,))
    search_history = c.fetchall()

    if not search_history:
        return False
    else:
        return True


def print_search_history(user_id):
    c.execute("SELECT place_name, address, timestamp FROM search_history "
              "WHERE user_id=?", (user_id,))
    search_history = c.fetchall()

    if not search_history:
        print("\nSearch history is empty\n")
    else:
        print("\nSearch History:\n")
        for index, entry in enumerate(search_history):
            place_name, address, timestamp = entry
            print("Place Name:", place_name)
            print("Address:", address)
            print("Timestamp:", timestamp)
            if index < len(search_history) - 1:
                print("-" * 20)
            else:
                print()
    time.sleep(0.65)


def print_most_popular_searches(user_id):
    c.execute("SELECT place_name, address, COUNT(*) as search_count "
              "FROM search_history "
              "WHERE user_id=? "
              "GROUP BY place_name, address "
              "ORDER BY search_count DESC",
              (user_id,))
    popular_searches = c.fetchall()

    if not popular_searches:
        print("Search history is empty\n")
    else:
        print("\nMost Popular Searches:")
        for index, entry in enumerate(popular_searches):
            place_name, address, search_count = entry
            print("Place Name:", place_name)
            print("Address:", address)
            print("Search Count:", search_count)
            if index < len(popular_searches) - 1:
                print("-" * 20)
            else:
                print()
    time.sleep(0.65)


def search_history(user_id, keyword):
    c.execute("SELECT place_name, address, timestamp "
              "FROM search_history "
              "WHERE user_id=? AND (place_name LIKE ? OR address LIKE ?)",
              (user_id, f"%{keyword}%", f"%{keyword}%"))
    search_results = c.fetchall()

    if not search_results:
        print("No matching records found\n")
    else:
        print("\nSearch Results:\n")
        for index, entry in enumerate(search_results):
            place_name, address, timestamp = entry
            print("Place Name:", place_name)
            print("Address:", address)
            print("Timestamp:", timestamp)
            if index < len(search_results) - 1:
                print("-" * 20)
            else:
                print()
    time.sleep(0.65)


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


def get_destinations(latitude, longitude, categories_str, user_id=None):
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
        save_search_history(user_id, data["results"])


def save_search_history(user_id, results):
    for result in results:
        place_name = result["name"]
        address = result["location"]["formatted_address"]
        c.execute("INSERT INTO search_history (user_id, place_name, address) "
                  "VALUES (?, ?, ?)", (user_id, place_name, address))
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

print("This destination finder shows tourist destinations in your chosen area")
print("For best results, enter zipcode or postcode followed by country name")
print("Example: 12345 United States of America")

time.sleep(0.65)

while True:

    user_id = None
    print("\n------------------\n")

    print("1: Guest Search")
    print("2: Login")
    print("3: Sign Up")
    print("Q: Quit")

    option = input("\nChoose an option: ")

    if option == "1":

        try:
            query = enter_query()
            latitude, longitude = get_coordinates(query)
            categories_str = choose_categories()
            get_destinations(latitude, longitude, categories_str, user_id)
        except TypeError:
            pass

    elif option == "2":

        user_id = login()

        if user_id is not None:

            print()
            while True:

                print("------------------\n")

                print("1: Search")
                print("2: View Search History")
                print("3: Delete Account")
                print("Q: Return to Main Menu")

                sub_option = input("\nChoose an option: ")

                if sub_option == "1":
                    query = enter_query()
                    categories_str = choose_categories()
                    latitude, longitude = get_coordinates(query)
                    get_destinations(
                        latitude, longitude, categories_str, user_id)

                elif sub_option == "2":

                    if check_search_history(user_id) is True:

                        time.sleep(0.65)
                        print("\n------------------\n")

                        while True:

                            print("1: View All Searches")
                            print("2: View Popular Searches")
                            print("3: Search For Record")
                            print("Q: Return to User Menu")

                            search_option = input("\nChoose an option: ")

                            if search_option == "1":
                                print_search_history(user_id)

                            elif search_option == "2":
                                print_most_popular_searches(user_id)

                            elif search_option == "3":

                                while True:
                                    word = input("\nEnter keyword to search: ")
                                    if len(word) < 2:
                                        print("Error: enter 3+ characters")
                                    else:
                                        break

                                search_history(user_id, word)

                            elif search_option.upper() == "Q":
                                print()
                                time.sleep(0.65)
                                break

                            else:
                                print("\nError: choose a valid option")
                                time.sleep(0.65)
                    else:
                        print("\nSearch history is empty\n")
                        time.sleep(0.65)

                elif sub_option == "3":
                    delete_user(user_id)
                    break

                elif sub_option.upper() == "Q":
                    time.sleep(0.65)
                    break

                else:
                    print("\nError: choose a valid option\n")
                    time.sleep(0.65)

    elif option == "3":

        while True:

            username, password = signup()

            c.execute("SELECT username FROM users WHERE username=?",
                      (username,))

            if c.fetchone():
                print("\nError: sername already exists - try another")

            else:
                c.execute("INSERT INTO users (username, password) "
                          "VALUES (?, ?)", (username, password))

                conn.commit()
                print("\nAccount created successfully!")
                time.sleep(0.65)
                break

    elif option.lower() == "q":
        break

c.close()
conn.close()
print("\nThank you for using Destination Finder!")
