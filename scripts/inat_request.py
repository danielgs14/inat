# This script will request the data through the iNaturalist API and store it as JSON files
# Once you get the JSON files, pandas can be used to manipulate dataframes for visualizations

# start with imports
import requests # talk to API from iNaturalist
import json # used here for a prettier output 
import os # navitating through directories

# add url
base_url = "https://api.inaturalist.org/v1"

# add iNaturalist user
user = "[your_user]"

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
# required as without pagination, you can get a max of 200 results
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
    print(f"Retrieved {len(all_results)} total results from {endpoint}.")
    return all_results

# store json
def to_json(data, filename):
    try:
        file_path = os.path.join(".", "files", "raw", filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)  # Pretty-print JSON
        print(f"Data saved to {file_path}")

    except Exception as e:
        print(f"Error saving to {file_path}: {e}")

# get observations
def get_observations(user):
    print("Getting all observations...")
    params = {"user_id": user}
    return get_all_pages("observations", params)

# get ids
def get_ids(user):
    print("Getting all identifications...")
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
    # Observations
    observations = get_observations(user)
    if observations:
        print(f"Retrieved {len(observations)} observations.")
        to_json(observations, "inat_observations.json")

    # Identifications
    identifications = get_ids(user)
    if identifications:
        print(f"Retrieved {len(identifications)} identifications.")
        to_json(identifications, "inat_identifications.json")

    # User Profile
    user_profile = get_profile(user)
    if user_profile:
        print("Retrieved user profile.")
        to_json([user_profile], "inat_profile.json")

if __name__ == "__main__":
    main()