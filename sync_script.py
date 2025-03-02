import pandas as pd
from dotenv import load_dotenv
import zipfile
import os
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Unzip the CSV file if it's not already extracted
zip_path = 'netflix_titles.csv.zip'
csv_filename = 'netflix_titles.csv'
if not os.path.exists(csv_filename):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('.')  # extracts all files into current directory

# Connect to Supabase
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Read the CSV
df = pd.read_csv('netflix_titles.csv')
df = df.where(pd.notnull(df), None)

# Get existing titles from Supabase
existing_titles_data = supabase.table("movies").select("title").range(0, 10000).execute()
existing_titles = {
    row["title"].strip().lower()
    for row in existing_titles_data.data if row["title"]
}

# Normalize the CSV titles as well
df["normalised_title"] = df["title"].apply(
    lambda x: x.strip().lower() if x else x
)

# 4. Filter to new entries
new_entries = df[~df["normalised_title"].isin(existing_titles)]

# 5. Prepare records for insertion
records_to_insert = []
for _, row in new_entries.iterrows():
    records_to_insert.append({
        "type": row["type"],
        "title": row["title"],
        "director": row["director"],
        "cast": row["cast"],
        "country": row["country"],
        "dateAdded": row["date_added"],
        "releaseYear": None if row["release_year"] is None
        else int(row["release_year"]),
        "duration": row["duration"],
        "listedIn": row["listed_in"],
        "description": row["description"],
        "rating": row["rating"]
    })

# 6. Insert new records (in batches if needed)
batch_size = 1000
for i in range(0, len(records_to_insert), batch_size):
    batch = records_to_insert[i: i + batch_size]
    supabase.table("movies").insert(batch).execute()

print(f"Inserted {len(records_to_insert)} new rows into 'movies'.")
