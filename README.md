# iNaturalist dashboard

A (in progress) dashboard created by leveraging the [iNaturalist API](https://api.inaturalist.org/v1/docs/) to extract my own user information and visualize it. There is already a way to extract data from iNaturalist using their own [export tool](https://www.inaturalist.org/observations/export) but I wanted to explore their API functionalities. This project leverages the APIs from both iNaturalist as well as from [World Register of Marine Species (WoRMS)](https://www.marinespecies.org/aphia.php?p=webservice). It will focus on marine taxa and, in my case, specifically extant

# The project:

First, I created a script that requests data through the [iNaturalist API](https://api.inaturalist.org/v1/docs/). Then it stores it in three separate files:
- [Observations](https://api.inaturalist.org/v1/docs/#!/Observations): Data you have uploaded about species occurrences.  
- [Identifications](https://api.inaturalist.org/v1/docs/#!/Identifications): your interactions with posts in which you have identified a taxon.
- [Profile](https://api.inaturalist.org/v1/docs/#!/Users/get_users_autocomplete): Information about the profile like username, name, counts and else. 

The JSON files available here in this repository contain my own observations, identifications and user profile. There is no sensitive information and it should all be available in iNaturalist. In other cases, I would hide this but it may be helpful for previewing the data so I am keeping it here.  

<br>

# Next steps:
- Take a species name or taxon ID from the returned files from the ``request.py`` script and match it to the AphiaID (a unique identifier for every taxon) from [WoRMS](https://www.marinespecies.org/aphia.php?p=webservice).
    - Create a dataset with taxonomic breakdown (phylum, class, order...) from WoRMS using my observations. Not all observations are identified down to species - some are even identified to phylum. 
    - Filter datasets (for example, for "[Research Grade](https://help.inaturalist.org/en/support/solutions/articles/151000169936-what-is-the-data-quality-assessment-and-how-do-observations-qualify-to-become-research-grade-)" quality observations) to visualize different information. 
        - How many of my observations have Research Grade quality? (Research Grade, Needs ID, Total)
        - How different would a list of my most observed species would look like by filtering data based on this? 
- Create visualizations leveraging [seaborn](https://seaborn.pydata.org/) and [matplotlib](https://matplotlib.org/) 
- Create a [streamlit](https://streamlit.io/) app to visualize the data and create the dashboard. 
- Make it reproducible for other users