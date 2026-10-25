🎬 Seenema
Discover your next favourite movie.
Seenema is a content-based movie recommendation system that helps users discover films similar to the ones they love. Built with Python and Streamlit, it uses TF-IDF vectorization and cosine similarity to recommend movies based on their metadata.

Seenema combines movie overviews, genres, keywords, cast, and director information to represent each movie as text. The trained recommendation artifacts are saved and loaded by the Streamlit application, so the model does not need to be trained whenever the app starts.

Live application: https://seenema.streamlit.app/
✨ Features
- 🔎 Movie Search — Find movies using the application's autocomplete/search interface.
- 🎯 Content-Based Recommendations — Get five movies ranked by content similarity to the selected movie.
- 🧠 TF-IDF Model — Convert combined movie metadata into numerical feature vectors.
- 🎭 Weighted Metadata — Give genres, cast, and directors more influence in the text representation by repeating those terms.
- 🖼️ Movie Posters — Display recommendation cards using poster URLs from the local movie metadata catalogue.
- 🎬 Movie Metadata — Use movie IDs to connect recommendations with display titles and poster information.
- 🎨 Streamlit Interface — Explore recommendations through Seenema's custom-branded interface.
- ⚡ Precomputed Model Artifacts — Load the saved vectorizer and TF-IDF matrix instead of fitting the model every time the app starts.
- 💾 Local-First Recommendations — Perform recommendation inference using the saved model and local data during normal operation.
🧠 Recommendation System
Seenema uses content-based filtering. It compares the content and metadata of a selected movie with other movies in the catalogue; it does not base recommendations on user ratings or collaborative user behaviour.
Recommendation pipeline
1. Load the dataset: Read movies_raw_enriched.csv, containing movie IDs, titles, overviews, genres, keywords, cast, and directors.
2. Inspect and select fields: Print the dataset shape, missing-value counts, and duplicate checks, then select the fields used by the model.
3. Clean the data: Drop rows with missing values in the selected fields.
4. Parse metadata: Convert the JSON-formatted genre and keyword fields into Python lists.
5. Normalize metadata terms: Remove non-alphanumeric characters from genre, keyword, cast, and director terms and convert them to lowercase.
6. Build the movie text: Combine each movie's overview with its genres, keywords, first five cast members, and director information.
7. Apply metadata weights: Repeat selected metadata terms to influence their relative importance in the combined text.
8. Generate TF-IDF vectors: Fit TfidfVectorizer to the combined movie text and create a TF-IDF feature matrix.
9. Save model artifacts: Serialize the processed movie DataFrame, fitted vectorizer, TF-IDF matrix, and version identifier into a pickle file.
10. Load and search at runtime: The Streamlit app loads the saved artifacts and uses the selected movie to calculate similarity scores.
11. Rank recommendations: Sort candidate movies by similarity and return the top five, excluding the selected entry and other entries with the same normalized title.
12. Display results: Use movie IDs to connect recommended movies with the local metadata catalogue and display recommendation titles and posters.
Metadata weighting
The model constructs a single text field, called soup, for each movie. The current weights in model.ipynb are:
Metadata field	Weight	How it is applied
Overview	—	Included once in lowercase
Genres	4	Each genre term is repeated four times
Keywords	1	Each keyword term is included once
Cast	3	Each of the first five cast terms is repeated three times
Director	3	Each director term is repeated three times


Repeating terms changes their frequency in the combined text and therefore influences the resulting TF-IDF representation.
TF-IDF configuration
The notebook uses the following configuration:
Parameter	Value
stop_words	"english"
ngram_range	(1, 1)
min_df	2
max_features	100_000
sublinear_tf	True


The vectorizer creates unigram features, ignores English stop words, excludes terms appearing in fewer than two documents, limits the vocabulary to at most 100,000 features, and applies sublinear term-frequency scaling.
Similarity and ranking
The recommender calculates similarity between the selected movie's TF-IDF vector and the vectors of all movies using linear_kernel. Because TfidfVectorizer uses L2 normalization by default, this dot product corresponds to cosine similarity for the generated vectors.

The candidate movies are sorted in descending similarity order. The selected movie and entries with the same stripped, case-folded title are excluded before the top n results are returned. The default number of recommendations is five.

The title lookup uses exact matching after trimming whitespace and applying case-folding. If a title is not found, the function returns up to five titles containing the supplied search text. An optional movie_id can be provided to resolve duplicate exact titles.
Model artifacts
The notebook exports the model to:
backend/movie_recommender.pkl
The pickle file contains:
- movies — the processed DataFrame with movie_id, title, and soup.
- tfidf_vectorizer — the fitted TfidfVectorizer.
- tfidf_matrix — the TF-IDF feature matrix.
- version — the model version identifier (v2).
The Streamlit application can reuse these precomputed artifacts without fitting the vectorizer again during normal startup.
🏗️ Architecture
Seenema uses an offline model-preparation workflow and a Streamlit runtime application.
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
                  Saved Artifacts
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
                 Selected Movie ID
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
               Recommendation Poster Cards
Design principles
- Content-based filtering: Recommend films using movie metadata.
- Offline preparation: Build the TF-IDF representation in the notebook.
- Reusable artifacts: Save the fitted vectorizer and feature matrix for inference.
- Local-first inference: Use the saved model and local metadata during normal application operation.
- Movie-ID matching: Connect recommendation results to their corresponding display metadata.
🛠️ Tech Stack
Technology	Purpose
Python	Core application and recommendation logic
Streamlit	Application interface
streamlit-searchbox / Streamlit search controls	Movie search and autocomplete interface
pandas	Dataset processing and manipulation
scikit-learn	TF-IDF vectorization and similarity calculation
NumPy / SciPy	Numerical operations and sparse matrix support
pickle	Serialization of model artifacts
Jupyter Notebook	Offline model development, testing, and artifact export
Git & GitHub	Version control and collaboration
TMDB	Source of movie metadata and poster imagery, where applicable


📁 Project Structure
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
The listing shows the expected project layout; optional assets and configuration files may vary with the repository version.
Directory responsibilities
- app.py — Streamlit interface, movie search, loading of saved model artifacts, recommendation inference, and result presentation.
- backend/model.ipynb — Data inspection and cleaning, metadata processing, text construction, TF-IDF model preparation, recommendation tests, and artifact export.
- backend/movie_recommender.pkl — Serialized processed movie data, fitted TF-IDF vectorizer, feature matrix, and version identifier.
- data/raw/movies_raw_enriched.csv — Source dataset used to prepare the recommendation model.
- data/movie_metadata.csv — Local movie metadata used by the application for search/display information and poster URLs.
- assets/ — Branding assets used by the interface.
- .streamlit/config.toml — Streamlit configuration and theme settings.
- requirements.txt — Python dependencies required to run the application.
🚀 Getting Started
Prerequisites
- Python installed on your system.
- Git.
- The project source files and required datasets.
- The saved model artifact at backend/movie_recommender.pkl, unless you intend to generate it from the notebook.
1. Clone the repository
Replace <repository-url> with the URL of your GitHub repository.
git clone <repository-url>
cd seenema
2. Create a virtual environment
python -m venv .venv
Activate it on Linux or macOS:
source .venv/bin/activate
On Windows PowerShell:
.venv\Scripts\Activate.ps1
3. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
4. Run Seenema
From the project root, run:
streamlit run app.py
Streamlit will provide a local URL, typically http://localhost:8501.
Rebuilding the model
To regenerate the model artifacts, run the cells in backend/model.ipynb in order. The notebook reads the enriched CSV, prepares the movie text, fits the TF-IDF vectorizer, runs recommendation tests, and writes movie_recommender.pkl to the backend directory based on the notebook's working directory.

Normal application execution uses the saved model and local metadata. TMDB credentials are not required by the current recommendation flow when all required local files are present.
🧪 Recommendation Methodology
1. Content-based filtering
Each movie is represented by its overview and selected metadata. The system compares these representations to find movies with similar textual features. Recommendations are therefore driven by movie content rather than a user's watch history or ratings.
2. TF-IDF
Term Frequency–Inverse Document Frequency (TF-IDF) transforms the combined text into numerical feature vectors. It balances how often a term appears in a movie's text against how common that term is across the collection. The model can then compare movies mathematically.
3. Cosine similarity
Cosine similarity compares the direction of two feature vectors. A higher score indicates that their TF-IDF representations are more similar. Seenema computes the selected movie's scores against the feature matrix, sorts the candidates by score, and presents the highest-ranked results.
4. Duplicate-title handling
The recommender performs title lookup using stripped, case-folded titles. When a movie_id is supplied, it can select a matching entry by ID. During ranking, it excludes the selected entry and any other entries whose normalized title matches the selected title.
🎞️ Data Attribution
Movie metadata and poster imagery are sourced from TMDB where applicable.

The Movie Database (TMDB)

Seenema is an independent project and is not endorsed or certified by TMDB. Applicable attribution, branding, and data usage requirements must be followed.
🗺️ Future Scope
Potential areas for continued development include:
- More comprehensive movie detail pages.
- Further refinement of movie search and duplicate-title selection.
- Evaluation of recommendation relevance across different genres.
- Expanded movie metadata and poster coverage.
- Further performance and interface improvements as the catalogue grows.
Built with Python and a love for cinema. 🍿
