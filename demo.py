
import pandas as pd

df = pd.read_csv("data/movie_metadata.csv")

def fix_poster_url(url):
    if pd.isna(url) or not isinstance(url, str) or not url.strip():
        return None

    url = url.strip()

    # Fix the missing slash after the TMDB image size.
    url = url.replace(
        "https://image.tmdb.org/t/p/w500",
        "https://image.tmdb.org/t/p/w500/",
        1
    ) if url.startswith("https://image.tmdb.org/t/p/w500") else url

    # Prevent duplicate slashes after w500/
    url = url.replace("w500//", "w500/")

    return url

df["poster_url"] = df["poster_url"].apply(fix_poster_url)

df.to_csv("data/movie_metadata.csv", index=False)

print("Poster URLs fixed and CSV saved!")
print(df[["display_title", "poster_url"]].head(10).to_string(index=False))
