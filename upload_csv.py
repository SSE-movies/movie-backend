import psycopg2
import pandas as pd
import os

# Get PostgreSQL connection URL from Railway
DATABASE_URL = os.getenv("DATABASE_URL")  # Make sure to set this in your terminal

# Connect to the PostgreSQL database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Read CSV file
df = pd.read_csv("netflix_titles.csv")

# Replace NaN values with None for PostgreSQL compatibility
df = df.where(pd.notnull(df), None)

# Insert data into the movies table
for row in df.itertuples(index=False, name=None):  # Convert DataFrame row to tuple
    print(f"Inserting row: {row}")  # Debugging: See what is actually being inserted
    cur.execute("""
        INSERT INTO movies (show_id, type, title, director, "cast", country, date_added, release_year, rating, duration, listed_in, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (show_id) DO NOTHING;
    """, row)
#print(df.columns)



# Commit changes and close connection
conn.commit()
cur.close()
conn.close()

print("✅ Data uploaded successfully!")
