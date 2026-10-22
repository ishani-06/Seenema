
import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Paths
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "movies_raw_enriched.csv"
MODEL_PATH = ROOT / "backend" / "movie_recommender.pkl"

# Load the required columns
columns = [
    "movie_id",
    "title",
    "overview",
    "genres",
    "keywords",
    "cast",
    "director",
]

df = pd.read_csv(DATA_PATH)[columns]

# Remove rows with missing values in any selected column
df = df.dropna(subset=columns).reset_index(drop=True)

# Convert JSON lists into readable text
def parse_list(value):
    try:
        result = json.loads(value)
        return " ".join(result) if isinstance(result, list) else ""
    except (json.JSONDecodeError, TypeError):
        return ""

# Combine movie information into one text field
def build_text(row):
    genres = parse_list(row["genres"])
    keywords = parse_list(row["keywords"])
    cast = row["cast"].replace("|", " ")
    director = row["director"].replace("|", " ")

    return " ".join([
        row["overview"],
        genres,
        keywords,
        cast,
        director,
    ])

df["text"] = df.apply(build_text, axis=1)

# Convert text into TF-IDF vectors
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["text"])

# Save the model and movie data
with open(MODEL_PATH, "wb") as file:
    pickle.dump(
        {
            "movies": df.drop(columns=["text"]),
            "vectorizer": vectorizer,
            "tfidf_matrix": tfidf_matrix,
        },
        file,
    )

print("Movies used:", len(df))
print("TF-IDF matrix shape:", tfidf_matrix.shape)
print("Model saved to:", MODEL_PATH)

def recommend(title, movie_id=None, n=5):
    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    movies = model["movies"]
    matrix = model["tfidf_matrix"]

    matches = movies.index[
        movies["title"].str.casefold() == title.strip().casefold()
    ].tolist()

    if not matches:
        return f"Movie not found: {title}"

    if movie_id is not None:
        matches = [
            i for i in matches
            if movies.iloc[i]["movie_id"] == movie_id
        ]
        if not matches:
            return f"Movie ID {movie_id} does not match '{title}'."

    elif len(matches) > 1:
        return movies.iloc[matches][["movie_id", "title"]]

    query_idx = matches[0]

    scores = cosine_similarity(
        matrix[query_idx], matrix
    ).flatten()

    ranked_indices = scores.argsort()[::-1]
    ranked_indices = [
        i for i in ranked_indices if i != query_idx
    ][:n]

    results = movies.iloc[ranked_indices][
        ["movie_id", "title"]
    ].copy()

    results["similarity"] = scores[ranked_indices]

    return results.reset_index(drop=True)



if __name__ == "__main__":
    test_movies = [
        "The Notebook",
        "Star Wars",
        "Toy Story",
        "The Godfather",
        "Saiyaara",
        "Drishyam",
        "Inception",
        "Interstellar",
        "3 Idiots",
        "Parasite",
    ]

    for title in test_movies:
        print(f"\n{'=' * 60}")
        print(f"Recommendations for: {title}")
        print("=" * 60)

        result = recommend(title, n=5)

        if isinstance(result, pd.DataFrame):
            print(result.to_string(index=False))
        else:
            print(result)

