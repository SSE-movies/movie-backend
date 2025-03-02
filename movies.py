from flask import Flask, jsonify, request
from dotenv import load_dotenv
import psycopg2
import os

app = Flask(__name__)
load_dotenv()

# Connect to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Creates a new database connection"""
    return psycopg2.connect(DATABASE_URL)


@app.route("/")
def home():
    return "Movie API is running!"


# Route: Get movies with pagination
# pagination example: http://127.0.0.1/movies?page=1&per_page=1000
@app.route("/movies", methods=["GET"])
def get_movies():
    """
    GET /movies

    Supports optional query parameters:
      - page (int): default=1
      - per_page (int): default=10
      - title (str): partial match on title (case-insensitive)
      - type (str): exact match on the 'type' column
      - categories (str): comma-separated list, each substring is matched in
                            'listedIn'
      - release_year (int): exact match on 'releaseYear'

    Example usage:
      GET /movies?
      page=1&per_page=10&title=Inception&type=Movie&categories=Action,
      Adventure&release_year=2010
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Get query parameters for pagination
    page = request.args.get("page", default=1, type=int)  # Default to page 1
    per_page = request.args.get(
        "per_page", default=10, type=int
    )  # Default 20 movies per page
    offset = (page - 1) * per_page  # Calculate offset for SQL LIMIT

    # Additional filters
    title = request.args.get("title", default=None, type=str)
    media_type = request.args.get("type", default=None, type=str)
    categories_str = request.args.get("categories", default=None, type=str)
    release_year = request.args.get("release_year", default=None, type=int)

    # Debug to be deleted
    print(
        "DEBUG: title=",
        title,
        " media_type=",
        media_type,
        " categories=",
        categories_str,
        " release_year=",
        release_year,
    )

    # Start building SQL
    base_sql = """
        SELECT "showId", type, title, director, "cast", country,
               "dateAdded", "releaseYear", rating, duration,
               "listedIn", description
        FROM movies
    """

    where_clauses = []
    params = []

    # Build WHERE clauses
    if title:
        where_clauses.append("title ILIKE %s")
        params.append(f"%{title}%")

    # Type: both uppercase and lowercase letters match
    if media_type:
        where_clauses.append("LOWER(type) = LOWER(%s)")
        params.append(media_type)

    # Categories: “Action & Adventure, Documentary”
    # → find each substring in "listedIn"
    # We require that *each* category appear as a substring in 'listedIn'
    # (Join them with AND)
    if categories_str:
        for cat in categories_str.split(","):
            cat = cat.strip()
            if cat:  # only apply if non-empty
                where_clauses.append('"listedIn" ILIKE %s')
                params.append(f"%{cat}%")

    # Release year: exact match on the integer column
    if release_year:
        where_clauses.append('"releaseYear" = %s')
        params.append(release_year)

    # Combine WHERE clauses with AND
    if where_clauses:
        base_sql += " WHERE " + " AND ".join(where_clauses)

    # Finally, add pagination
    base_sql += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    # Execute query
    cur.execute(base_sql, tuple(params))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert query results to JSON format
    movies_list = []
    for row in rows:
        movies_list.append(
            {
                "showId": row[0],
                "type": row[1],
                "title": row[2],
                "director": row[3],
                "cast": row[4],
                "country": row[5],
                "date_added": row[6],
                "releaseYear": row[7],
                "rating": row[8],
                "duration": row[9],
                "listedIn": row[10],
                "description": row[11],
            }
        )

    return jsonify({"page": page, "per_page": per_page, "movies": movies_list})


# Run Flask App
if __name__ == "__main__":
    port = int(os.getenv("PORT", 80))
    app.run(host="0.0.0.0", port=port)
