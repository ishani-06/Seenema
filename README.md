# 🎬 Seenema

### Discover your next favourite movie.

Seenema is a content-based movie recommendation system that helps users discover films similar to the ones they love. Built with Python, FastAPI, and Streamlit, the project uses TF-IDF vectorization and cosine similarity to recommend movies based on their metadata.

The project uses [The Movie Database (TMDB)](https://www.themoviedb.org/) as its movie metadata source during offline dataset creation. Movie details and poster URLs are stored locally, allowing recommendations to run without making TMDB API requests during normal operation.

> **Project status:** Under development.

---

## ✨ Planned Features

- 🔎 **Movie Search** — Search and select movies from our locally maintained catalogue.
- 🎯 **Content-Based Recommendations** — Discover similar movies using TF-IDF and cosine similarity.
- 🖼️ **Movie Posters** — Display posters using image URLs stored in the dataset.
- 🎬 **Movie Details** — Explore movie descriptions, genres, cast, directors, and release information.
- ⚡ **FastAPI Backend** — Serve movie search, details, and recommendation requests through a REST API.
- 🎨 **Streamlit Frontend** — A minimal, elegant interface for discovering movies.

---

## 🧠 Recommendation System

Seenema uses **content-based filtering** to identify movies with similar characteristics.

The planned recommendation pipeline is:

1. Collect movie metadata from TMDB using offline ingestion scripts.
2. Clean and normalize the collected data into our own movie dataset.
3. Combine selected movie attributes into a text representation.
4. Apply TF-IDF vectorization to transform movie metadata into numerical feature vectors.
5. Calculate cosine similarity between the selected movie and other movies.
6. Return the highest-ranked recommendations to the frontend.

### Example

Selecting *The Godfather* could return movies such as *Goodfellas* or *Scarface* if their metadata produces sufficiently high similarity scores.

These are illustrative examples, not measured model results.

---

## 🏗️ Architecture

```text
                   OFFLINE DATA PIPELINE

                    TMDB REST API
                          |
                          v
                 Data Ingestion Pipeline
                          |
                          v
                   Movie Dataset
                          |
                          v
                 TF-IDF Vectorization
                          |
                          v
                 Saved ML Artifacts


                    RUNTIME APPLICATION

                  Streamlit Frontend
                          |
                          | HTTP / REST
                          v
                    FastAPI Backend
                          |
                +---------+---------+
                |         |         |
                v         v         v
              Search    Details   Recommender
                                    |
                                    v
                            Cosine Similarity
                                    |
                                    v
                          Local Dataset + Model
```

### Design Principles

- **KISS:** Keep the architecture simple and maintainable.
- **Local-first recommendations:** No TMDB API calls during normal application operation.
- **Separation of concerns:** The frontend and backend communicate through documented API contracts.
- **No user database:** No accounts, user profiles, or collaborative filtering in the initial scope.
- **Flexible schema:** The movie dataset can evolve as project requirements change.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application and ML logic |
| Streamlit | Frontend interface |
| FastAPI | Backend REST API |
| scikit-learn | TF-IDF vectorization and similarity calculations |
| pandas | Dataset processing and manipulation |
| NumPy / SciPy | Numerical operations and sparse matrices |
| TMDB API | Offline movie metadata collection |
| Git & GitHub | Version control and collaboration |

---

## 📁 Planned Project Structure

```text
seenema/
├── frontend/
│   ├── app.py
│   ├── api_client.py
│   ├── pages/
│   └── components/
├── backend/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── ml/
│   └── ingestion/
├── data/
│   └── README.md
├── artifacts/
│   └── README.md
├── tests/
│   ├── frontend/
│   └── backend/
├── docs/
│   ├── HLD.md
│   └── API_SPEC.md
├── .env.example
├── .gitignore
└── README.md
```

This structure is a proposed layout and may change during implementation.

---

## 🔌 Backend API

The backend will expose versioned REST endpoints under `/api/v1`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Check whether the API process is running |
| GET | `/api/v1/ready` | Check whether the dataset and model are ready |
| GET | `/api/v1/movies/search` | Search the local movie catalogue |
| GET | `/api/v1/movies/{movie_id}` | Retrieve movie details |
| GET | `/api/v1/movies/{movie_id}/recommendations` | Retrieve similar movies |

The API contract is documented separately in `docs/API_SPEC.md`.

---

## 🚀 Getting Started

> Setup instructions will be finalized once the application structure and implementation are in place.

### Prerequisites

- Python 3.11 or a compatible Python version selected for the project.
- Git.
- A TMDB API Read Access Token for offline dataset generation.

### Planned Setup

```bash
git clone <repository-url>
cd seenema

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

On Windows, activate the environment using:

```powershell
.venv\Scripts\Activate.ps1
```

The repository URL, dependency file, environment variables, and startup commands will be finalized during implementation.

**Important:** The TMDB token is required only for the offline ingestion workflow, not for normal application operation.

---

## 📚 Documentation

- [High-Level Design](docs/HLD.md)
- [API & Integration Specification](docs/API_SPEC.md)

These documents will be maintained as the architecture evolves.

---

## 🎞️ Data Attribution

Movie metadata and poster imagery are sourced from [TMDB](https://www.themoviedb.org/).

Seenema is not endorsed or certified by TMDB. Applicable TMDB attribution, branding, and API usage requirements will be followed.

---

## 📌 Current Status

Seenema is in the planning and development stage.

The initial architecture and recommendation approach have been selected. Dataset generation, ML implementation, backend endpoints, and frontend development remain to be completed.

**Built with Python and a love for cinema. 🍿**
