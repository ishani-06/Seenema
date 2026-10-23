
import base64
import os
import pickle
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_searchbox import st_searchbox


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Seenema — Your Next Great Watch",
    page_icon="assets/logo.png",
    layout="wide",
)


# --------------------------------------------------
# ASSETS
# --------------------------------------------------

@st.cache_data
def get_base64_image(image_path):
    path = Path(image_path)

    if path.exists():
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    return ""


img_base64 = get_base64_image("assets/hero.png")
logo_base64 = get_base64_image("assets/logo.png")


# --------------------------------------------------
# METADATA
# --------------------------------------------------

@st.cache_data
def load_metadata():
    return pd.read_csv("data/movie_metadata.csv")


movieMetadata = load_metadata()


# --------------------------------------------------
# MODEL
# --------------------------------------------------

@st.cache_resource
def load_recommender():
    model_path = Path("./backend/movie_recommender.pkl")

    with open(model_path, "rb") as file:
        return pickle.load(file)


recommenderModel = load_recommender()


# --------------------------------------------------
# MOVIE SEARCH INDEX
# --------------------------------------------------

@st.cache_data
def build_title_index(title_list):
    # Store original titles alongside normalized search strings.
    return [
        (title, title.casefold())
        for title in title_list
    ]


titles = (
    movieMetadata["display_title"]
    .dropna()
    .astype(str)
    .str.strip()
)

titles = titles[titles.ne("")].drop_duplicates().tolist()

title_index = build_title_index(tuple(titles))

MIN_QUERY_LENGTH = 1
MAX_SUGGESTIONS = 40


def search_movie_titles(searchterm: str) -> list[str]:
    query = (searchterm or "").strip().casefold()

    # Do not return suggestions until three characters are entered.
    if len(query) < MIN_QUERY_LENGTH:
        return []

    prefix_matches = []
    substring_matches = []

    for title, normalized_title in title_index:
        if normalized_title.startswith(query):
            prefix_matches.append(title)

            if len(prefix_matches) >= MAX_SUGGESTIONS:
                return prefix_matches

        elif (
            query in normalized_title
            and len(substring_matches) < MAX_SUGGESTIONS
        ):
            substring_matches.append(title)

    # Prioritize titles that begin with the query.
    remaining = MAX_SUGGESTIONS - len(prefix_matches)

    return prefix_matches + substring_matches[:remaining]


# --------------------------------------------------
# MAIN PAGE — HEADER
# --------------------------------------------------

with st.container(horizontal_alignment="center"):
    st.html(f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 0;
            margin-right: 0;
        ">
            <img
                src="data:image/png;base64,{logo_base64}"
                style="height: 75px; width: auto; margin-right: 0;"
            />
            <div style="display: flex; margin-top: 15px;">
                <p style="
                    font-size: 55px;
                    font-weight: bold;
                    color: #f2e4c4;
                ">Seen</p>
                <p style="
                    font-size: 55px;
                    font-weight: bold;
                    color: #ecb235;
                ">ema</p>
            </div>
        </div>
        <hr style="
            background-color: #ecb235;
            height: 2px;
            border: none;
        ">
    """)


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.html(f"""
    <div style="
        background-image:
            linear-gradient(
                to right,
                rgba(6, 18, 14, 0.98) 35%,
                rgba(6, 18, 14, 0.6) 65%,
                rgba(6, 18, 14, 0.1) 100%
            ),
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
            Find your next<br>
            <span style="color: #ecb235;">great watch.</span>
        </h1>

        <p style="
            color: #b3c3bb;
            font-size: 1.1rem;
            margin-top: 1rem;
            margin-bottom: 0;
            max-width: 500px;
        ">
            Get movie recommendations powered by machine learning.
            Discover films similar to what you love.
        </p>
    </div>
""")


# --------------------------------------------------
# SEARCH BAR + RECOMMEND BUTTON
# --------------------------------------------------

with st.container():
    col_input, col_btn = st.columns(
        [0.90, 0.10],
        gap="xxsmall",
        vertical_alignment="bottom",
    )

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
                        "backgroundColor": "rgba(6, 18, 14, 0.6)",
                        "borderColor": "rgba(143, 160, 151, 0.3)",
                        "borderRadius": "12px",
                        "minHeight": "48px",
                        "boxShadow": "none",
                    },
                    "placeholder": {
                        "color": "rgba(143, 160, 151, 0.6)",
                        "fontSize": "18px",
                    },
                    "input": {
                        "color": "#f5e9d1",
                        "fontSize": "18px",
                    },
                    "singleValue": {
                        "color": "#f5e9d1",
                        "fontSize": "18px",
                    },
                    "menu": {
                        "backgroundColor": "#10231b",
                        "border": "1px solid rgba(143, 160, 151, 0.3)",
                    },
                    "option": {
                        "color": "#f2e4c4",
                        "backgroundColor": "#10231b",
                        "highlightColor": "#ecb235",
                    },
                    "optionEmpty": "hidden",
                },
            },
        )

    with col_btn:
        search_clicked = st.button(
            "Recommend Movies →",
            use_container_width=True,
            type="primary",
        )


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.html("""
    <style>
    div[data-testid="stButton"] button {
        background-color: #F3B73E;
        color: #06120E;
        border: 1px solid #F3B73E;
        border-radius: 12px;
        font-weight: 600;
        font-size: 18px;
        height: 48px;
        transition: background-color 0.2s ease;
    }

    div[data-testid="stButton"] button:hover {
        background-color: #d19a28;
        border-color: #d19a28;
        color: #06120E;
    }
    </style>
""")


# --------------------------------------------------
# RECOMMENDATION HANDLER
# --------------------------------------------------

if search_clicked:
    if not isinstance(search_query, str) or not search_query.strip():
        st.warning("Please select a movie first.")
    else:
        movie_name = search_query.strip()

        st.write(f"Searching for: **{movie_name}**")

        # Connect your existing recommendation function here.
        # recommenderModel is already loaded above.
