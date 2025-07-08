# imports
import requests 
import json  
import pandas as pd
import os 

# iNaturalist API URLs
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
    
# get all data 
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

# # store json
# def to_json(data, filename):
#     try:
#         file_path = os.path.join("..", "files", "raw", filename)
#         os.makedirs(os.path.dirname(file_path), exist_ok=True)
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, ensure_ascii=False, indent=4)
#     except Exception as e:
#         print(f"Error saving to {file_path}: {e}")

# store csv
def to_csv(data, filename, fields=None, rename_map=None):
    try:
        file_path = os.path.join("files", "raw", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df = pd.json_normalize(data)
        if fields:
            missing = [f for f in fields if f not in df.columns]
            if missing:
                print(f"Warning: Skipping missing fields: {missing}")
            fields_in_df = [f for f in fields if f in df.columns]
            df = df[fields_in_df]
        if rename_map:
            df = df.rename(columns=rename_map)
        df.to_csv(file_path, index=False, encoding="utf-8")
        print(f"Saved CSV to {file_path}")
    except Exception as e:
        print(f"Error saving CSV to {file_path}: {e}")

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
    observations = get_observations(user)
    if observations:
        obs_fields = [
            "id",
            "observed_on",
            "time_observed_at",
            "species_guess",
            "taxon.name",
            "taxon.rank",
            "taxon.id",
            "geojson.coordinates",
            "place_guess",
            "location",
            "quality_grade",
            "user.login"
        ]
        obs_rename = {
            "id": "observation_id",
            "observed_on": "date",
            "time_observed_at": "time",
            "species_guess": "species_guess",
            "taxon.name": "scientific_name",
            "taxon.rank": "rank",
            "taxon.id": "taxon_id",
            "geojson.coordinates": "coordinates",
            "place_guess": "place",
            "location": "lat_lon",
            "quality_grade": "grade",
            "user.login": "user"
        }
        to_csv(observations, "inat_observations.csv", fields=obs_fields, rename_map=obs_rename)

    # identifications = get_ids(user)
    # if identifications:
    #     ids_fields = [
    #         "id",
    #         "created_at",
    #         "taxon.name",
    #         "taxon.rank",
    #         "observation.id",
    #         "observation.species_guess",
    #         "observation.place_guess",
    #         "user.login"
    #     ]
    #     ids_rename = {
    #         "id": "identification_id",
    #         "created_at": "timestamp",
    #         "taxon.name": "scientific_name",
    #         "taxon.rank": "rank",
    #         "observation.id": "observation_id",
    #         "observation.species_guess": "species_guess",
    #         "observation.place_guess": "place",
    #         "user.login": "user"
    #     }
    #     to_csv(identifications, "inat_identifications.csv", fields=ids_fields, rename_map=ids_rename)

    user_profile = get_profile(user)
    if user_profile:
        profile_fields = [
            "id",
            "login",
            "name",
            "created_at",
            "observations_count",
            "identifications_count"
        ]
        profile_rename = {
            "id": "user_id",
            "login": "username",
            "name": "full_name",
            "created_at": "joined",
            "observations_count": "total_observations",
            "identifications_count": "total_identifications"
        }
        to_csv(user_profile, "inat_user_profile.csv", fields=profile_fields, rename_map=profile_rename)

if __name__ == "__main__":
    main()