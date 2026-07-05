import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
STREAMLIT_DIR = ROOT / "streamlit"
OPEN_LIBRARY_SUBJECT_URL = "https://openlibrary.org/subjects/{subject}.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"

SUBJECTS = [
    "literary_fiction",
    "classic_literature",
    "fantasy",
    "science_fiction",
    "mystery",
    "thriller",
    "romance",
    "historical_fiction",
    "young_adult",
    "children",
    "biography",
    "memoir",
    "history",
    "science",
    "technology",
    "business",
    "psychology",
    "philosophy",
    "self_help",
    "poetry",
    "horror",
    "adventure",
    "dystopian",
    "crime",
    "politics",
    "travel",
    "art",
    "religion",
    "health",
    "cooking",
]


def clean_text(value: Any) -> str:
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def compact_subjects(subjects, limit=18):
    if not isinstance(subjects, list):
        return ""
    cleaned = []
    seen = set()
    for item in subjects:
        value = clean_text(item).lower()
        if not value or len(value) > 60 or value in seen:
            continue
        if any(token in value for token in ["accessible book", "protected daisy", "in library"]):
            continue
        seen.add(value)
        cleaned.append(value)
        if len(cleaned) >= limit:
            break
    return ", ".join(cleaned)


def load_existing_catalog() -> pd.DataFrame:
    path = STREAMLIT_DIR / "enriched_data.csv"
    df = pd.read_csv(path)
    out = pd.DataFrame(
        {
            "book_id": df.get("book_id", ""),
            "title": df["title"].map(clean_text),
            "authors": df["authors"].map(clean_text),
            "original_publication_year": df.get("original_publication_year", ""),
            "language_code": df.get("language_code", "eng"),
            "average_rating": df.get("average_rating", ""),
            "image_url": df.get("image_url", ""),
            "description": df["description"].map(clean_text),
            "subjects": "",
            "data_source": "GoodBooks + Google Books enrichment",
        }
    )
    return out


def fetch_subject(subject: str, limit: int) -> list[dict[str, Any]]:
    params = {"limit": limit, "details": "true"}
    response = requests.get(OPEN_LIBRARY_SUBJECT_URL.format(subject=subject), params=params, timeout=40)
    response.raise_for_status()
    return response.json().get("works", [])


def openlibrary_records(limit_per_subject: int) -> pd.DataFrame:
    rows = []
    for subject in SUBJECTS:
        print(f"Fetching Open Library subject: {subject}")
        try:
            works = fetch_subject(subject, limit_per_subject)
        except Exception as exc:
            print(f"Skipping {subject}: {exc}")
            continue
        for work in works:
            authors = ", ".join(clean_text(author.get("name", "")) for author in work.get("authors", []) if author.get("name"))
            subjects = compact_subjects(work.get("subject", []))
            title = clean_text(work.get("title", ""))
            if not title or not authors:
                continue
            cover_id = work.get("cover_id")
            rows.append(
                {
                    "book_id": clean_text(work.get("key", "")),
                    "title": title,
                    "authors": authors,
                    "original_publication_year": work.get("first_publish_year", ""),
                    "language_code": "eng",
                    "average_rating": "",
                    "image_url": f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else "",
                    "description": subjects,
                    "subjects": subjects,
                    "data_source": f"Open Library subject: {subject}",
                }
            )
        time.sleep(0.7)
    return pd.DataFrame(rows)


def build_search_text(row) -> str:
    parts = [
        f"Title: {row.get('title', '')}",
        f"Author: {row.get('authors', '')}",
        f"Subjects: {row.get('subjects', '')}",
        f"Description: {row.get('description', '')}",
        f"Published: {row.get('original_publication_year', '')}",
    ]
    return clean_text(" ".join(parts))


def latin_ratio(value: str) -> float:
    letters = re.findall(r"[^\W\d_]", value, flags=re.UNICODE)
    if not letters:
        return 1.0
    latin = re.findall(r"[A-Za-z]", "".join(letters))
    return len(latin) / len(letters)


def quality_filter(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["title"] = data["title"].map(clean_text)
    data["authors"] = data["authors"].map(clean_text)
    data["description"] = data["description"].map(clean_text)
    data["subjects"] = data["subjects"].map(clean_text)
    data = data[(data["title"].str.len() >= 2) & (data["authors"].str.len() >= 2)]
    data = data[(data["description"].str.len() >= 20) | (data["subjects"].str.len() >= 20)]
    data = data[data["title"].map(latin_ratio) >= 0.75]
    data["dedupe_key"] = (
        data["title"].str.lower().str.replace(r"[^a-z0-9]+", "", regex=True)
        + "::"
        + data["authors"].str.lower().str.replace(r"[^a-z0-9]+", "", regex=True).str[:24]
    )
    data["source_rank"] = np.where(data["data_source"].str.contains("GoodBooks", na=False), 0, 1)
    data = data.sort_values(["dedupe_key", "source_rank"]).drop_duplicates("dedupe_key", keep="first")
    data = data.drop(columns=["dedupe_key", "source_rank"])
    data["search_text"] = data.apply(build_search_text, axis=1)
    return data.reset_index(drop=True)


def encode_catalog(df: pd.DataFrame, batch_size: int) -> np.ndarray:
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        df["search_text"].tolist(),
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    return embeddings.astype(np.float32)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-per-subject", type=int, default=350)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    existing = load_existing_catalog()
    expanded = openlibrary_records(args.limit_per_subject)
    catalog = quality_filter(pd.concat([existing, expanded], ignore_index=True))
    embeddings = encode_catalog(catalog, args.batch_size)

    STREAMLIT_DIR.mkdir(parents=True, exist_ok=True)
    catalog.to_csv(STREAMLIT_DIR / "catalog_v2.csv", index=False)
    np.save(STREAMLIT_DIR / "embeddings_v2.npy", embeddings)
    metadata = {
        "version": "v2",
        "embedding_model": MODEL_NAME,
        "rows": int(len(catalog)),
        "embedding_shape": list(embeddings.shape),
        "base_rows": int(len(existing)),
        "openlibrary_rows_after_filtering": int(len(catalog) - len(existing)),
        "subjects": SUBJECTS,
        "limit_per_subject": args.limit_per_subject,
    }
    (STREAMLIT_DIR / "catalog_v2_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(metadata)


if __name__ == "__main__":
    sys.exit(main())
