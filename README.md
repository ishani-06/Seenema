# 🎬 Seenema

### Discover your next favourite movie.

Seenema is a content-based movie recommendation system that helps users discover films similar to the ones they love. Built with Python and Streamlit, it uses TF-IDF vectorization and cosine similarity to recommend movies based on their metadata.

Seenema combines movie overviews, genres, keywords, cast, and director information to identify films with similar content. The application also features movie autocomplete search and poster-based recommendation cards.

> **Project status:** MVP implemented. Deployment and further improvements are ongoing.

---

## ✨ Features

- 🔎 **Movie Search** — Search for movies using an autocomplete interface backed by a local movie catalogue.
- 🎯 **Content-Based Recommendations** — Discover five similar movies using TF-IDF vectors and cosine similarity.
- 🖼️ **Movie Posters** — Display recommendation posters using locally stored poster URLs.
- 🎬 **Movie Metadata** — Use movie IDs to connect recommendations with their display titles and poster information.
- 🎨 **Streamlit Interface** — Explore movie recommendations through a custom-branded interface.
- ⚡ **Precomputed Model Artifacts** — Load a saved recommendation model instead of retraining it every time the application starts.
- 💾 **Local-First Recommendations** — Generate recommendations from the saved model and local data without making TMDB API requests during normal operation.

---

## 🧠 Recommendation System

Seenema uses **content-based filtering** to identify movies with similar metadata.

### Recommendation pipeline

1. **Data preparation:** Load the enriched movie dataset containing movie IDs, titles, overviews, genres, keywords, cast, and directors.
2. **Data cleaning:** Remove rows with missing required fields, handle duplicate checks, clean titles, and normalize metadata.
3. **Text preprocessing:** Convert genres and keywords into text and normalize cast and director fields.
4. **Feature construction:** Combine the selected metadata fields into a single text representation for each movie.
5. **TF-IDF vectorization:** Transform movie text into numerical feature vectors using `TfidfVectorizer`.
6. **Similarity calculation:** Calculate cosine similarity between the selected movie and the other movies in the dataset.
7. **Ranking:** Rank movies by similarity and return the top five recommendations, excluding the selected movie and other entries with the same normalized title.
8. **Presentation:** Match recommended movie IDs with the local metadata catalogue and display their titles and posters in Streamlit.

### Example

Selecting *The Godfather* may return other crime dramas or films with similar themes, cast, keywords, or descriptions.

Actual recommendations depend on the dataset and the similarity scores produced by the model.

### Model artifacts

The trained artifacts are serialized into:

`backend/movie_recommender.pkl`

The pickle file contains:

- The processed movie DataFrame.
- The fitted TF-IDF vectorizer.
- The TF-IDF feature matrix.
- A model version identifier.

This allows the application to reuse the existing model without fitting the vectorizer on every launch.

---

## 🏗️ Architecture

Seenema currently uses a simple, integrated Streamlit architecture.

```text
                 OFFLINE MODEL PREPARATION

             movies_raw_enriched.csv
                        |
                        v
                 Data Cleaning
                        |
                        v
               Metadata Processing
                        |
                        v
                Text Construction
                        |
                        v
               TF-IDF Vectorization
                        |
                        v
               Saved Model Artifacts
                        |
                        v
             movie_recommender.pkl


                 RUNTIME APPLICATION

                 Streamlit app.py
                        |
                        v
                Movie Autocomplete
                        |
                        v
                 Selected Movie ID
                        |
                        v
             Saved TF-IDF Feature Matrix
                        |
                        v
               Cosine Similarity
                        |
                        v
             Top-5 Movie Recommendations
                        |
                        v
              Local Movie Metadata
                        |
                        v
             Titles and Poster Cards
```

### Design principles

- **Simplicity:** Keep the initial application easy to understand, run, and maintain.
- **Local-first recommendations:** Use saved model artifacts and local metadata during normal operation.
- **Separation of preparation and inference:** Prepare the recommendation model offline and load it at runtime.
- **Content-based filtering:** Recommend movies based on their metadata rather than user ratings or collaborative filtering.
- **Incremental development:** Build and improve the MVP without introducing unnecessary infrastructure.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application and recommendation logic |
| Streamlit | Application interface |
| streamlit-searchbox | Movie autocomplete search |
| pandas | Dataset processing and manipulation |
| scikit-learn | TF-IDF vectorization and cosine similarity |
| NumPy / SciPy | Numerical operations and sparse matrix support |
| pickle | Serialization of model artifacts |
| Jupyter Notebook | Offline model development and experimentation |
| Git & GitHub | Version control and collaboration |
| TMDB | Movie metadata and poster source, where applicable |

---

## 📁 Project Structure

```text
seenema/
├── app.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── logo.png
│   └── hero.png
├── backend/
│   ├── model.ipynb
│   └── movie_recommender.pkl
└── data/
    ├── raw/
    │   └── movies_raw_enriched.csv
    └── movie_metadata.csv
```

The structure above represents the current application layout. The exact files present in the repository may vary as development continues.

**Directory responsibilities**

- `app.py` — Streamlit application, search interface, model loading, recommendation logic, and poster presentation.
- `backend/model.ipynb` — Data preprocessing, feature construction, model development, testing, and artifact export.
- `backend/movie_recommender.pkl` — Serialized model artifacts used by the application.
- `data/raw/` — Source dataset used during model preparation.
- `data/movie_metadata.csv` — Movie metadata used for autocomplete, display titles, and poster URLs.
- `assets/` — Branding assets used by the interface.
- `.streamlit/config.toml` — Streamlit configuration and theme settings.
- `requirements.txt` — Python dependencies required to run the application.

---

## 🚀 Getting Started

### Prerequisites

- Python installed on your system.
- Git.
- The project source files and required datasets.
- The saved model artifact at `backend/movie_recommender.pkl`.

### 1. Clone the repository

Replace `<repository-url>` with the URL of your GitHub repository.

```bash
git clone <repository-url>
cd seenema
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Seenema

From the project root, run:

```bash
streamlit run app.py
```

Streamlit will provide a local URL, typically `http://localhost:8501`.

**Note:** Normal application execution uses the saved model and local metadata. TMDB credentials are not required by the current recommendation flow, provided all required local files are present.

---

## 🧪 Recommendation Methodology

Seenema currently uses two main machine learning techniques.

### TF-IDF (Term Frequency–Inverse Document Frequency)

TF-IDF converts each movie's combined text metadata into a numerical feature vector. Words that are useful for distinguishing one movie from others receive greater importance than words that appear frequently across the entire collection.

### Cosine similarity

Cosine similarity measures how closely two movie feature vectors align. The application ranks candidate movies by their similarity to the selected movie and returns the highest-ranked results.

This is a content-based recommendation approach. It does not currently learn from user watch histories, ratings, or collaborative user behaviour.

---

## 🎞️ Data Attribution

Movie metadata and poster imagery are sourced from TMDB where applicable.

[The Movie Database (TMDB)](https://www.themoviedb.org/)

Seenema is an independent project and is not endorsed or certified by TMDB. Applicable attribution, branding, and data usage requirements must be followed.

---

## 🗺️ Future Improvements

Potential improvements beyond the current MVP include:

- More comprehensive movie detail pages.
- Better handling of duplicate movie titles and ambiguous searches.
- Evaluation of recommendation relevance across different genres.
- Improved error handling for missing metadata and unavailable posters.
- Deployment and production-readiness improvements.
- Performance and memory optimization for larger movie collections.

These are future improvements, not claims about features already implemented.

---

**Built with Python and a love for cinema. 🍿**