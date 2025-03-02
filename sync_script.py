import pandas as pd
import os
from supabase import create_client, Client

# 1. Connect to Supabase
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Read the CSV
df = pd.read_csv('netflix_titles.csv')

# 3. Get existing IDs from Supabase
existing_ids_data = supabase.table("movies").select("showId").execute()
existing_ids = {row["showId"] for row in existing_ids_data.data}

# 4. Filter to new entries
new_entries = df[~df["show_id"].isin(existing_ids)]

# 5. Prepare records for insertion
records_to_insert = []
for _, row in new_entries.iterrows():
    records_to_insert.append({
        "showId": row["show_id"],
        "type": row["type"],
        "title": row["title"],
        "director": row["director"],
        "cast": row["cast"],
        "country": row["country"],
        "dateAdded": row["date_added"],
        "releaseYear": int(row["release_year"]),
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
