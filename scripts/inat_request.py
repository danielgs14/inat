# imports
import requests 
import json 
import os 

# add url
base_url = "https://api.inaturalist.org/v1"

# add iNaturalist user
user = "[your_username]"

# define request function
def get_data(endpoint, params={}):
    url = f"{base_url}/{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting {endpoint}: {e}")
        return None
    
# get all data from all pages 
# required as you can get a max of 200 results without pagination 

def get_all_pages(endpoint, base_params={}):
    all_results = []
    page = 1
    while True:
        print(f"Getting page {page} of {endpoint}...")
        params = {**base_params, "page": page, "per_page": 200}
        data = get_data(endpoint, params)
        if data and "results" in data:
            results = data["results"]
            all_results.extend(results)
            if len(results) < 200:
                break
            page += 1
        else:
            break
    print(f"Got {len(all_results)} total results from {endpoint}.")
    return all_results

# store json
def to_json(data, filename):
    try:
        file_path = os.path.join(".", "files", "raw", filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")

# get observations
def get_observations(user):
    print("Getting observations...")
    params = {"user_id": user}
    return get_all_pages("observations", params)

# get ids
def get_ids(user):
    print("Getting identifications...")
    params = {"user_id": user}
    return get_all_pages("identifications", params)

# get profile
def get_profile(user):
    print("Getting your profile...")
    params = {"q": user}
    data = get_data("users/autocomplete", params)
    return data.get("results", []) if data else []

# main function to bring you your data
def main():
    observations = get_observations(user)
    if observations:
        to_json(observations, "observations.json")
    identifications = get_ids(user)
    if identifications:
        to_json(identifications, "identifications.json")
    user_profile = get_profile(user)
    if user_profile:
        to_json([user_profile], "user_profile.json")

if __name__ == "__main__":
    main()