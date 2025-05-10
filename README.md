Here is the updated and complete `README.md` file for **Bookwise-AI**, fully aligned with your latest project structure and the fact that you're managing secrets directly through Streamlit Cloud:

---

```markdown
# Bookwise-AI: A Semantic Book Recommendation System

**Bookwise-AI** is an intelligent, natural language-driven book recommendation platform. Users can describe the kind of book they're looking for using free-form text, and the system returns the most semantically relevant results using state-of-the-art sentence embeddings. The app includes a Streamlit frontend, automated data pipelines via Apache Airflow, and infrastructure provisioning with Terraform.

---

## 🔗 Live App

Access the deployed app: [Bookwise-AI on Streamlit Cloud](https://bookwise-ai-recommendation.streamlit.app/)

---

## Features

- Natural language search for books.
- Semantic similarity via Sentence-BERT (`all-MiniLM-L6-v2`).
- Enriched data from the Google Books API.
- Interactive UI with real-time search and recommendation display.
- Feedback collection system for result relevance.
- Automated data ingestion pipelines via Apache Airflow.
- Infrastructure-as-code with Terraform.

---

## System Overview

### 1. Data Pipeline

- **Raw Data**: Based on the GoodBooks-10K dataset.
- **Cleaning**: Removed missing and irrelevant entries, standardized language codes.
- **Enrichment**: Book descriptions fetched via the Google Books API.
- **Embedding**: Descriptions embedded using `all-MiniLM-L6-v2` model into 384-dimensional vectors.

### 2. Recommendation Engine

- User query is embedded and compared to the dataset using cosine similarity.
- Top N most similar books returned as recommendations.

### 3. Streamlit Web App

- Text input for query.
- Slider for result count.
- Book cards with title, author, rating, description, and image.
- External search links.
- User feedback buttons with logging to Google Sheets.

### 4. Airflow DAGs

- Upload tasks for:
  - Raw data
  - Cleaned data
  - Enriched data
  - Embeddings

### 5. Deployment

- Model and data stored locally within the repo to avoid external dependencies.
- App deployed via Streamlit Cloud.

---

## Project Structure

```

bookwise-ai/
├── airflow/                 # Airflow pipelines and data
│   ├── dags/                # DAG scripts
│   ├── data/                # CSV and NPY files
│   ├── docker/              # Airflow Docker setup
│   ├── keys/                # GCP service keys (not used in deployment)
│   ├── logs/                # Airflow logs
│   └── plugins/             # (placeholder for custom plugins)
├── authentication/          # Credential backups (not used on Streamlit Cloud)
├── data/                    # Standalone dataset files
├── infrastructure/          # Terraform configuration
├── notebooks/               # Jupyter notebooks for development
├── project-plan/            # Project planning documents
├── streamlit/               # Main app code
│   ├── app.py               # Streamlit app entry point
│   ├── Dockerfile           # Optional container setup
│   ├── all-MiniLM-L6-v2/    # Local copy of sentence-transformers model
│   ├── embeddings.npy
│   ├── enriched\_data.csv
│   └── requirements.txt
├── LICENSE
└── README.md

````

---

## Getting Started (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/sntk-76/bookwise-ai.git
cd bookwise-ai
````

### 2. Create a Virtual Environment and Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r streamlit/requirements.txt
```

### 3. Run the Streamlit App Locally

```bash
streamlit run streamlit/app.py
```

> Note: Secrets for Google Sheets logging are only required for production. Local logging can be mocked or disabled for development.

---

## Set Up Secrets (Streamlit Cloud Only)

Streamlit Cloud allows secrets to be securely managed through its UI.

To configure:

1. Go to your app’s dashboard on [Streamlit Cloud](https://streamlit.io/cloud).
2. Click the **gear icon** next to your app name and choose **Secrets**.
3. Paste your Google service account credentials in the following format:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
```

There is no need to include `.streamlit/secrets.toml` in your local or remote repository.

---

## Airflow Pipelines

To automate the data processing and uploading workflows, you can use the DAGs under `airflow/dags/`.

### Run Airflow Locally with Docker

```bash
cd airflow/docker
docker-compose up
```

Airflow will launch with the following DAGs:

* `upload_raw_data`
* `upload_cleaned_raw_data`
* `upload_enriched_data`
* `upload_embeddings`

These tasks are designed to upload files to your GCP bucket.

---

## Infrastructure (Optional)

Terraform files in the `infrastructure/` folder allow you to provision required cloud resources:

* Google Cloud Storage buckets
* Service accounts
* IAM bindings

Run with:

```bash
cd infrastructure
terraform init
terraform apply
```

Make sure your GCP CLI is authenticated and configured before applying.

---

## Optional Enhancements

* Integrate FAISS or Annoy for faster, large-scale vector search.
* Add genre or mood filters for refined discovery.
* Enable user sessions or personalization.
* Containerize Streamlit app for Docker-based deployment.
* Log analytics or feedback trends to BigQuery.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

* [GoodBooks-10K Dataset](https://www.kaggle.com/datasets/zygmunt/goodbooks-10k)
* [Google Books API](https://developers.google.com/books)
* [SentenceTransformers](https://www.sbert.net/)
* [Streamlit](https://streamlit.io/)
* [Apache Airflow](https://airflow.apache.org/)
* [Terraform](https://www.terraform.io/)

```

---

Let me know if you'd like a version of this tailored for documentation hosting (e.g., GitHub Pages, ReadTheDocs) or shortened for a public project showcase.
```
