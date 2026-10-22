
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Paths and configuration
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent

INPUT_CSV = PROJECT_ROOT / "data" / "raw" / "movies_raw.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "raw" / "movies_raw_enriched.csv"
CHECKPOINT_FILE = PROJECT_ROOT / "data" / "checkpoints" / "credits_checkpoint.jsonl"

WORKERS = 5
MAX_RETRIES = 5
REQUEST_TIMEOUT = 30

load_dotenv(BACKEND_DIR / ".env")
TMDB_TOKEN = os.getenv("TMDB_API_READ_ACCESS_TOKEN")

if not TMDB_TOKEN:
    raise RuntimeError(
        "TMDB_API_READ_ACCESS_TOKEN was not found in backend/.env"
    )

if not INPUT_CSV.exists():
    raise FileNotFoundError(f"Input dataset not found: {INPUT_CSV}")

CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# TMDB credits request
# --------------------------------------------------

HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json",
}


def fetch_credits(movie_id):
    """Fetch the top five billed cast members and all directors."""

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == MAX_RETRIES - 1:
                    response.raise_for_status()

                retry_after = response.headers.get("Retry-After")

                try:
                    delay = float(retry_after) if retry_after else 2 ** attempt
                except ValueError:
                    delay = 2 ** attempt

                time.sleep(min(max(delay, 1), 60))
                continue

            response.raise_for_status()
            credits = response.json()

            cast_members = sorted(
                credits.get("cast", []),
                key=lambda member: member.get("order", 999999),
            )

            top_cast = [
                member["name"]
                for member in cast_members[:5]
                if member.get("name")
            ]

            directors = list(dict.fromkeys(
                member["name"]
                for member in credits.get("crew", [])
                if member.get("job") == "Director"
                and member.get("name")
            ))

            return {
                "movie_id": int(movie_id),
                "cast": " | ".join(top_cast),
                "director": " | ".join(directors),
            }

        except (requests.RequestException, ValueError):
            if attempt == MAX_RETRIES - 1:
                raise

            time.sleep(min(2 ** attempt, 30))

    raise RuntimeError(f"Could not fetch credits for movie {movie_id}")


# --------------------------------------------------
# Load successful checkpoint records
# --------------------------------------------------

def load_checkpoint():
    """Load completed movie credits so interrupted runs can resume."""

    completed = {}

    if not CHECKPOINT_FILE.exists():
        return completed

    with CHECKPOINT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                movie_id = int(record["movie_id"])

                if "cast" in record and "director" in record:
                    completed[movie_id] = {
                        "cast": record["cast"],
                        "director": record["director"],
                    }
            except (ValueError, KeyError, json.JSONDecodeError):
                continue

    return completed


# --------------------------------------------------
# Main enrichment process
# --------------------------------------------------

def main():
    df = pd.read_csv(INPUT_CSV)

    if "movie_id" not in df.columns:
        raise ValueError("The input CSV must contain a movie_id column.")

    if df["movie_id"].isna().any():
        raise ValueError(
            "Some movie_id values are missing. Fix them before enrichment."
        )

    numeric_ids = pd.to_numeric(df["movie_id"], errors="raise")

    if (numeric_ids % 1 != 0).any():
        raise ValueError("Some movie_id values are not whole numbers.")

    df["movie_id"] = numeric_ids.astype("int64")

    if df["movie_id"].duplicated().any():
        raise ValueError(
            "Duplicate movie IDs detected. Validate the dataset first."
        )

    movie_ids = df["movie_id"].tolist()
    completed = load_checkpoint()

    pending_ids = [
        movie_id for movie_id in movie_ids
        if movie_id not in completed
    ]

    print(f"Movies in dataset: {len(movie_ids):,}")
    print(f"Credits already checkpointed: {len(completed):,}")
    print(f"Movies remaining: {len(pending_ids):,}")
    print(f"Workers: {WORKERS}")

    successful_this_run = 0
    failed_ids = []

    # Only the main thread writes to the checkpoint file.
    with CHECKPOINT_FILE.open("a", encoding="utf-8") as checkpoint:
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {
                executor.submit(fetch_credits, movie_id): movie_id
                for movie_id in pending_ids
            }

            total = len(futures)

            for count, future in enumerate(as_completed(futures), start=1):
                movie_id = futures[future]

                try:
                    result = future.result()

                    checkpoint.write(
                        json.dumps(result, ensure_ascii=False) + "\n"
                    )
                    checkpoint.flush()

                    completed[movie_id] = {
                        "cast": result["cast"],
                        "director": result["director"],
                    }

                    successful_this_run += 1

                except Exception as error:
                    failed_ids.append(movie_id)
                    print(f"\nFailed movie {movie_id}: {error}")

                if count % 250 == 0 or count == total:
                    print(
                        f"Processed {count:,}/{total:,} | "
                        f"Successful: {successful_this_run:,} | "
                        f"Failed: {len(failed_ids):,}"
                    )

    # Add/refresh the two columns without changing existing fields.
    df["cast"] = df["movie_id"].map(
        lambda movie_id: completed.get(movie_id, {}).get("cast", "")
    )

    df["director"] = df["movie_id"].map(
        lambda movie_id: completed.get(movie_id, {}).get("director", "")
    )

    # Write to a separate file. The original CSV remains untouched.
    temp_output = OUTPUT_CSV.with_suffix(".tmp.csv")
    df.to_csv(temp_output, index=False, encoding="utf-8")
    temp_output.replace(OUTPUT_CSV)

    missing_credits = int(
        (
            df["cast"].eq("")
            | df["director"].eq("")
        ).sum()
    )

    print("\nCredits enrichment pass finished.")
    print(f"Successful requests this run: {successful_this_run:,}")
    print(f"Failed requests this run: {len(failed_ids):,}")
    print(f"Rows with empty cast or director: {missing_credits:,}")
    print(f"Enriched dataset: {OUTPUT_CSV}")
    print(f"Checkpoint: {CHECKPOINT_FILE}")

    if failed_ids:
        print(
            "\nSome requests failed. Rerun the same command to retry "
            "those movies; successful checkpoint records will be reused."
        )


if __name__ == "__main__":
    main()
