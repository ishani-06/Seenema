# 🎬 Seenema

### Discover your next favourite movie.

**Seenema** is a content-based movie recommendation system that helps users discover films similar to the ones they love. Built with Python and Streamlit, it uses **TF-IDF vectorization** and **cosine similarity** to recommend movies based on their metadata.

Seenema combines movie overviews, genres, keywords, cast, and director information to represent each movie as text. The trained recommendation artifacts are saved and loaded by the Streamlit application, so the model does not need to be trained whenever the app starts.

**Live application:** [https://seenema.streamlit.app/](https://seenema.streamlit.app/)

---

## ✨ Features

- 🔎 **Movie Search** — Find movies using the application's autocomplete search interface.
- 🎯 **Content-Based Recommendations** — Get five movies ranked by content similarity to the selected movie.
- 🧠 **TF-IDF Model** — Convert combined movie metadata into numerical feature vectors.
- 🎭 **Weighted Metadata** — Give genres, cast, and directors more influence in the text representation by repeating those terms.
- 🖼️ **Movie Posters** — Display recommendation cards using poster URLs from the local movie metadata catalogue.
- 🎬 **Movie Metadata** — Use movie IDs to connect recommendations with their display titles and poster information.
- 🎨 **Streamlit Interface** — Explore recommendations through Seenema's custom-branded interface.
- ⚡ **Precomputed Model Artifacts** — Load the saved vectorizer and TF-IDF matrix instead of fitting the model every time the application starts.
- 💾 **Local-First Recommendations** — Perform recommendation inference using the saved model and local data during normal operation.

---

## 🧠 Recommendation System

Seenema uses **content-based filtering** to identify movies with similar metadata.

### Recommendation Pipeline

1. **Data Loading:** Load the enriched movie dataset containing movie IDs, titles, overviews, genres, keywords, cast, and directors.
2. **Data Inspection:** Examine the dataset shape, missing values, and duplicate movie IDs and titles.
3. **Data Cleaning:** Select the required columns and remove rows containing missing values.
4. **Metadata Processing:** Parse JSON-formatted genres and keywords into Python lists.
5. **Text Normalization:** Convert genre, keyword, cast, and director terms into lowercase alphanumeric strings.
6. **Feature Construction:** Combine each movie's overview, genres, keywords, cast, and director into a single text representation called `soup`.
7. **Metadata Weighting:** Repeat selected metadata terms to influence their importance in the combined text.
8. **TF-IDF Vectorization:** Transform the combined movie text into numerical feature vectors using `TfidfVectorizer`.
9. **Similarity Calculation:** Calculate cosine similarity between the selected movie and the other movies using `linear_kernel`.
10. **Ranking:** Sort candidate movies by similarity and return the top five recommendations.
11. **Duplicate Handling:** Exclude the selected movie and other entries with the same normalized title.
12. **Presentation:** Match recommended movie IDs with the local metadata catalogue and display their titles and posters in Streamlit.

### Metadata Weighting

The model combines the selected movie features into a single text field. The current metadata weights are:

| Metadata Field | Weight | Implementation |
|---|---:|---|
| Overview | — | Included once in lowercase |
| Genres | 4 | Each genre term is repeated four times |
| Keywords | 1 | Each keyword term is included once |
| Cast | 3 | The first five cast members are repeated three times |
| Director | 3 | Director terms are repeated three times |

Repeating metadata terms changes their frequency in the combined text and influences the resulting TF-IDF representation.

### TF-IDF Configuration

The model uses the following configuration:

| Parameter | Value |
|---|---|
| `stop_words` | `"english"` |
| `ngram_range` | `(1, 1)` |
| `min_df` | `2` |
| `max_features` | `100_000` |
| `sublinear_tf` | `True` |

The vectorizer uses unigrams, ignores English stop words, excludes terms appearing in fewer than two documents, limits the vocabulary to at most 100,000 features, and applies sublinear term-frequency scaling.

### Similarity Calculation

Seenema uses `TfidfVectorizer` to transform the combined movie text into numerical feature vectors.

The model then uses `linear_kernel` to calculate the dot product between the selected movie's TF-IDF vector and the vectors of all movies. Since the TF-IDF vectors are L2-normalized by default, this dot product corresponds to cosine similarity.

Movies are ranked in descending order of similarity, and the highest-ranked candidates are returned as recommendations.

### Recommendation Logic

The `recommend()` function accepts the following parameters:

```python
recommend(title, movie_id=None, n=5)
```

| Parameter | Description |
|---|---|
| `title` | The title of the movie selected by the user |
| `movie_id` | Optional movie ID used to resolve duplicate exact titles |
| `n` | Number of recommendations to return; defaults to five |

The function performs exact title matching after stripping whitespace and applying case-folding. If a movie is not found, it returns up to five titles containing the supplied search text.

The selected movie and other entries with the same normalized title are excluded from the recommendations. The remaining candidates are ranked entirely by content similarity.

### Model Artifacts

The trained model is serialized into:

```text
backend/movie_recommender.pkl
```

The pickle file contains:

- `movies` — The processed DataFrame containing `movie_id`, `title`, and `soup`.
- `tfidf_vectorizer` — The fitted TF-IDF vectorizer.
- `tfidf_matrix` — The generated TF-IDF feature matrix.
- `version` — The model version identifier, currently `v2`.

These artifacts allow the application to reuse the precomputed feature matrix and fitted vectorizer without retraining the model whenever the application starts.

---

## 🏗️ Architecture

Seenema separates offline model preparation from runtime recommendation inference.

```text
                  OFFLINE MODEL PREPARATION

              movies_raw_enriched.csv
                        |
                        v
                 Data Inspection
                        |
                        v
                  Data Cleaning
                        |
                        v
                Metadata Processing
                        |
                        v
                 Text Construction
             (Overview + Weighted Metadata)
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
                    Movie Search
                        |
                        v
                  Selected Movie
                        |
                        v
                 Saved Model Artifacts
                        |
                        v
                Similarity Calculation
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

### Design Principles

- **Content-Based Filtering:** Recommend movies based on their metadata.
- **Offline Model Preparation:** Prepare the TF-IDF representation in the notebook.
- **Reusable Artifacts:** Save the fitted vectorizer and feature matrix for inference.
- **Local-First Inference:** Use saved model artifacts and local metadata during normal operation.
- **Movie-ID Matching:** Connect recommendation results with their corresponding display metadata.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application and recommendation logic |
| Streamlit | Application interface |
| `streamlit-searchbox` | Movie autocomplete search, where used by the application |
| pandas | Dataset processing and manipulation |
| scikit-learn | TF-IDF vectorization and similarity calculation |
| NumPy / SciPy | Numerical operations and sparse matrix support |
| `pickle` | Serialization of model artifacts |
| Jupyter Notebook | Offline model development, testing, and artifact export |
| Git & GitHub | Version control and collaboration |
| TMDB | Source of movie metadata and poster imagery, where applicable |

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

The structure above represents the expected project layout. The exact files present in the repository may vary.

### Directory Responsibilities

- `app.py` — Streamlit application, movie search, model loading, recommendation inference, and result presentation.
- `backend/model.ipynb` — Data inspection, preprocessing, feature construction, TF-IDF model preparation, recommendation testing, and artifact export.
- `backend/movie_recommender.pkl` — Serialized model artifacts used by the application.
- `data/raw/movies_raw_enriched.csv` — Source dataset used during model preparation.
- `data/movie_metadata.csv` — Local movie metadata used for search, display titles, and poster URLs.
- `assets/` — Branding assets used by the interface.
- `.streamlit/config.toml` — Streamlit configuration and theme settings.
- `requirements.txt` — Python dependencies required to run the application.

---

## 🚀 Getting Started

### Prerequisites

- Python installed on your system.
- Git.
- The project source files and required datasets.
- The saved model artifact at `backend/movie_recommender.pkl`, unless you intend to generate it from the notebook.

### 1. Clone the Repository

Replace `<repository-url>` with the URL of your GitHub repository.

```bash
git clone <repository-url>
cd seenema
```

### 2. Create a Virtual Environment

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

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Seenema

From the project root, execute:

```bash
streamlit run app.py
```

Streamlit will provide a local URL, typically:

```text
http://localhost:8501
```

### Rebuilding the Model

To regenerate the model artifacts, run the cells in `backend/model.ipynb` in order.

The notebook reads the enriched CSV, prepares the movie text, fits the TF-IDF vectorizer, tests recommendations across a selection of movies, and exports the model artifacts to the backend directory based on the notebook's working directory.

Normal application execution uses the saved model and local metadata. TMDB credentials are not required by the current recommendation flow when all required local files are present.

---

## 🧪 Recommendation Methodology

### 1. Content-Based Filtering

Content-based filtering recommends movies by comparing their content and metadata. Each movie is represented by its overview, genres, keywords, cast, and director information.

Movies with similar textual representations receive higher similarity scores and are ranked higher in the recommendation results.

### 2. TF-IDF

**Term Frequency–Inverse Document Frequency (TF-IDF)** converts text into numerical feature vectors.

- **Term Frequency (TF):** Measures how frequently a term occurs in a document.
- **Inverse Document Frequency (IDF):** Reduces the influence of terms that appear across many documents.

Together, these measures help represent the distinctive textual characteristics of each movie.

### 3. Cosine Similarity

**Cosine similarity** measures the similarity between two feature vectors based on the angle between them.

For L2-normalized TF-IDF vectors, the dot product calculated using `linear_kernel` is equivalent to cosine similarity.

Seenema calculates the selected movie's similarity against the entire feature matrix, sorts the candidate movies by score, and returns the highest-ranked results.

### 4. Duplicate-Title Handling

The recommendation function normalizes titles by stripping whitespace and applying case-folding.

An optional `movie_id` can be provided to resolve duplicate exact titles. During recommendation ranking, the selected movie and entries sharing its normalized title are excluded.

---

## 🎞️ Data Attribution

Movie metadata and poster imagery are sourced from TMDB where applicable.

[The Movie Database (TMDB)](https://www.themoviedb.org/)

Seenema is an independent project and is not endorsed or certified by TMDB. Applicable attribution, branding, and data usage requirements must be followed.

---

## 🗺️ Future Scope

Potential areas for further development include:

- More comprehensive movie detail pages.
- Further refinement of movie search and duplicate-title selection.
- Evaluation of recommendation relevance across different genres.
- Expanded movie metadata and poster coverage.
- Further performance and interface improvements as the catalogue grows.

---

**Built with Python and a love for cinema. 🍿**
