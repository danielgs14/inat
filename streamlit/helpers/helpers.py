# helpers.py

import streamlit as st
import pandas as pd
import requests

# --- iNaturalist ---
base_inat_url = "https://api.inaturalist.org/v1"

def get_data(endpoint, params={}):
    url = f"{base_inat_url}/{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting {endpoint}: {e}")
        return None

def get_all_pages(endpoint, base_params={}):
    all_results = []
    page = 1
    while True:
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
    return all_results

@st.cache_data(show_spinner=False)
def get_observations(user):
    with st.spinner("Getting observations..."):
        params = {"user_id": user}
        return get_all_pages("observations", params)

@st.cache_data(show_spinner=False)
def get_profile(user):
    with st.spinner("Getting user profile..."):
        params = {"q": user}
        data = get_data("users/autocomplete", params)
        return data.get("results", []) if data else []

def process_observations(observations):
    fields = [
        "id", "observed_on", "time_observed_at", "species_guess", "taxon.name", "taxon.rank",
        "taxon.id", "geojson.coordinates", "place_guess", "location", "quality_grade", "user.login"
    ]
    rename_map = {
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
    df = pd.json_normalize(observations)
    fields = [f for f in fields if f in df.columns]
    df = df[fields].rename(columns=rename_map)
    return df

def get_taxonomic_summary(df):
    eda_columns = ['phylum', 'class', 'order', 'family', 'genus', 'scientific_name', 'rank']
    eda_dfs = {}
    for col in eda_columns:
        if col in df.columns:
            total = df[col].dropna().shape[0]
            value_counts = df[col].value_counts(dropna=True)
            percentages = (value_counts / total * 100).round(2)
            summary_df = pd.DataFrame({
                col: value_counts.index,
                'count': value_counts.values,
                'percentage': percentages.values
            })
            eda_dfs[col] = summary_df
    return eda_dfs


# --- WoRMS ---

base_worms_url = "https://www.marinespecies.org/rest"
aphia_record_endpoint = "/AphiaRecordsByName/"

@st.cache_data(show_spinner=False)
def get_worms_data(scientific_names):
    worms = []
    errors = []

    def get_aphia_records(scientific_name):
        try:
            response = requests.get(base_worms_url + aphia_record_endpoint + scientific_name)
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
            if scientificname == target_name and status in {"accepted", "alternative representation", "unaccepted"}:
                return record.get("rank")
        return None

    for name in scientific_names:
        query_name = name.replace("_", " ")
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

    worms_df = pd.DataFrame(worms)
    return worms_df, errors