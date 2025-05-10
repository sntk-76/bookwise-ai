from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Load model and data once
df = pd.read_csv("data/enriched_data.csv")
embeddings = np.load("data/embeddings.npy")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

class RecommendationRequest(BaseModel):
    query: str
    top_n: int = 5

@app.post("/recommend")
def recommend_books(req: RecommendationRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query is empty.")

    query_embedding = model.encode([req.query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = similarities.argsort()[::-1][:req.top_n]

    results = df.iloc[top_indices].copy()
    results["similarity"] = similarities[top_indices]
    return results.to_dict(orient="records")
