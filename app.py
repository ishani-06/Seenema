import base64
from json import load
import os
import streamlit as st
import pickle
from pathlib import Path
import pandas as pd
from streamlit_searchbox import st_searchbox
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="Seenema — Your Next Great Watch",
    page_icon="assets/logo.png",
    layout="wide",
)

# Assets

@st.cache_data
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_base64 = get_base64_image("assets/hero.png" )
logo_base64 = get_base64_image("assets/logo.png")

# Metadata
@st.cache_data
def load_metadata():
    return pd.read_csv("data/movie_metadata.csv")


movieMetadata = load_metadata()

# Model
@st.cache_resource
def load_recommender():
    model_path = Path("./backend/movie_recommender.pkl")

    with open(model_path, "rb") as file:
        return pickle.load(file)


recommenderModel = load_recommender()

movies = recommenderModel["movies"]
tfidf = recommenderModel["tfidf_vectorizer"]
tfidf_matrix = recommenderModel["tfidf_matrix"]


def recommend_by_id(movie_id, n=5):
    # Match IDs as strings to avoid int/string mismatches.
    matches = movies.index[
        movies["movie_id"].astype(str) == str(movie_id)
    ].tolist()

    if not matches:
        return pd.DataFrame()

    movie_index = matches[0]
    selected_title = (
        str(movies.iloc[movie_index]["title"]).strip().casefold()
    )

    # Calculate similarity against every movie.
    similarities = cosine_similarity(
        tfidf_matrix[movie_index],
        tfidf_matrix,
    ).ravel()

    ranked_indices = similarities.argsort()[::-1]

    # Exclude the selected movie and other records with the same title.
    ranked_indices = [
        i for i in ranked_indices
        if (
            i != movie_index
            and str(movies.iloc[i]["title"]).strip().casefold()
            != selected_title
        )
    ][:max(0, n)]

    results = movies.iloc[ranked_indices][
        ["movie_id", "title"]
    ].copy()

    results["similarity"] = similarities[ranked_indices]

    return results.reset_index(drop=True)



# Search Engine

@st.cache_data
def build_title_index(title_list):
    # Store original titles alongside normalized search strings.
    return [
        (title, title.casefold())
        for title in title_list
    ]

titles = movieMetadata["display_title"]

title_index = build_title_index(tuple(titles))

MIN_QUERY_LENGTH = 1
MAX_SUGGESTIONS = 40

# def search_movie_titles(searchterm: str) -> list[str]:
#     query = (searchterm or "").strip().casefold()

#     # Do not return suggestions until three characters are entered.
#     if len(query) < MIN_QUERY_LENGTH:
#         return []

#     prefix_matches = []
#     substring_matches = []

#     for title, normalized_title in title_index:
#         if normalized_title.startswith(query):
#             prefix_matches.append(title)

#             if len(prefix_matches) >= MAX_SUGGESTIONS:
#                 return prefix_matches

#         elif (
#             query in normalized_title
#             and len(substring_matches) < MAX_SUGGESTIONS
#         ):
#             substring_matches.append(title)

#     # Prioritize titles that begin with the query.
#     remaining = MAX_SUGGESTIONS - len(prefix_matches)

#     return prefix_matches + substring_matches[:remaining]


def search_movie_titles(searchterm: str) -> list[str]:
    query = (searchterm or "").strip().casefold()

    if len(query) < MIN_QUERY_LENGTH:
        return []

    prefix_matches = []
    substring_matches = []

    for title, normalized_title in title_index:
        if normalized_title.startswith(query):
            prefix_matches.append(title)

            if len(prefix_matches) >= MAX_SUGGESTIONS:
                return prefix_matches

        elif query in normalized_title:
            substring_matches.append(title)

            if len(substring_matches) >= MAX_SUGGESTIONS:
                break

    remaining = MAX_SUGGESTIONS - len(prefix_matches)
    return prefix_matches + substring_matches[:remaining]


# Main Page

with st.container(horizontal_alignment="center"):
    st.html(f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-top: 0px; margin-right: 0px;">
            <img src="data:image/png;base64,{logo_base64}" style="height: 75px; width: auto; margin-right: 0px;" />
            <div style="display: flex; margin-top: 15px">
                <p style="font-size: 55px; font-weight: bold; color: #f2e4c4">Seen</p>
                <p style="font-size: 55px; font-weight: bold; color: #ecb235">ema</p>
            </div>
        </div>
        <hr style="background-color: #ecb235; height: 2px; border: none">
    """)

st.html(f"""
    <div style="
        background-image: linear-gradient(to right, rgba(6, 18, 14, 0.98) 35%, rgba(6, 18, 14, 0.6) 65%, rgba(6, 18, 14, 0.1) 100%), 
                          url('data:image/png;base64,{img_base64}');
        background-size: cover;
        background-position: right center;
        background-repeat: no-repeat;
        width: 91.7vw;
        padding: 4rem 6rem;
        font-family: 'Source Sans Pro', sans-serif;
        box-sizing: border-box;
    ">
        <div style="
            color: #8fa097;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1.5px;
            margin-bottom: 0.5rem;
        ">
            More Stories For You
        </div>
        
        <h1 style="
            font-size: 3.5rem;
            font-weight: 700;
            line-height: 1.1;
            margin: 0;
            color: #f2e4c4;
        ">
            Find your next<br><span style="color: #ecb235;">great watch.</span>
        </h1>
        
        <p style="
            color: #b3c3bb;
            font-size: 1.1rem;
            margin-top: 1rem;
            margin-bottom: 0;
            max-width: 500px;
        ">
            Get movie recommendations powered by machine learning. Discover films similar to what you love.
        </p>
    </div>
""")

with st.container():
    col_input, col_btn = st.columns([0.90, 0.1], gap="xxsmall", vertical_alignment="top")

    with col_input:
        
        search_query = st_searchbox(
            search_function=search_movie_titles,
            placeholder="Search for any movie…",
            label=None,
            key="seenema_movie_search",
            debounce=250,
            edit_after_submit="option",
            style_overrides={
                "searchbox": {
                    "control": {
                        "backgroundColor": "#061a13",
                        "borderColor": "#ecb235",
                        "borderRadius": "10px",
                        "minHeight": "48px",
                        "boxShadow": "none",
                    },
                    "input": {
                        "color": "#f2e4c4",
                        "fontFamily": "Inter, Arial, sans-serif",
                        "fontSize": "16px",
                        "letterSpacing": "normal",
                        "wordSpacing": "normal",
                    },
                    "placeholder": {
                        "color": "#8fa097",
                        "fontFamily": "Inter, Arial, sans-serif",
                        "fontSize": "16px",
                    },
                    "singleValue": {
                        "color": "#f2e4c4",
                        "fontFamily": "Inter, Arial, sans-serif",
                        "fontSize": "16px",
                        "letterSpacing": "normal",
                        "wordSpacing": "normal",
                    },
                    "menu": {
                        "backgroundColor": "#10251d",
                        "border": "1px solid #294438",
                        "borderRadius": "10px",
                        "overflow": "hidden",
                    },
                    "menuList": {
                        "backgroundColor": "#10251d",
                        "maxHeight": "260px",
                        "padding": "4px",
                    },
                    "option": {
                        "color": "#f2e4c4",
                        "backgroundColor": "#10251d",
                        "fontFamily": "Inter, Arial, sans-serif",
                        "fontSize": "15px",
                        "fontWeight": "400",
                        "letterSpacing": "normal",
                        "wordSpacing": "normal",
                        "padding": "9px 12px",
                        "highlightColor": "#ecb235",
                    },
                    "optionEmpty": "hidden",
                },
            },
        )


    with col_btn:
        search_clicked = st.button("Recommend Movies →", use_container_width=True, type="primary")

st.html("""
    <style>
    div[data-testid="stButton"] button {
        background-color: #F3B73E;
        color: #06120E;
        border: 1px solid #F3B73E;
        border-radius: 12px;
        font-weight: 600;
        font-size: 18px;
        height: 40px;
        transition: background-color 0.2s ease;
    }

    div[data-testid="stButton"] button:hover {
        background-color: #d19a28;
        border-color: #d19a28;
        color: #06120E;
    }
    </style>
""")


if search_clicked:
    if not search_query:
        st.write("Please select a movie first.")
    else:
        # Resolve the selected display title to its exact movie ID.
        selected_rows = movieMetadata[
            movieMetadata["display_title"] == search_query
        ]

        if selected_rows.empty:
            st.write("Could not find the selected movie in the metadata.")
        else:
            selected_movie = selected_rows.iloc[0]
            selected_id = selected_movie["movie_id"]

            st.subheader(
                f"Since you watched {selected_movie['display_title']}"
            )

            recommendations = recommend_by_id(selected_id, n=5)

            if recommendations.empty:
                st.info("No recommendations were found.")
            else:
                # Attach poster and display metadata using movie ID.
                metadata = movieMetadata.copy()
                metadata["_id_key"] = metadata["movie_id"].astype(str)

                recommendations["_id_key"] = (
                    recommendations["movie_id"].astype(str)
                )

                recommendations = recommendations.merge(
                    metadata[
                        [
                            "_id_key",
                            "display_title",
                            "poster_url",
                        ]
                    ].drop_duplicates("_id_key"),
                    on="_id_key",
                    how="left",
                )
                columns = st.columns(5)

                for column, (_, movie) in zip(
                    columns, recommendations.iterrows()
                ):
                    with column:
                        if pd.notna(movie["poster_url"]) and movie["poster_url"]:
                            st.image(movie["poster_url"], use_container_width=True)
                        else:
                            st.caption("Poster unavailable")

                        st.markdown(f"**{movie['display_title']}**")
                        st.caption(
                            f"Similarity: {movie['similarity']:.3f}"
                        )
