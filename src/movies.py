"""Flask routes for the Movie Backend API."""

from flask import Flask, jsonify, request
from .database import get_movies, MovieQueryParams, get_movie_by_id
from .config import PORT

app = Flask(__name__)


@app.route("/")
def home():
    """Return a simple message indicating the API is running."""
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
      - categories (str): comma-separated list, each substring is matched in 'listedIn'
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

    # Create query parameters object
    params = MovieQueryParams(
        page=page,
        per_page=per_page,
        title=title,
        media_type=media_type,
        categories_str=categories_str,
        release_year=release_year,
    )

    # Get movies from database
    movies_list = get_movies(params)

    return jsonify({"page": page, "per_page": per_page, "movies": movies_list})


@app.route("/movies/<movie_id>", methods=["GET"])
def get_movie_by_id_route(movie_id):
    """
    GET /movies/<movie_id>

    Retrieve detailed information for a specific movie identified by its unique showId.

    Args:
        movie_id (str): The unique identifier for the movie to retrieve.

    Returns:
        A JSON response containing the movie's details, including:
            - showId: Unique movie identifier.
            - type: Movie type.
            - title: Movie title.
            - director: Director's name.
            - cast: Main cast.
            - country: Country of production.
            - date_added: Date the movie was added.
            - releaseYear: Year of release.
            - rating: Movie rating.
            - duration: Movie duration.
            - listedIn: Categories or genres.
            - description: Movie description.
        If the movie is not found, returns a JSON response with an error message and a 404 status code.
    """
    # Call the helper function from database.py (assume you've defined it there)
    movie = get_movie_by_id(movie_id)
    if movie:
        return jsonify(movie)
    else:
        return jsonify({"error": "Movie not found"}), 404


def run_app():
    """Run the Flask application."""
    app.run(host="0.0.0.0", port=PORT)
