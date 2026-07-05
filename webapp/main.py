from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from webapp.recommender import recommend_books

app = FastAPI(title="Bookwise AI")


class RecommendationRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_n: int = Field(5, ge=1, le=10)


@app.get("/bookwise/", response_class=HTMLResponse)
def bookwise_page():
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Bookwise AI</title>
  <style>
    :root { color-scheme: light; --ink:#161c1b; --muted:#5f6866; --line:#dfe5e2; --paper:#f6f7f3; --soft:#f3efff; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--paper); color:var(--ink); }
    main { width:min(1100px, calc(100% - 32px)); margin:0 auto; padding:54px 0; }
    h1 { margin:0; font-size:clamp(2.35rem, 6vw, 4.9rem); line-height:1; letter-spacing:0; }
    p { color:var(--muted); line-height:1.65; }
    .panel { margin-top:28px; border:1px solid var(--line); border-radius:8px; background:white; padding:22px; box-shadow:0 18px 45px rgba(29,35,33,.06); }
    form { display:grid; grid-template-columns:1fr 110px auto; gap:10px; align-items:center; }
    textarea, select, button { border-radius:8px; font:inherit; }
    textarea { min-height:88px; resize:vertical; border:1px solid var(--line); padding:13px 14px; }
    select { height:46px; border:1px solid var(--line); padding:0 10px; background:white; }
    button { height:46px; border:1px solid var(--ink); background:var(--ink); color:white; padding:0 18px; font-weight:800; cursor:pointer; }
    button:disabled { opacity:.55; cursor:wait; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; margin-top:22px; }
    .book { border:1px solid var(--line); border-radius:8px; background:#fff; overflow:hidden; display:grid; grid-template-columns:96px 1fr; min-height:180px; }
    .book img { width:96px; height:100%; object-fit:cover; background:#edf0ed; }
    .book div { padding:14px; }
    h2 { margin:24px 0 0; font-size:1.1rem; }
    h3 { margin:0 0 7px; font-size:1rem; line-height:1.3; }
    .meta { margin:0 0 8px; font-size:.86rem; color:var(--muted); }
    .desc { margin:0 0 10px; font-size:.9rem; line-height:1.45; color:#303936; }
    a { color:#5b21b6; font-weight:800; text-decoration:none; }
    .score { display:inline-block; margin-top:2px; padding:3px 7px; border-radius:999px; background:var(--soft); color:#4c1d95; font-size:.78rem; font-weight:800; }
    .error { color:#8a1f1f; font-weight:700; }
    @media (max-width:720px) {
      form { grid-template-columns:1fr; }
      select, button { width:100%; }
    }
  </style>
</head>
<body>
<main>
  <h1>Bookwise AI</h1>
  <p>Describe the kind of book you want and get semantic recommendations from an expanded embedding catalog.</p>
  <section class="panel">
    <form id="recommend-form">
      <textarea id="query" required minlength="3" placeholder="Example: A heartbreaking family story about memory, resilience, and personal growth."></textarea>
      <select id="top_n" aria-label="Number of recommendations">
        <option value="3">3 books</option>
        <option value="5" selected>5 books</option>
        <option value="8">8 books</option>
        <option value="10">10 books</option>
      </select>
      <button id="submit" type="submit">Recommend</button>
    </form>
    <div id="status"></div>
    <div id="results"></div>
  </section>
</main>
<script>
const form = document.querySelector("#recommend-form");
const statusEl = document.querySelector("#status");
const resultsEl = document.querySelector("#results");
const button = document.querySelector("#submit");
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
}[char]));
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  button.disabled = true;
  statusEl.innerHTML = "<p>Finding matches...</p>";
  resultsEl.innerHTML = "";
  try {
    const response = await fetch("/bookwise/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: document.querySelector("#query").value,
        top_n: Number(document.querySelector("#top_n").value)
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Recommendation failed");
    const cards = data.recommendations.map(book => `
      <article class="book">
        <img src="${escapeHtml(book.image_url)}" alt="">
        <div>
          <h3>${escapeHtml(book.title)}</h3>
          <p class="meta">${escapeHtml(book.authors || "Unknown author")} · Rating ${escapeHtml(book.average_rating || "N/A")}</p>
          <p class="desc">${escapeHtml(book.description)}</p>
          ${book.subjects ? `<p class="meta">${escapeHtml(book.subjects)}</p>` : ""}
          <a href="${escapeHtml(book.google_url)}" target="_blank" rel="noreferrer">More info</a>
          <br><span class="score">Match ${escapeHtml(book.match_score)}</span>
        </div>
      </article>`).join("");
    resultsEl.innerHTML = `<h2>Top matches</h2><p class="meta">${data.catalog_size} books searched · ${escapeHtml(data.embedding_model)}</p><div class="grid">${cards}</div>`;
    statusEl.innerHTML = "";
  } catch (error) {
    statusEl.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  } finally {
    button.disabled = false;
  }
});
</script>
</body>
</html>
        """
    )


@app.post("/bookwise/api/recommend")
def recommend(request: RecommendationRequest):
    query = request.query.strip()
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Please describe the book you want.")

    try:
        return recommend_books(query, request.top_n)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="The recommender could not load.") from exc
