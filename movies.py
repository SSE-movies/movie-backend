from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

class MovieData:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.movies_dict = self.load_data()

    def load_data(self):
        df = pd.read_csv(self.csv_file)
        movies_dict = {}
        for _, row in df.iterrows():
            show_id = row["show_id"]
            movies_dict[show_id] = {
                "type": row["type"],
                "title": row["title"],
                "director": row["director"] if pd.notna(row["director"]) else None,
                "cast": row["cast"].split(", ") if pd.notna(row["cast"]) else [],
                "country": row["country"] if pd.notna(row["country"]) else None,
                "date_added": row["date_added"] if pd.notna(row["date_added"]) else None,
                "release_year": row["release_year"],
                "rating": row["rating"] if pd.notna(row["rating"]) else None,
                "duration": row["duration"] if pd.notna(row["duration"]) else None,
                "genres": row["listed_in"].split(", ") if pd.notna(row["listed_in"]) else [],
                "description": row["description"] if pd.notna(row["description"]) else None,
            }
        return movies_dict

movie_data = MovieData("netflix_titles.csv")

@app.route("/", methods=["GET"])
def get_movies():
    return jsonify(list(movie_data.movies_dict.values()))

@app.route("/movies/<show_id>", methods=["GET"])
def get_movie(show_id):
    movie = movie_data.movies_dict.get(show_id)
    if movie:
        return jsonify(movie)
    return jsonify({"error": "Movie not found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
