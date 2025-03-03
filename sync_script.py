import pandas as pd
from dotenv import load_dotenv
import zipfile
import os
from supabase import create_client, Client
import sys
import time


# Helper function to safely convert values to integer
def safe_int(value):
    try:
        # Consider empty strings as missing too.
        return int(value) if value not in (None, '') else None
    except (ValueError, TypeError):
        return None


# Load environment variables
load_dotenv()

# Validate required environment variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    sys.exit(
        """
        Error: SUPABASE_URL and/or SUPABASE_KEY
        environment variables are missing.
        """
    )

# Unzip the CSV file if it's not already extracted
zip_path = 'netflix_titles.csv.zip'
csv_filename = 'netflix_titles.csv'

if not os.path.exists(csv_filename):
    if not os.path.exists(zip_path):
        sys.exit(f"Error: Neither {csv_filename} nor {zip_path} were found.")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')  # extracts all files into current dir
    except zipfile.BadZipFile:
        sys.exit("Error: The zip file is corrupted or not a zip file.")

# Connect to Supabase
supabase: Client = create_client(url, key)

# Read the CSV file safely
try:
    df = pd.read_csv(csv_filename)
except Exception as e:
    sys.exit(f"Error reading CSV file: {e}")

# Replace missing values with None
df = df.where(pd.notnull(df), None)

# Get existing titles from Supabase, with safe fallback if no data returned
existing_titles = set()
page = 0
page_size = 1000

while True:
    start = page * page_size
    end = start + page_size - 1
    response = (supabase.table("movies")
                .select("title")
                .range(start, end)
                .execute())
    data = response.data or []
    if not data:
        break
    for row in data:
        if title := row.get("title"):
            existing_titles.add(title.strip().lower())
    page += 1

# Normalize the CSV titles safely (only strip if the value is a string)
df["normalised_title"] = df["title"].apply(
    lambda x: x.strip().lower() if isinstance(x, str) else None
)

# Filter to new entries that are not already in Supabase
new_entries = df[~df["normalised_title"].isin(existing_titles)]

# Prepare records for insertion with safe conversion for nums & missing fields
records_to_insert = []
for _, row in new_entries.iterrows():
    record = {
        "type": row.get("type"),
        "title": row.get("title"),
        "director": row.get("director"),
        "cast": row.get("cast"),
        "country": row.get("country"),
        "dateAdded": row.get("date_added"),
        "releaseYear": safe_int(row.get("release_year")),
        "duration": row.get("duration"),
        "listedIn": row.get("listed_in"),
        "description": row.get("description"),
        "rating": row.get("rating")
    }
    records_to_insert.append(record)

# Insert new records in batches (handling potential insertion errors)
batch_size = 1000
max_retries = 5
total_inserted = 0

for i in range(0, len(records_to_insert), batch_size):
    batch = records_to_insert[i: i + batch_size]
    attempt = 0
    while attempt < max_retries:
        try:
            supabase.table("movies").insert(batch).execute()
            total_inserted += len(batch)
            print(f"Successfully inserted batch starting at index {i}")
            break  # exit the retry loop if the insert is successful
        except Exception as e:
            attempt += 1
            print(
                f"""Error inserting batch starting at index {i},
                attempt {attempt}: {e}""")
            # Wait a bit longer on each retry (exponential backoff)
            time.sleep(2 ** attempt)
    else:
        # This block executes if we did not break out of the while loop
        print(
            f"""Failed to insert batch starting at index {i}
            after {max_retries} attempts.""")

print(f"Inserted {total_inserted} new rows into 'movies'.")