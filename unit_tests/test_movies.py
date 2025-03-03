import pytest
from src.movies import app
import os
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


def test_get_movies_default_pagination(client):
    """Test getting movies with default pagination"""
    response = client.get("/movies")
    assert response.status_code == 200
    data = response.get_json()
    assert "page" in data
    assert "per_page" in data
    assert "movies" in data
    assert data["page"] == 1
    assert data["per_page"] == 10
    assert isinstance(data["movies"], list)


def test_get_movies_custom_pagination(client):
    """Test getting movies with custom pagination"""
    response = client.get("/movies?page=2&per_page=5")
    assert response.status_code == 200
    data = response.get_json()
    assert data["page"] == 2
    assert data["per_page"] == 5
    assert len(data["movies"]) <= 5


# def test_get_movies_with_title_filter(client):
#     """Test getting movies with title filter"""
#     response = client.get('/movies?title=Jaws')
#     assert response.status_code == 200
#     data = response.get_json()
#     assert all('Jaws' in movie['title'].lower() for movie in data['movies'])


def test_get_movies_with_type_filter(client):
    """Test getting movies with type filter"""
    response = client.get("/movies?type=Movie")
    assert response.status_code == 200
    data = response.get_json()
    assert all(movie["type"].lower() == "movie" for movie in data["movies"])


def test_get_movies_with_categories_filter(client):
    """Test getting movies with categories filter"""
    response = client.get("/movies?categories=Action,Adventure")
    assert response.status_code == 200
    data = response.get_json()
    # Check if any movie has either Action or Adventure in its categories
    assert any(
        "Action" in movie["listedIn"] or "Adventure" in movie["listedIn"]
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
    response = client.get("/movies?title=Inception&type=Movie&release_year=2010")
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
