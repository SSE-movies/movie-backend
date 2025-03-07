import pytest
from src.movies import app

# import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_endpoint(client):
    """Test the home endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "Movie API is running!"


def test_get_movies_response_structure(client):
    """Test the structure of the movies endpoint response"""
    response = client.get("/movies")
    assert response.status_code == 200
    data = response.get_json()
    assert "page" in data
    assert "per_page" in data
    assert "movies" in data
    assert isinstance(data["movies"], list)


def test_pagination_defaults(client):
    """Test default pagination values"""
    response = client.get("/movies")
    data = response.get_json()
    assert data["page"] == 1
    assert data["per_page"] == 10


def test_movie_object_structure(client):
    """Test the structure of returned movie objects"""
    response = client.get("/movies")
    data = response.get_json()
    if len(data["movies"]) > 0:
        movie = data["movies"][0]
        required_fields = [
            "showId",
            "type",
            "title",
            "director",
            "cast",
            "country",
            "date_added",
            "releaseYear",
            "rating",
            "duration",
            "listedIn",
            "description",
        ]
        for field in required_fields:
            assert field in movie


def test_filter_params_accepted(client):
    """Test that filter parameters are accepted"""
    params = {
        "title": "test",
        "type": "Movie",
        "categories": "Drama",
        "release_year": "2020",
    }
    response = client.get("/movies", query_string=params)
    assert response.status_code == 200


def test_empty_response_structure(client):
    """Test response structure when no results found"""
    response = client.get(
        "/movies?title=ThisMovieDefinitelyDoesNotExist123456789"
    )
    data = response.get_json()
    assert response.status_code == 200
    assert "movies" in data
    assert isinstance(data["movies"], list)
    assert len(data["movies"]) == 0


def test_get_movies_custom_pagination(client):
    """Test getting movies with custom pagination"""
    response = client.get("/movies?page=2&per_page=5")
    assert response.status_code == 200
    data = response.get_json()
    assert data["page"] == 2
    assert data["per_page"] == 5
    assert len(data["movies"]) <= 5


def test_invalid_pagination_params(client):
    """Test handling of invalid pagination parameters"""
    response = client.get("/movies?page=invalid&per_page=invalid")
    assert response.status_code == 200
    data = response.get_json()
    # Should fall back to defaults
    assert data["page"] == 1
    assert data["per_page"] == 10


def test_get_movies_with_type_filter(client):
    """Test getting movies with type filter"""
    response = client.get("/movies?type=Movie")
    assert response.status_code == 200
    data = response.get_json()
    if len(data["movies"]) > 0:
        assert all(
            movie["type"].lower() == "movie" for movie in data["movies"]
        )


def test_get_movies_with_categories_filter(client):
    """Test getting movies with categories filter"""
    response = client.get("/movies?categories=Action,Adventure")
    assert response.status_code == 200
    data = response.get_json()
    if len(data["movies"]) > 0:
        assert any(
            "action" in movie["listedIn"].lower()
            or "adventure" in movie["listedIn"].lower()
            for movie in data["movies"]
        )


def test_get_movies_with_release_year_filter(client):
    """Test getting movies with release year filter"""
    response = client.get("/movies?release_year=2020")
    assert response.status_code == 200
    data = response.get_json()
    assert all(movie["releaseYear"] == 2020 for movie in data["movies"])


def test_get_movies_with_multiple_filters(client):
    """Test getting movies with multiple filters"""
    response = client.get(
        "/movies?title=Inception&type=Movie&release_year=2010"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert all(
        "inception" in movie["title"].lower()
        and movie["type"].lower() == "movie"
        and movie["releaseYear"] == 2010
        for movie in data["movies"]
    )


def test_invalid_page_number(client):
    """Test handling of invalid page number"""
    response = client.get("/movies?page=invalid")
    assert response.status_code == 200
    data = response.get_json()
    assert data["page"] == 1


def test_invalid_per_page_number(client):
    """Test handling of invalid per_page number"""
    response = client.get("/movies?per_page=invalid")
    assert response.status_code == 200
    data = response.get_json()
    assert data["per_page"] == 10


def test_pagination_metadata(client):
    """Test pagination metadata in response"""
    response = client.get("/movies")
    data = response.get_json()
    required_fields = ["page", "per_page", "total", "movies"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    assert isinstance(data["total"], int)
    assert data["total"] > 0


def test_filter_with_no_results(client):
    """Test filtering with criteria that should return no results"""
    response = client.get(
        "/movies?title=ThisMovieDefinitelyDoesNotExist123456789"
    )
    data = response.get_json()
    assert response.status_code == 200
    assert len(data["movies"]) == 0
    assert data["total"] == 0
