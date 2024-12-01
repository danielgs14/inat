# Current state of script
December 1st, 2024: 
- You can run inat_request.py to fetch data from iNaturalist. 
- Then you can run inat_parse.py to create a dataframe with data I decided was useful to keep. 
- Currently, I'm trying to use the taxon name from iNaturalist to get Aphia records from WoRMS.
    - Requesting the AphiaID only leads to errors and the records hold more information

# Challenges 
When requesting the Aphia records from WoRMS, I get multiple (up to 49 in some cases) records due to:
- Multiple authorships
- Subspecies
- Genus records also fetch direct taxa so all direct child species are recorded
    - The output I am getting from **get_aphia_records(scientific_name)**, found in tests/worms_functions_request_test.ipynb, is a dataframe with 49 columns and many rows, each column being a record and each row being the scientific name provided. 
    - A possible solution **for some cases** (like *Aplysia* or Terebellidae which have multiple records) is to filter status for only accepted values.
    - For other cases (like Echinacea and Ctenophora), filtering for kingdom = Animalia might also do the trick