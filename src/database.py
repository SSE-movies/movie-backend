"""Database operations for the Movie Backend API."""

from dataclasses import dataclass
from typing import List, Optional
import psycopg2
from .config import DATABASE_URL


@dataclass
class MovieQueryParams:
    """Parameters for movie queries."""

    page: int = 1
    per_page: int = 10
    title: Optional[str] = None
    media_type: Optional[str] = None
    categories_str: Optional[str] = None
    release_year: Optional[int] = None


def get_db_connection():
    """Creates a new database connection."""
    return psycopg2.connect(DATABASE_URL)


def get_movies(params: MovieQueryParams) -> tuple[List[dict], int]:
    """
    Get movies from database with optional filters.

    Args:
        params: MovieQueryParams object containing query parameters

    Returns:
        Tuple of (List of movie dictionaries, total count)
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Build base SQL for counting total results
    count_sql = """
        SELECT COUNT(*)
        FROM movies
    """

    # Build WHERE clauses (reuse existing code from lines 50-82)
    where_clauses = []
    query_params = []

    # Add filters (reuse existing code)
    if params.title:
        where_clauses.append("title ILIKE %s")
        query_params.append(f"%{params.title}%")

    if params.media_type:
        where_clauses.append("LOWER(type) = LOWER(%s)")
        query_params.append(params.media_type)

    if params.categories_str:
        category_clauses = []
        for cat in params.categories_str.split(","):
            cat = cat.strip()
            if cat:
                category_clauses.append('"listedIn" ILIKE %s')
                query_params.append(f"%{cat}%")

        if category_clauses:
            where_clauses.append("(" + " OR ".join(category_clauses) + ")")

    if params.release_year:
        where_clauses.append('"releaseYear" = %s')
        query_params.append(params.release_year)

    # Add WHERE clauses to count query if needed
    if where_clauses:
        count_sql += " WHERE " + " AND ".join(where_clauses)

    # Get total count
    cur.execute(count_sql, tuple(query_params))
    total_count = cur.fetchone()[0]

    # Execute main query (reuse existing code from lines 84-113)
    base_sql = """
        SELECT "showId", type, title, director, "cast", country,
               "dateAdded", "releaseYear", rating, duration,
               "listedIn", description
        FROM movies
    """

    if where_clauses:
        base_sql += " WHERE " + " AND ".join(where_clauses)

    base_sql += " LIMIT %s OFFSET %s"
    query_params.extend([params.per_page, (params.page - 1) * params.per_page])

    cur.execute(base_sql, tuple(query_params))
    rows = cur.fetchall()

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

    cur.close()
    conn.close()

    return movies_list, total_count


def get_movie_by_id(movie_id: str) -> Optional[dict]:
    """
    Retrieve a specific movie from the database by its showId.

    Args:
        movie_id (str): The unique identifier of the movie.

    Returns:
        A dictionary containing the movie's details if found, or None if the movie does not exist.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT "showId", type, title, director, "cast", country,
               "dateAdded", "releaseYear", rating, duration,
               "listedIn", description
        FROM movies
        WHERE "showId" = %s
    """
    cur.execute(query, (movie_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return {
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

    return None
