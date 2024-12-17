# Current state of script
December 16th, 2024:
- After fetching the data from iNaturalist, you can run `worms_request.py` to create a csv with the accepted name by WoRMS as well as other record information 

December 1st, 2024: 
- You can run `inat_request.py` to fetch data from iNaturalist. 
- Then you can run `inat_parse.py` to create a dataframe with data I decided was useful to keep. 
- Currently, I'm trying to use the taxon name from iNaturalist to get Aphia records from WoRMS.
    - Requesting the AphiaID only leads to errors, while the records hold more information like taxonomic breakdown