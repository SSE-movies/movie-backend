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


# ✅ Route: Get movies with pagination
# pagination example: http://127.0.0.1/movies?page=1&per_page=1000
@app.route("/movies", methods=["GET"])
def get_movies():
    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ Get query parameters for pagination
    page = request.args.get("page", default=1, type=int)  # Default to page 1
    per_page = request.args.get(
        "per_page", default=20, type=int
    )  # Default 20 movies per page
    offset = (page - 1) * per_page  # Calculate offset for SQL LIMIT

    # ✅ Fetch paginated results
    cur.execute(
        """
        SELECT "showId", type, title, director, "cast", country, "dateAdded",
                "releaseYear", rating, duration, "listedIn", description
        FROM movies
        LIMIT %s OFFSET %s;
    """,
        (per_page, offset),
    )

    movies = cur.fetchall()

    cur.close()
    conn.close()

    # ✅ Convert query results to JSON format
    movies_list = [
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
        for row in movies
    ]

    return jsonify({"page": page, "per_page": per_page, "movies": movies_list})


# ✅ Run Flask App
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
