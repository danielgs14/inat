# This script will request the data through the iNaturalist API and store it as JSON files

# start with imports
import requests
import pandas as pd
import json
import os

# add url
base_url = "https://api.inaturalist.org/v1"

# add iNaturalist user
user = "d_gonzalez"

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
    
# store json
def to_json(data, filename):
    try:
        # # Ensure the directory exists
        # os.makedirs(os.path.join("..", "files", "raw"), exist_ok=True)
        file_path = os.path.join(".", "files", "raw", filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")

# get observations
def get_observations(user):
    print("Getting my observations...")
    params = {"user_id": user, 
              "per_page": 30}
    data = get_data("observations", params)
    return data.get("results", []) if data else []

# get ids
def get_ids(user):
    print("Getting my ids...")
    params = {"user_id": user, 
              "per_page": 30}
    data = get_data("identifications", params)
    return data.get("results", []) if data else []

#get profile
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
        to_json(observations, "observations.json")

    # Identifications
    identifications = get_ids(user)
    if identifications:
        print(f"Retrieved {len(identifications)} identifications.")
        to_json(identifications, "identifications.json")

    # User Profile
    user_profile = get_profile(user)
    if user_profile:
        print("Retrieved user profile.")
        to_json([user_profile], "user_profile.json")

if __name__ == "__main__":
    main()