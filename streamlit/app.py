import datetime
import sys
from pathlib import Path

import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from webapp.recommender import get_data, get_model, recommend_books


def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        creds_dict = dict(st.secrets["gcp"])
    except Exception:
        return None

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception:
        return None


def log_to_sheet(tab_name, row_data):
    client = get_gsheet_client()
    if client is None:
        return False

    try:
        sheet = client.open_by_key("1JYzcT53ogOg7t4fhZJMZQ16QPcFgRvrQSWWHbQ5n5IQ").worksheet(tab_name)
        sheet.append_row(row_data)
        return True
    except Exception:
        return False


@st.cache_resource
def load_runtime():
    model = get_model()
    data = get_data()
    return model, data


model, data_info = load_runtime()

st.title("Semantic Book Recommender")
st.write(
    "Provide a detailed description of the book you are looking for, "
    "and Bookwise AI will search the semantic embedding catalog for the closest matches."
)
st.caption(f"Catalog: {data_info['version']} · {len(data_info['df'])} books · {model._bookwise_model_name}")

user_input = st.text_input("What kind of book are you looking for?")
top_n = st.slider("How many recommendations?", 1, 10, 5)

if st.button("Get Recommendations") and user_input:
    log_to_sheet("QueryLogs", [str(datetime.datetime.now()), user_input])

    try:
        with st.spinner("Finding the best book matches..."):
            response = recommend_books(user_input, top_n)
            st.session_state.results = response["recommendations"]
            st.session_state.query = user_input
            st.session_state.logged_feedback = set()
    except Exception as exc:
        st.error("Something went wrong. Please try again.")
        log_to_sheet("QueryLogs", [str(datetime.datetime.now()), f"ERROR: {str(exc)}"])

if "results" in st.session_state:
    st.success(f"Top {len(st.session_state.results)} recommendations for you:")

    for i, row in enumerate(st.session_state.results):
        left_col, right_col = st.columns([1, 3])

        with left_col:
            if row.get("image_url"):
                st.image(row["image_url"], width=120)

        with right_col:
            st.markdown(f"### {row['title']}")
            st.markdown(f"**Author:** {row.get('authors', '')}")
            st.markdown(f"**Rating:** {row.get('average_rating') or 'N/A'}")
            st.markdown(f"**Match Score:** {row.get('match_score')}")
            st.markdown(f"{row.get('description', '')[:350]}...")
            if row.get("subjects"):
                st.caption(row["subjects"])
            st.markdown(f"[More Info on Google](<{row['google_url']}>)")

            feedback = st.radio(
                "Was this helpful?",
                ["Yes", "No"],
                key=f"feedback_{i}",
                index=None,
            )

            feedback_key = f"{st.session_state.query}-{row['title']}"
            if feedback and feedback_key not in st.session_state.logged_feedback:
                log_to_sheet(
                    "FeedbackLogs",
                    [
                        str(datetime.datetime.now()),
                        st.session_state.query,
                        row["title"],
                        feedback,
                    ],
                )
                st.session_state.logged_feedback.add(feedback_key)
                st.success("Feedback recorded.")

        st.markdown("---")

st.markdown(
    """
    Want to learn more about how this app works?

    [Visit the GitHub repository](https://github.com/sntk-76/bookwise-ai).
    """
)
