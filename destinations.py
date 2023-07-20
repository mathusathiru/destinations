import requests
import config
import time
import sys

def quit_option():
    time.sleep(0.65)
    option = input("Enter any key to continue or 'Q' to quit: ")
    if option.lower() == "q":
        sys.exit("Program closed.")
    else:
        print()

print("Destination Finder")
print("+-+-+-+-+-+-+-+-+-\n")

print("This destination finder will show tourist destinations in your chosen area")
print("For best results, enter zipcode or postcode followed by country name")
print("Example: 12345 United States of America\n")
time.sleep(0.65)

while True:

    query = input("Enter location: ")

    base_url = "https://api.opencagedata.com/geocode/v1/json"
    url = base_url + "?q=" + query + "&key=" + config.key1

    response = requests.get(url)
    data = response.json()

    if data["status"]["code"] == 200:
        if data["total_results"] == 1:
            break
        elif data["total_results"] == 0:
            print("Error: location not found\n- please enter a valid location")
            quit_option()
        else:
            print("Error: multiple locations or invalid location found\n- please check for mispellings or provide a more specific location")
            quit_option()
    else:
        print("Error:", data["status"]["message"])
        quit_option()

result = data["results"][0]
longitude = result["geometry"]["lat"]
latitude = result["geometry"]["lng"]

print(longitude, latitude)

