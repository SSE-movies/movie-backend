from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

# Connect to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Creates a new database connection"""
    return psycopg2.connect(DATABASE_URL)

# ✅ Route: Get movies with pagination
@app.route("/movies", methods=["GET"])
def get_movies():
    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ Get query parameters for pagination
    page = request.args.get("page", default=1, type=int)  # Default to page 1
    per_page = request.args.get("per_page", default=20, type=int)  # Default 20 movies per page
    offset = (page - 1) * per_page  # Calculate offset for SQL LIMIT

    # ✅ Fetch paginated results
    cur.execute('''
        SELECT show_id, type, title, director, "cast", country, date_added, release_year, rating, duration, listed_in, description 
        FROM movies
        LIMIT %s OFFSET %s;
    ''', (per_page, offset))

    movies = cur.fetchall()

    cur.close()
    conn.close()

    # ✅ Convert query results to JSON format
    movies_list = [
        {
            "show_id": row[0],
            "type": row[1],
            "title": row[2],
            "director": row[3],
            "cast": row[4],
            "country": row[5],
            "date_added": row[6],
            "release_year": row[7],
            "rating": row[8],
            "duration": row[9],
            "listed_in": row[10],
            "description": row[11],
        }
        for row in movies
    ]

    return jsonify({
        "page": page,
        "per_page": per_page,
        "movies": movies_list
    })

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
