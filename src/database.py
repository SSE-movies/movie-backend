import psycopg2
from .config import DATABASE_URL

def get_db_connection():
    """Creates a new database connection"""
    return psycopg2.connect(DATABASE_URL)

def get_movies(page=1, per_page=10, title=None, media_type=None, categories_str=None, release_year=None):
    """
    Get movies from database with optional filters
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Calculate offset for SQL LIMIT
    offset = (page - 1) * per_page

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

    # Categories: "Action & Adventure, Documentary"
    if categories_str:
        category_clauses = []
        for cat in categories_str.split(","):
            cat = cat.strip()
            if cat:  # only apply if non-empty
                category_clauses.append('"listedIn" ILIKE %s')
                params.append(f"%{cat}%")

        if category_clauses:
            where_clauses.append("(" + " OR ".join(category_clauses) + ")")

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

    return movies_list 