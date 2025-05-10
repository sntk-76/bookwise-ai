import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --------------------------
# Google Sheets logging setup
# --------------------------
def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = dict(st.secrets["gcp"])  # Get credentials from Streamlit secrets
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

def log_to_sheet(tab_name, row_data):
    client = get_gsheet_client()
    sheet = client.open_by_key("1JYzcT53ogOg7t4fhZJMZQ16QPcFgRvrQSWWHbQ5n5IQ").worksheet(tab_name)
    sheet.append_row(row_data)

# --------------------------
# Load model and data
# --------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer('streamlit/all-MiniLM-L6-v2')

@st.cache_data
def load_data():
    df = pd.read_csv("streamlit/enriched_data.csv")
    vectors = np.load("streamlit/embeddings.npy")

    return df, vectors

model = load_model()
df, book_vectors = load_data()

# --------------------------
# App UI
# --------------------------
st.title("📚 Semantic Book Recommender")
st.write(
    "Provide a detailed description of the book you're looking for, "
    "and we'll use our AI engine powered by BERT to find the most relevant titles."
)

user_input = st.text_input("📝 What kind of book are you looking for?")
top_n = st.slider("How many recommendations?", 1, 10, 5)

if st.button("Get Recommendations") and user_input:
    log_to_sheet("QueryLogs", [str(datetime.datetime.now()), user_input])

    try:
        with st.spinner("🔎 Finding the best book matches..."):
            user_vec = model.encode([user_input])
            scores = cosine_similarity(user_vec, book_vectors)[0]
            top_indices = scores.argsort()[-top_n:][::-1]
            results = df.iloc[top_indices].copy()
            results["similarity"] = scores[top_indices]

            st.session_state.results = results
            st.session_state.query = user_input
            st.session_state.logged_feedback = set()

    except Exception as e:
        st.error("Something went wrong. Please try again.")
        log_to_sheet("QueryLogs", [str(datetime.datetime.now()), f"ERROR: {str(e)}"])

# --------------------------
# Show Recommendations
# --------------------------
if "results" in st.session_state:
    st.success(f"Top {top_n} recommendations for you:")

    for i, row in st.session_state.results.iterrows():
        left_col, right_col = st.columns([1, 3])

        with left_col:
            st.image(row['image_url'], width=120)

        with right_col:
            st.markdown(f"### {row['title']}")
            st.markdown(f"**Author:** {row['authors']}")
            st.markdown(f"**Rating:** {row['average_rating']} ⭐")
            st.markdown(f"**Similarity Score:** {row['similarity']:.2f}")
            st.markdown(f"{row['description'][:350]}...")

            query_title = row['title'].replace(" ", "+")
            google_url = f"https://www.google.com/search?q={query_title}+book"
            st.markdown(f"[📖 More Info on Google](<{google_url}>)")

            feedback = st.radio(
                f"Was this helpful?",
                ["👍 Yes", "👎 No"],
                key=f"feedback_{i}",
                index=None
            )

            feedback_key = f"{st.session_state.query}-{row['title']}"
            if feedback and feedback_key not in st.session_state.logged_feedback:
                log_to_sheet("FeedbackLogs", [
                    str(datetime.datetime.now()),
                    st.session_state.query,
                    row['title'],
                    feedback
                ])
                st.session_state.logged_feedback.add(feedback_key)
                st.success("✅ Feedback recorded!")

        st.markdown("---")

# --------------------------
# GitHub link
# --------------------------
st.markdown(
    """
    **ℹ️ Want to learn more about how this app works?**

    If you're interested in the workflow, data processing steps, and full source code,  
    [click here to visit the GitHub repository](https://github.com/sntk-76/bookwise-ai).
    """
)
