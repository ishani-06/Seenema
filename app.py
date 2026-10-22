import base64
import os
import streamlit as st

st.set_page_config(
    page_title="Seenema — Your Next Great Watch",
    page_icon="assets/logo.png",
    layout="wide",
)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

image_path = "assets/hero.png" 
img_base64 = get_base64_image(image_path)

logo_path = "assets/logo.png"
logo_base64 = get_base64_image(logo_path)

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
    col_input, col_btn = st.columns([0.90, 0.1], gap="xxsmall", vertical_alignment="bottom")

    with col_input:
        # label_visibility="collapsed" completely hides the default top label space
        search_query = st.text_input(
            "Search", 
            placeholder="Search for a movie, actor, or genre...", 
            label_visibility="collapsed"
        )

    with col_btn:
        search_clicked = st.button("Recommend Movies →", use_container_width=True, type="primary")

st.html("""
    <style>
    div[data-testid="stTextInput"] input {
        background-color: rgba(6, 18, 14, 0.6) !important;
        color: #f5e9d1 !important;
        border: 1px solid rgba(143, 160, 151, 0.3) !important;
        border-right: none !important;
        border-top-left-radius: 12px !important;
        border-bottom-left-radius: 12px !important;
        border-top-right-radius: 0px !important;
        border-bottom-right-radius: 0px !important;
        padding: 0.75rem 1rem !important;
        height: 48px !important;
        font-size: 18px !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #F3B73E !important;
        box-shadow: 0 0 0 1px #F3B73E !important;
    }
    
    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(143, 160, 151, 0.6);
        font-size: 18px;
    }

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

if search_query or search_clicked:
    movie_name = search_query.strip()

    if movie_name:
        st.write(f"Searching for: **{movie_name}**")