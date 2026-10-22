
import csv
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
DATA = ROOT / "data"
RAW = DATA / "raw"
CHECKPOINTS = DATA / "checkpoints"

IDS_FILE = CHECKPOINTS / "movie_ids.jsonl"
PROCESSED_FILE = CHECKPOINTS / "processed_ids.jsonl"
OUTPUT_FILE = RAW / "movies_raw.csv"
STATE_FILE = CHECKPOINTS / "build_discovery_state.json"

API = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"

WORKERS = 5

LANGUAGES = [
    "hi", "en", "bn", "te", "ta", "ml", "kn", "mr",
    "pa", "gu", "or", "as", "ur", "ja", "ko", "fr",
    "es", "de", "it", "zh", "pt", "ar", "th", "id",
]

PERIODS = [
    (1900, 1969),
    (1970, 1989),
    (1990, 2009),
    (2010, 2017),
    (2018, 2022),
    (2023, 2026),
]

COLUMNS = [
    "movie_id",
    "title",
    "overview",
    "release_date",
    "genres",
    "keywords",
    "runtime",
    "vote_average",
    "vote_count",
    "poster_url",
]

load_dotenv(BACKEND / ".env")
TOKEN = os.getenv("TMDB_API_READ_ACCESS_TOKEN")


# --------------------------------------------------
# API
# --------------------------------------------------

def fetch(path, **params):
    """Make a TMDB request with retries."""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "accept": "application/json",
    }

    for attempt in range(6):
        try:
            response = requests.get(
                f"{API}/{path.lstrip('/')}",
                headers=headers,
                params=params,
                timeout=30,
            )

            if response.status_code == 404:
                return None

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == 5:
                    response.raise_for_status()

                retry_after = response.headers.get("Retry-After")
                try:
                    delay = min(float(retry_after), 120)
                except (TypeError, ValueError):
                    delay = min(2 ** attempt, 60)

                time.sleep(delay)
                continue

            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(min(2 ** attempt, 30))

    return None


# --------------------------------------------------
# Checkpoints
# --------------------------------------------------

def read_ids(path):
    ids = set()

    if path.exists():
        with path.open(encoding="utf-8") as file:
            for line in file:
                try:
                    value = json.loads(line)
                    if isinstance(value, dict):
                        value = value["movie_id"]
                    ids.add(int(value))
                except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                    continue

    return ids


def save_id(path, movie_id):
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(movie_id) + "\n")
        file.flush()


# --------------------------------------------------
# Discovery
# --------------------------------------------------

def discover_movies(target):
    ids = read_ids(IDS_FILE)

    if len(ids) >= target:
        print(f"Using {len(ids):,} existing discovered IDs.")
        return

    queries = [
        {
            "with_original_language": language,
            "primary_release_date.gte": f"{start}-01-01",
            "primary_release_date.lte": f"{end}-12-31",
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "include_video": "false",
        }
        for language in LANGUAGES
        for start, end in PERIODS
    ]

    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if state["query_count"] != len(queries):
            raise RuntimeError(
                "Discovery configuration changed. Back up the checkpoint "
                "before resetting build_discovery_state.json."
            )
    else:
        state = {
            "query_count": len(queries),
            "pages": [1] * len(queries),
            "done": [False] * len(queries),
        }

    while len(ids) < target and not all(state["done"]):
        progressed = False

        for index, query in enumerate(queries):
            if len(ids) >= target:
                break

            if state["done"][index]:
                continue

            page = state["pages"][index]

            if page > 500:
                state["done"][index] = True
                continue

            try:
                result = fetch(
                    "/discover/movie",
                    page=page,
                    **query,
                )
            except requests.RequestException as error:
                STATE_FILE.write_text(
                    json.dumps(state, indent=2), encoding="utf-8"
                )
                raise RuntimeError(
                    "Discovery interrupted. Rerun the same command to resume."
                ) from error

            if not result:
                state["done"][index] = True
                continue

            for movie in result.get("results", []):
                movie_id = movie.get("id")
                if movie_id and movie_id not in ids:
                    save_id(IDS_FILE, movie_id)
                    ids.add(movie_id)

            state["pages"][index] = page + 1

            if (
                page >= min(result.get("total_pages", 0), 500)
                or not result.get("results")
            ):
                state["done"][index] = True

            STATE_FILE.write_text(
                json.dumps(state, indent=2), encoding="utf-8"
            )

            progressed = True
            print(f"\rDiscovered {len(ids):,}/{target:,}", end="", flush=True)

        if not progressed:
            break

    print(f"\nDiscovery IDs available: {len(ids):,}")


# --------------------------------------------------
# Movie metadata
# --------------------------------------------------

def get_movie(movie_id):
    movie = fetch(
        f"/movie/{movie_id}",
        append_to_response="keywords",
    )

    if not movie:
        return None

    keywords = movie.get("keywords") or {}

    return {
        "movie_id": movie["id"],
        "title": movie.get("title") or movie.get("original_title") or "",
        "overview": (movie.get("overview") or "").strip(),
        "release_date": movie.get("release_date") or "",
        "genres": json.dumps(
            [g["name"] for g in movie.get("genres", []) if g.get("name")],
            ensure_ascii=False,
        ),
        "keywords": json.dumps(
            [k["name"] for k in keywords.get("keywords", []) if k.get("name")],
            ensure_ascii=False,
        ),
        "runtime": movie.get("runtime"),
        "vote_average": movie.get("vote_average"),
        "vote_count": movie.get("vote_count"),
        "poster_url": (
            f"{POSTER_BASE}{movie['poster_path'].lstrip('/')}"
            if movie.get("poster_path") else ""
        ),
    }


# --------------------------------------------------
# Preserve existing CSV while removing cast/director
# --------------------------------------------------

def prepare_output():
    if not OUTPUT_FILE.exists() or OUTPUT_FILE.stat().st_size == 0:
        with OUTPUT_FILE.open(
            "w", newline="", encoding="utf-8-sig"
        ) as file:
            csv.DictWriter(file, fieldnames=COLUMNS).writeheader()
        return

    # Rewrite existing rows with the new schema before appending.
    temp = OUTPUT_FILE.with_suffix(".tmp")

    with OUTPUT_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as source, temp.open(
        "w", newline="", encoding="utf-8-sig"
    ) as destination:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(destination, fieldnames=COLUMNS)
        writer.writeheader()

        for row in reader:
            writer.writerow({column: row.get(column, "") for column in COLUMNS})

    temp.replace(OUTPUT_FILE)


# --------------------------------------------------
# Build dataset
# --------------------------------------------------

def build_dataset(target):
    if not TOKEN:
        raise RuntimeError(
            "TMDB_API_READ_ACCESS_TOKEN is missing from backend/.env"
        )

    RAW.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)

    # Validate authentication.
    fetch("/configuration")

    discover_movies(target)

    ids = read_ids(IDS_FILE)
    processed = read_ids(PROCESSED_FILE)

    prepare_output()

    pending = sorted(ids - processed)
    print(f"Already processed: {len(processed):,}")
    print(f"Remaining: {len(pending):,}")

    saved = 0
    failures = 0

    with OUTPUT_FILE.open(
        "a", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)

        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {
                executor.submit(get_movie, movie_id): movie_id
                for movie_id in pending
            }

            for count, future in enumerate(as_completed(futures), start=1):
                movie_id = futures[future]

                try:
                    row = future.result()

                    if row is not None:
                        writer.writerow(row)
                        file.flush()
                        saved += 1

                    # Mark complete after writing the result.
                    save_id(PROCESSED_FILE, movie_id)

                except Exception as error:
                    failures += 1
                    print(f"\nMovie {movie_id} failed: {error}")

                if count % 100 == 0:
                    print(
                        f"\rProcessed {count:,}/{len(pending):,} | "
                        f"Saved {saved:,} | Failed {failures:,}",
                        end="",
                        flush=True,
                    )

    print("\nDataset build pass finished.")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Successful records this run: {saved:,}")
    print(f"Failures this run: {failures:,}")
    print("Rerun the same command to retry unprocessed IDs.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=35000)
    args = parser.parse_args()

    if args.target < 1:
        parser.error("--target must be positive")

    build_dataset(args.target)
