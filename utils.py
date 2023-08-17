from database import save_history  # function from database.py
import requests  # for AIP requests
import config  # contains API keys

# checks validity of user queries
def enter_query(query):
    try:
        if len(query) < 2:
            # returns error message to user if the query is less than 2 characters
            return None, "Error: query is too short (2+ characters needed)"
        else:
            # returns query if it is 2 characters or longer
            return query, None
    except ValueError:
        # except message handles any unknown errors in the query input process
        return None, "Error: invalid query"

# generates set of checkboxes that user can select to refine their search choices
def generate_checkboxes():
    # dictionary containing key FourSquare categories with respective IDs, utilised in API call
    categories = {
        "Arts and Entertainment": 10000,
        "Community": 12000,
        "Dining and Drinking": 13000,
        "Events": 14000,
        "Landmarks and Outdoors": 16000,
        "Retail": 17000,
        "Sports": 18000,
        "Travel and Transportation": 19000,
    }

    # string to store all categories in categories, and counter for checkbox IDs and labels
    checkboxes = ""
    counter = 0

    # iterate through categories to generate HTML checkboxes from all categories, including divs, classes and ids for CSS, and accompanying label
    for name, id in categories.items():
        checkbox_str = f'<div class="form-check">'
        checkbox_str += f'<input type="checkbox" class="form-check-input" name="categories" value="{id}" id="checkbox_{counter}">'
        checkbox_str += f'<label class="form-check-label" for="checkbox_{counter}">{name}</label>'
        checkbox_str += '</div>'

        checkboxes += checkbox_str

        counter += 1

    # jinja in HTML will work with the checkboxes string to display individual checkboxes
    return checkboxes

# generates set of radius buttons that user can select to select their radius choices
def generate_radio_buttons():
    # list of radiuses, providing radius options the user can store
    values = [500, 1000, 2500, 5000, 10000]

    radius_buttons = ""  # string to store all radio buttons in values

    # iterate through values to generate HTML radio buttons from all values, including divs, classes and ids for CSS, and accompanying label
    for value in values:
        button_str = f'<div class="form-group">'
        button_str += f'<div class="form-check">'
        button_str += f'<input class="form-check-input" type="radio" name="radius" value="{value}" id="radius-{value}">'
        button_str += f'<label class="form-check-label" for="radius-{value}">{value}</label>'
        button_str += '</div>'
        button_str += '</div>'

        radius_buttons += button_str

    # jinja in HTML will work with the radius_buttons string to display individual checkboxes
    return radius_buttons

# utilises OpenCage API to retrieve valid latitude and longitude values for a user input location, returning error messages for invalid locations
def get_coordinates(search):
    try:
        # constructing URL for API call, including base URL with query from enter_query(query) and API key from config
        base_url = "https://api.opencagedata.com/geocode/v1/json"
        url = base_url + "?q=" + search + "&key=" + config.key1

        # executing GET request to OpenCage API
        response = requests.get(url)

        # parsing JSON response from API call and obtaining the status code
        data = response.json()
        status_code = int(data["status"]["code"])

        # status code 200 indicates a successful request
        if status_code == 200:

            # checking if a latitude and longitude value are in the JSON response, returning the latitude and longitude values
            if data["total_results"] == 1:
                result = data["results"][0]
                latitude = result["geometry"]["lat"]
                longitude = result["geometry"]["lng"]
                return latitude, longitude, None

            # error message for if latitude and longitude values were not in the JSON response (potential output for typos)
            elif data["total_results"] == 0:
                return None, None, "Error: location not found - please use a valid location"

            # error message if multiple latitude and longitude values were found in the JSON response (potential output for a non-specific input returning multiple latitudes and longitudes)
            else:
                return None, None, "Error: multiple locations or invalid location found - check for misspellings or provide a more specific location"

        # error message if the status code is not 200, concatenating API error message with status code
        else:
            return None, None, f"Error {status_code}: {data['status']['message']}"

    # except block error message for unknown cases of error
    except requests.exceptions.ConnectionError:
        return "Error: connection failure - check your internet connection"
    except Exception:
        return "Error: failed to retrieve destinations"


# utilises FourSquare API to retrieve list of valid location results, and saves results to user's search history if they are logged in
# parameters include latitude and longitude values returned from get_coordinates(), categories and radius from search.js form input, and the user's id and the database session to save results to history
def get_destinations(latitude, longitude, categories, radius, user_id, db_session):
    try:

        # base URL for FourSquare API
        url = "https://api.foursquare.com/v3/places/search"

        # header containing authorisation details, including API key from config file
        header = {"accept": "application/json", "Authorization": config.key2}

        # dictionary of parameters including latitude and longitude in a string value per FourSquare API documentation, DISTANCE to sort the results by nearest distance to input location, integer radius value, and categories in a string
        param_dict = {"ll": f"{latitude},{longitude}",
                      "sort": "DISTANCE",
                      "radius": radius,
                      "categories": categories}

        # executing GET request to FourSquare API with URL, parameters and header
        response = requests.get(url, params=param_dict, headers=header)

        # parsing JSON response from API call
        data = response.json()

        # status 200 code indicates a successful request
        if response.status_code == 200:

            # list to store valid results from the respinse
            filtered_results = []

            # checking if each location has a formatted address, useful to the user, and appends it to filtered_results
            if "results" in data:
                for result in data["results"]:
                    if "formatted_address" in result.get("location", {}):
                        filtered_results.append(result)

            # saves search histroy with save_history() from database.py if the user_id is provided (if not, it is a None value)
            if user_id is not None:
                save_history(db_session, user_id, filtered_results)

            # if filtered_results list is not empty and has results, the list is returned
            if len(filtered_results) > 0:
                return filtered_results
            # return a message if filtered_lists results is empty, indicating that no valid locations were found
            else:
                return "No valid locations found for this area"

        # return API error message if the status code is not 200
        else:
            return f"Error: {data['message']}"

    # except block error message for unknown cases of error
    except requests.exceptions.ConnectionError:
        return "Error: connection failure - check your internet connection"
    except Exception:
        return "Error: failed to retrieve destinations"
