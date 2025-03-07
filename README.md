# Movie Backend API

## Overview

The Movie Backend API is a RESTful service that provides access to a database of movies and TV shows. It supports filtering, pagination, and detailed movie information retrieval.

## Features

- Get a list of movies with pagination
- Filter movies by title, type, categories, and release year
- Get detailed information about a specific movie by ID
- Consistent JSON response format

## API Endpoints

### `GET /`

Returns a simple message indicating the API is running.

**Response:**

Movie API is running!


### `GET /movies`

Returns a paginated list of movies with optional filtering.

**Query Parameters:**
- `page` (int, default=1): Page number for pagination
- `per_page` (int, default=10): Number of results per page
- `title` (string): Partial match on movie title (case-insensitive)
- `type` (string): Exact match on media type (e.g., "Movie" or "TV Show")
- `categories` (string): Comma-separated list of categories to match in the "listedIn" field
- `release_year` (int): Exact match on release year

**Response:**

JSON response containing:
- `page`: Current page number
- `per_page`: Number of results per page
- `total`: Total number of results
- `movies`: List of movie dictionaries

Example:

```json
{
  "page": 1,
  "per_page": 10,
  "total": 100,
  "movies": [
    {
      "showId": "1234567890",
      "type": "Movie",
      "title": "Inception",
      "director": "Christopher Nolan",
      "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page",
      "country": "USA",
      "date_added": "2010-07-16",
      "releaseYear": 2010,
      "rating": "PG-13",
      "duration": "2h 28m",
      "listedIn": "Action, Adventure, Sci-Fi",
      "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO."
    }
  ]
}
```

### `GET /movies/<movie_id>`

Returns detailed information about a specific movie by its ID.

**Path Parameters:**
- `movie_id` (string): The unique identifier of the movie

**Response:**

JSON response containing the movie details if found, or an error message if not found.

Example:

```json
{
  "showId": "1234567890",
  "type": "Movie",
  "title": "Inception",
  "director": "Christopher Nolan",
  "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page",
  "country": "USA",
  "date_added": "2010-07-16",
  "releaseYear": 2010,
  "rating": "PG-13",
  "duration": "2h 28m",
  "listedIn": "Action, Adventure, Sci-Fi",
  "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO."
}
```

## Running the API

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the API:

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

## Testing

To run the tests:

```bash
pytest unit_tests.py
```

The API expects a PostgreSQL database (in Supabase)with a `movies` table containing the following columns:
- `showId` (string): Unique identifier
- `type` (string): Media type (Movie or TV Show)
- `title` (string): Title of the movie or show
- `director` (string): Director name(s)
- `cast` (string): Cast members
- `country` (string): Country of origin
- `dateAdded` (string): Date added to the database
- `releaseYear` (integer): Year of release
- `rating` (string): Content rating
- `duration` (string): Duration (e.g., "90 min" or "2 Seasons")
- `listedIn` (string): Categories (comma-separated)
- `description` (string): Plot summary

## Docker Support

The application can be run in a Docker container using the provided Dockerfile:

```bash
docker build -t movie-backend .
docker run -p 5000:5000 -e DATABASE_URL=your_db_url movie-backend
```                             