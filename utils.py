from database import save_search_history
import requests
import config

def enter_query(query):
    try:
        if len(query) < 2:
            return None, "Error: query is too short (2+ characters needed)"
        return query, None
    except ValueError:
        return None, "Error: invalid query"

def generate_checkboxes():
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

    checkboxes = ""

    counter = 0

    for name, id in categories_dict.items():
        checkbox_str = f'<div class="form-check">'
        checkbox_str += f'<input type="checkbox" class="form-check-input" name="categories" value="{id}" id="checkbox_{counter}">'
        checkbox_str += f'<label class="form-check-label" for="checkbox_{counter}">{name}</label>'
        checkbox_str += '</div>'

        checkboxes += checkbox_str

        counter += 1

    return checkboxes

def generate_radio_buttons():
    values = [500, 1000, 2500, 5000, 10000]

    radius_buttons = ""

    for value in values:
        button_str = f'<div class="form-group">'
        button_str += f'<div class="form-check">'
        button_str += f'<input class="form-check-input" type="radio" name="radius" value="{value}" id="radius-{value}">'
        button_str += f'<label class="form-check-label" for="radius-{value}">{value}</label>'
        button_str += '</div>'
        button_str += '</div>'

        radius_buttons += button_str

    return radius_buttons


def get_coordinates(search):
    try:
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
                return latitude, longitude, None
            elif data["total_results"] == 0:
                return None, None, "Error: location not found - please use a valid location"
            else:
                return None, None, "Error: multiple locations or invalid location found - check for misspellings or provide a more specific location"
        else:
            return None, None, f"Error {status_code}: {data['status']['message']}"
    except requests.exceptions.RequestException:
        return None, None, "Error: failed to retrieve coordinates"

def get_destinations(latitude, longitude, categories_str, radius, user_id, db_session):
    try:
        url = "https://api.foursquare.com/v3/places/search"
        header = {"accept": "application/json", "Authorization": config.key2}
        param_dict = {"ll": f"{latitude},{longitude}",
                      "sort": "DISTANCE",
                      "radius": radius,
                      "categories": categories_str}
        response = requests.get(url, params=param_dict, headers=header)
        data = response.json()

        filtered_results = []
        if "results" in data:
            filtered_results = data["results"]

        if user_id is not None:
            save_search_history(db_session, user_id, filtered_results)

        if response.status_code == 200:
            return filtered_results
        else:
            return f"Error: {data['message']}"
    except requests.exceptions.RequestException:
        return "Error: failed to retrieve destinations"
