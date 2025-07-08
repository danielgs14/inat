import pandas as pd

df_obs = pd.read_csv("./files/raw/inat_observations.csv")
df_tax = pd.read_csv("./files/raw/worms_output.csv")

df_tax.rename(columns={"scientificname": "scientific_name"}, inplace=True)

df_merged = pd.merge(
    df_obs,
    df_tax[["scientific_name", "kingdom", "phylum", "class", "order", "family", "genus"]],
    on="scientific_name",
    how="left"
)

cols = [col for col in df_merged.columns if col not in ["scientific_name", "rank"]]
cols += ["scientific_name", "rank"]
df_merged = df_merged[cols]

df_merged.to_csv("./files/tidy/analytics.csv", index=False)
print("Merged dataset saved to analytics.csv")

