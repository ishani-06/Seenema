import os

import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TMDB_API_READ_ACCESS_TOKEN")

if not token:
    raise SystemExit("TMDB token missing. Check your backend/.env file.")

response = requests.get(
    "https://api.themoviedb.org/3/configuration",
    headers={
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
    },
    timeout=15,
)

if response.ok:
    data = response.json()
    print("TMDB authentication successful!")
    print("Image base URL:", data["images"]["secure_base_url"])
else:
    print("TMDB request failed.")
    print("HTTP status:", response.status_code)
    print("Response:", response.text[:300])