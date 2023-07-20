import requests
import config
import time

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
            print("Error: location not found\n- please enter a valid location")
        else:
            print("Error: multiple locations or invalid location found\n- please check for mispellings or provide a more specific location")
    else:
        print("Error", str(status_code) + ":", data["status"]["message"])

    return None

def get_destinations(latitude, longitude, categories_str):
    
        url = "https://api.foursquare.com/v3/places/search"

        header = {"accept": "application/json", "Authorization": config.key2}
        param_dict = {"ll": str(latitude) + "," + str(longitude), "sort": "DISTANCE", "radius": 5000, "categories": categories_str}

        response = requests.get(url, params = param_dict, headers = header)
        data = response.json()

        if response.status_code == 200:
            display_locations(data["results"])
        else:
            print(data["message"])

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

print("Destination Finder")
print("+-+-+-+-+-+-+-+-+-\n")

print("This destination finder will show tourist destinations in your chosen area")
print("For best results, enter zipcode or postcode followed by country name")
print("Example: 12345 United States of America\n")

time.sleep(0.65)

while True:

    query = input("Enter location: ")

    try:
        categories_str = choose_categories()
        latitude, longitude = get_coordinates(query)
        get_destinations(latitude, longitude, categories_str)
        if quit_option():
            break
    except TypeError:
        if quit_option():
            break

print("\nThank you for using Destination Finder!")
