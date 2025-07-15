import streamlit as st
import pandas as pd
import time
from helpers.helpers import (
    get_observations,
    process_observations,
    get_profile,
    get_taxonomic_summary,
    get_worms_data
)

st.set_page_config(
    page_title="iNaturalist Observations Dashboard",
    page_icon=":coconut:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("iNaturalist Dashboard")
st.markdown("This streamlit app fetches your iNaturalist observations and enriches them with taxonomic data from WoRMS.")

for i in ["df_obs", "df_profile", "worms_df", "retry_df", "worms_errors", "retry_triggered", "names_to_retry", "name_corrections"]:
    if i not in st.session_state:
        if "df" in i:
            st.session_state[i] = pd.DataFrame()
        elif "errors" in i:
            st.session_state[i] = []
        elif i == "name_corrections":
            st.session_state[i] = {}
        else:
            st.session_state[i] = False

st.header("Fetch iNaturalist Data")
user = st.text_input("Enter your iNaturalist username:")
run = st.button("Fetch Data from iNaturalist")

if run and user:
    profile = get_profile(user)
    if profile and len(profile) > 0:
        df_profile = pd.json_normalize(profile)
        st.session_state.df_profile = df_profile

        name = df_profile['name'].iloc[0]
        login = df_profile['login'].iloc[0]
        observations_count = df_profile['observations_count'].iloc[0]
        user_id = df_profile['id'].iloc[0]
        icon_url = f"https://static.inaturalist.org/attachments/users/icons/{user_id}/original.jpeg"

        st.image(icon_url, width=120)
        st.markdown(f"**{name} (@{login})** — {observations_count} observations")

    observations = get_observations(user)
    if observations:
        df_obs = process_observations(observations)
        st.session_state.df_obs = df_obs

        st.subheader("Observation Preview")
        st.dataframe(df_obs.head(), hide_index=True)

        st.download_button(
            label="Download iNaturalist Data as CSV",
            data=df_obs.to_csv(index=False).encode("utf-8"),
            file_name=f"{user}_observations.csv",
            mime="text/csv"
        )
elif run:
    st.warning("Please enter a valid iNaturalist username.")

st.divider()

st.header("Add taxonomic breakdown from WoRMS")
query = st.button("Query WoRMS")

if query:
    if not st.session_state.df_obs.empty:
        unique_names = st.session_state.df_obs["scientific_name"].dropna().unique()

        with st.spinner("Fetching WoRMS data... This may take several minutes."):
            start = time.time()
            worms_df, worms_errors = get_worms_data(unique_names)
            duration = time.time() - start
            minutes, seconds = divmod(int(duration), 60)

        st.session_state.worms_df = worms_df
        st.session_state.worms_errors = worms_errors

        if not worms_df.empty:
            st.success(f"Successfully retrieved WoRMS data in {minutes}:{seconds:02d} minutes")
            st.dataframe(worms_df.head(8), hide_index=True)
            st.download_button(
                label="Download WoRMS Data as CSV",
                data=worms_df.to_csv(index=False).encode("utf-8"),
                file_name="worms_taxa.csv",
                mime="text/csv"
            )
        else:
            st.warning("No WoRMS data found.")

    else:
        st.warning("Please fetch iNaturalist data first.")

if st.session_state.worms_errors:
    st.error("Some errors occurred while querying WoRMS.")
    failed_names = [e.split(":")[0] for e in st.session_state.worms_errors]

    st.markdown("### Fix Names and Retry")
    default_mapping = "\n".join(f"{name} => {name}" for name in failed_names)
    edited_mappings = st.text_area(
        "Map original names to corrected ones (format: original => corrected):",
        default_mapping,
        key="edit_retry_names"
    )
    fix_btn = st.button("Retry Failed Names")

    if fix_btn:
        name_map = {}
        for line in edited_mappings.strip().splitlines():
            if "=>" in line:
                original, corrected = [s.strip() for s in line.split("=>", 1)]
                name_map[original] = corrected

        st.session_state.name_corrections = name_map

        df_obs = st.session_state.df_obs.copy()
        df_obs["scientific_name"] = df_obs["scientific_name"].replace(name_map)
        st.session_state.df_obs = df_obs

        retry_names = list(name_map.values())
        with st.spinner("Retrying fixed names..."):
            retry_df, retry_errors = get_worms_data(retry_names)

        if not retry_df.empty:
            st.session_state.retry_df = retry_df
            st.session_state.worms_df = pd.concat(
                [st.session_state.worms_df, retry_df],
                ignore_index=True
            )

        st.session_state.worms_errors = retry_errors
        st.session_state.retry_triggered = False

        if not st.session_state.retry_df.empty:
            st.success("Successfully added fixed taxa:")
            st.dataframe(st.session_state.retry_df, hide_index=True)

        if not st.session_state.worms_df.empty:
            st.markdown("### Current Combined WoRMS Dataset")
            st.dataframe(st.session_state.worms_df.head(8), hide_index=True)

            st.download_button(
                "Download Final WoRMS CSV",
                st.session_state.worms_df.to_csv(index=False).encode("utf-8"),
                file_name="worms_taxa.csv",
                mime="text/csv"
            )

st.divider()
st.header("Merge iNaturalist and WoRMS Data")

merge_btn = st.button("Merge Datasets")

if merge_btn:
    if not st.session_state.df_obs.empty and not st.session_state.worms_df.empty:
        merged = pd.merge(
            st.session_state.df_obs,
            st.session_state.worms_df,
            how="left",
            left_on="scientific_name",
            right_on="scientificname"
        )
        st.dataframe(merged.head(8), hide_index=True)

        st.download_button(
            label="Download Merged Data",
            data=merged.to_csv(index=False).encode("utf-8"),
            file_name="merged_inat_worms.csv",
            mime="text/csv"
        )
    else:
        st.warning("Both iNaturalist and WoRMS data must be available before merging.")
