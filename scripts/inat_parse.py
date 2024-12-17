import pandas as pd
import json 
import os
import time

# read files
start_time = time.time()
with open("./files/raw/inat_observations.json", "r", encoding = "utf-8") as f:
    observations = json.load(f)
print(f"Opening JSON file to read")
df_observations = pd.json_normalize(observations)
print(f"Normalizing JSON with pandas")
# subset of columns I wanted to keep out of the 499 the request returns
df_observations = df_observations[
    ["quality_grade"
    , "observed_on"
    , "identifications_most_agree"
    , "num_identification_agreements"
    , "community_taxon_id"
    , "location"
    , "taxon.name"]
    ]
print(f"Subsetting columns")
# some data cleaning
# add underscore to scientific names between genus and species epithet
df_observations['taxon.name'] = df_observations['taxon.name']

# fix location
df_observations[['lat', 'lon']] = df_observations['location'].str.split(',', expand=True)
df_observations = df_observations.drop(columns = ['location'])

# store as csv
df_observations.to_csv("./files/tidy/inat_observations.csv", index = False)
print(f"Check files/tidy folder for inat_observations.csv")

end_time = time.time()

# benchmark
duration = end_time - start_time 

print(f"This script lasted {duration:.2f} seconds, I just added this to know it did something.")