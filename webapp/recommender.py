import re
from pathlib import Path
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).resolve().parents[1]
STREAMLIT_DIR = PROJECT_DIR / "streamlit"
CATALOG_V2 = STREAMLIT_DIR / "catalog_v2.csv"
EMBEDDINGS_V2 = STREAMLIT_DIR / "embeddings_v2.npy"
METADATA_V2 = STREAMLIT_DIR / "catalog_v2_metadata.json"
CATALOG_LEGACY = STREAMLIT_DIR / "enriched_data.csv"
EMBEDDINGS_LEGACY = STREAMLIT_DIR / "embeddings.npy"

MODEL_V2 = "sentence-transformers/all-MiniLM-L12-v2"
MODEL_LEGACY = "sentence-transformers/all-MiniLM-L6-v2"

_model = None
_data = None


def clean_text(value):
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_embeddings(vectors):
    vectors = vectors.astype(np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    return vectors / norms


def model_name():
    return MODEL_V2 if CATALOG_V2.exists() and EMBEDDINGS_V2.exists() else MODEL_LEGACY


def get_model():
    global _model
    name = model_name()
    if _model is None or getattr(_model, "_bookwise_model_name", None) != name:
        _model = SentenceTransformer(name)
        _model._bookwise_model_name = name
    return _model


def get_data():
    global _data
    use_v2 = CATALOG_V2.exists() and EMBEDDINGS_V2.exists()
    catalog_path = CATALOG_V2 if use_v2 else CATALOG_LEGACY
    embeddings_path = EMBEDDINGS_V2 if use_v2 else EMBEDDINGS_LEGACY
    cache_key = (str(catalog_path), str(embeddings_path))
    if _data is None or _data.get("cache_key") != cache_key:
        if not catalog_path.exists() or not embeddings_path.exists():
            raise RuntimeError("Bookwise data files are missing.")
        df = pd.read_csv(catalog_path)
        vectors = normalize_embeddings(np.load(embeddings_path))
        _data = {"cache_key": cache_key, "df": df, "vectors": vectors, "version": "v2" if use_v2 else "legacy"}
    return _data


def query_embedding(query):
    vector = get_model().encode([query], normalize_embeddings=True)
    return vector.astype(np.float32)[0]


def build_query_terms(query):
    words = re.findall(r"[a-zA-Z]{3,}", query.lower())
    stopwords = {
        "book",
        "novel",
        "story",
        "about",
        "with",
        "want",
        "like",
        "that",
        "this",
        "the",
        "and",
        "for",
        "from",
        "into",
        "very",
    }
    return [word for word in words if word not in stopwords]


def hybrid_scores(df, vectors, query):
    query_vec = query_embedding(query)
    semantic = vectors @ query_vec
    terms = build_query_terms(query)

    if not terms:
        return semantic, semantic, np.zeros(len(df), dtype=np.float32)

    searchable = df.get("search_text", df.get("description", pd.Series([""] * len(df)))).fillna("").str.lower()
    title_author = (
        df.get("title", pd.Series([""] * len(df))).fillna("")
        + " "
        + df.get("authors", pd.Series([""] * len(df))).fillna("")
    ).str.lower()
    lexical = np.zeros(len(df), dtype=np.float32)
    title_boost = np.zeros(len(df), dtype=np.float32)
    for term in terms:
        lexical += searchable.str.contains(re.escape(term), regex=True).to_numpy(dtype=np.float32)
        title_boost += title_author.str.contains(re.escape(term), regex=True).to_numpy(dtype=np.float32)
    lexical = np.minimum(lexical / max(1, len(terms)), 1.0)
    title_boost = np.minimum(title_boost / max(1, len(terms)), 1.0)

    rating = pd.to_numeric(df.get("average_rating", 0), errors="coerce").fillna(0).to_numpy(np.float32)
    rating_boost = np.clip((rating - 3.5) / 1.5, 0, 1)

    final = (0.89 * semantic) + (0.06 * lexical) + (0.02 * title_boost) + (0.03 * rating_boost)
    return final, semantic, lexical


def recommend_books(query, top_n=5):
    data = get_data()
    df = data["df"]
    vectors = data["vectors"]
    final_scores, semantic_scores, lexical_scores = hybrid_scores(df, vectors, query)

    candidate_count = min(len(df), max(50, top_n * 15))
    candidate_indices = np.argpartition(final_scores, -candidate_count)[-candidate_count:]
    candidate_indices = candidate_indices[np.argsort(final_scores[candidate_indices])[::-1]]

    seen_titles = set()
    recommendations = []
    for idx in candidate_indices:
        row = df.iloc[int(idx)]
        title = clean_text(row.get("title", "Untitled"))
        key = re.sub(r"[^a-z0-9]+", "", title.lower())
        if key in seen_titles:
            continue
        seen_titles.add(key)
        description = clean_text(row.get("description", ""))
        if len(description) > 280:
            description = description[:277].rsplit(" ", 1)[0] + "..."
        recommendations.append(
            {
                "title": title,
                "authors": clean_text(row.get("authors", "")),
                "average_rating": clean_text(row.get("average_rating", "")),
                "image_url": clean_text(row.get("image_url", "")),
                "description": description,
                "subjects": clean_text(row.get("subjects", "")),
                "similarity": f"{float(semantic_scores[int(idx)]):.2f}",
                "match_score": f"{float(final_scores[int(idx)]):.2f}",
                "lexical_score": f"{float(lexical_scores[int(idx)]):.2f}",
                "data_source": clean_text(row.get("data_source", "")),
                "google_url": f"https://www.google.com/search?q={quote_plus(title + ' book')}",
            }
        )
        if len(recommendations) >= top_n:
            break

    return {
        "query": query,
        "version": data["version"],
        "catalog_size": int(len(df)),
        "embedding_model": model_name(),
        "recommendations": recommendations,
    }
