# imports
import requests
import time
import pandas as pd
import json

start_time = time.time()

# read csv 
df_observations = pd.read_csv("./files/raw/inat_observations.csv")

df_observations.replace({
    "Echinaster spinulosus": "Echinaster (Othilia) spinulosus",
    "Eques punctatus": "Equetus punctatus",
    "Holothuria thomasi": "Holothuria (Thymiosycia) thomasi"
}, inplace=True)

df_observations.to_csv('./files/raw/inat_observations.csv', index = False)

# no need for repeated names, use unique() to get distinct values.
request_list = df_observations["scientific_name"].unique().tolist()
request_list.sort()
total = len(request_list)
print(f"There are {total} unique taxon names")

taxa_df = pd.DataFrame(request_list)
taxa_df.to_csv('./files/raw/inat_request_list.csv', index = False, header = False)

# WoRMS API URLs
base_url = "https://www.marinespecies.org/rest"
aphia_record_endpoint = "/AphiaRecordsByName/"

# results list to convert into pd df later
worms = []
# error list to review taxa issues like subgenus
errors = []

def get_aphia_records(scientific_name):
    try:
        response = requests.get(base_url + aphia_record_endpoint + scientific_name)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        errors.append(f"{scientific_name}: {e}")
        return None
    
def get_target_rank(records, target_name):
    target_name = str(target_name).lower().replace("_", " ")
    for record in records:
        scientificname = str(record.get("scientificname") or "").lower()
        status = record.get("status")
        if scientificname == target_name and status in {"accepted", "alternative representation"}:
            return record.get("rank")
    return None

for i in request_list:
    query_name = i.replace("_", " ")
    print(f"Going through {i}")
    
    result = get_aphia_records(query_name)
    if result:
        target_rank = get_target_rank(result, query_name)
        if target_rank:
            filtered_records = [
                record for record in result
                if record.get("status") in {"accepted", "alternative representation"}
                and record.get("rank") == target_rank
                and str(record.get("scientificname") or "").lower() == query_name.lower()
            ]
            worms.extend(filtered_records)

worms = pd.DataFrame(worms)
worms.to_csv('./files/raw/worms_output.csv', index=False)

if errors:
    print("The following errors occurred while fetching data:")
    for err in errors:
        print(f"- {err}")
else:
    print("No errors occurred.")

end_time = time.time()
duration = end_time - start_time 
min = int(duration // 60)
s = int(duration % 60)
print(f"This lasted {min}:{s:02d} minutes")