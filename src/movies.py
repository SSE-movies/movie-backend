from flask import Flask, jsonify, request
from .database import get_movies
from .config import PORT

app = Flask(__name__)


@app.route("/")
def home():
    return "Movie API is running!"


@app.route("/movies", methods=["GET"])
def get_movies_route():
    """
    GET /movies

    Supports optional query parameters:
      - page (int): default=1
      - per_page (int): default=10
      - title (str): partial match on title (case-insensitive)
      - type (str): exact match on the 'type' column
      - categories (str): comma-separated list, each substring is matched
                          in 'listedIn'
      - release_year (int): exact match on 'releaseYear'
    """
    # Get query parameters for pagination
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    # Additional filters
    title = request.args.get("title", default=None, type=str)
    media_type = request.args.get("type", default=None, type=str)
    categories_str = request.args.get("categories", default=None, type=str)
    release_year = request.args.get("release_year", default=None, type=int)

    # Get movies from database
    movies_list = get_movies(
        page=page,
        per_page=per_page,
        title=title,
        media_type=media_type,
        categories_str=categories_str,
        release_year=release_year
    )

    return jsonify({
        "page": page,
        "per_page": per_page,
        "movies": movies_list
    })


def run_app():
    """Run the Flask application"""
    app.run(host="0.0.0.0", port=PORT)
