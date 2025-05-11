# A Semantic Book Recommendation System

**Bookwise-AI** is an end-to-end, intelligent book recommendation platform that leverages natural language understanding to deliver highly relevant suggestions. Users can simply describe the type of book they’re interested in using free-form, conversational language, and the system interprets this input using advanced Sentence-BERT embeddings to semantically match it with enriched book descriptions. The project combines a responsive and interactive frontend built with Streamlit, a robust data engineering workflow orchestrated through Apache Airflow, and scalable infrastructure management using Terraform, making it both modular and production-ready.

![Project Cover](https://github.com/sntk-76/bookwise-ai/blob/main/Bookwise.png)

---

## 🔗 Live App

Access the deployed app: [Bookwise-AI on Streamlit Cloud](https://bookwise-ai-recommendation.streamlit.app/)

---

## Features

- Natural language input for book recommendations.
- Semantic similarity matching using `all-MiniLM-L6-v2` from SentenceTransformers.
- Book metadata enriched via Google Books API.
- Feedback system for user interaction.
- Automated data ingestion using Apache Airflow DAGs.
- Infrastructure-as-Code with Terraform.
- Deployment on Streamlit Cloud with secure secrets management.

---

## 🛠️ Technologies Used

### 📊 Data Processing & Machine Learning
- **Python** – Core programming language for all components.
- **Pandas** – Data manipulation and analysis.
- **NumPy** – Numerical computations.
- **Apache Spark** – Distributed data processing for scalable transformations.
- **Sentence-BERT (all-MiniLM-L6-v2)** – Semantic text embeddings for recommendation.

### 📈 Data Engineering & Orchestration
- **Apache Airflow** – Workflow orchestration for automated data pipelines.
- **Docker** – Containerization for local Airflow deployment and potential app deployment.

### ☁️ Cloud & Infrastructure
- **Google Cloud Platform (GCP)** – Used for storing enriched datasets and logging user feedback via Google Sheets.
- **Terraform** – Infrastructure-as-Code for provisioning GCP resources.

### 🌐 Frontend & App Interface
- **Streamlit** – Interactive web app interface for user input, recommendations, and feedback.

---

## System Overview

### 1. Data Pipeline

- **Dataset**: Based on GoodBooks-10K (Kaggle).
- **Cleaning**: Removed null values, standardized language codes.
- **Enrichment**: Book descriptions added using Google Books API.
- **Embedding**: Used Sentence-BERT to convert descriptions into vector representations.

### 2. Recommendation Logic

- User input is embedded using the same model.
- Cosine similarity is used to match user input with book embeddings.
- Top-N books are recommended based on similarity score.

### 3. Streamlit App

- Simple UI to input preferences and display results.
- Adjustable number of recommendations via slider.
- Displays book title, author, rating, image, and description.
- Feedback radio buttons (Yes/No).
- External link to Google Search for more details.

### 4. Logging

- User queries and feedback are logged to a Google Sheet using a GCP service account.
- Secure secrets management is handled directly through Streamlit Cloud.

---

## Project Structure

```
bookwise-ai/
├── airflow/                 # Airflow DAGs and logs
│   ├── dags/                # Python upload DAGs
│   ├── data/                # Processed data files
│   ├── docker/              # Docker Compose setup for Airflow
│   ├── logs/                # DAG logs
│   └── plugins/             # (optional) custom Airflow plugins
├── authentication/          # API keys and service account credentials (not used in deployment)
├── data/                    # Cleaned and enriched datasets
├── infrastructure/          # Terraform files for infrastructure provisioning
├── notebooks/               # Jupyter notebooks for data exploration
├── streamlit/               # Streamlit app files
│   ├── app.py               # Streamlit app entry point
│   ├── Dockerfile           # Optional Dockerfile for local deployment
│   ├── requirements.txt     # Python dependencies
│   ├── embeddings.npy       # Precomputed embeddings
│   ├── enriched_data.csv    # Final enriched dataset
│   └── all-MiniLM-L6-v2/    # Local version of the embedding model
├── LICENSE
└── README.md
```

---

## Getting Started (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/bookwise-ai.git
cd bookwise-ai
```

### 2. Create a Virtual Environment and Install Dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r streamlit/requirements.txt
```

### 3. Run the App

```bash
streamlit run streamlit/app.py
```

> Note: Feedback logging will only work if credentials are properly set up in Streamlit Cloud.

---

## Setting Up Secrets (Streamlit Cloud Only)

Secrets (such as Google Sheets API credentials) are managed via the **Streamlit Cloud UI**:

1. Go to your app's dashboard on [Streamlit Cloud](https://streamlit.io/cloud).
2. Click the gear icon next to your app name.
3. Select the **Secrets** tab.
4. Add your service account credentials in TOML format:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
```

No need to include a `.streamlit/secrets.toml` file in your repository.

---

## Airflow Pipelines

The Airflow DAGs automate the upload of data files to GCP or local storage.

### Available DAGs

- `upload_raw_data`
- `upload_cleaned_raw_data`
- `upload_enriched_data`
- `upload_embeddings`

### Run Airflow Locally

```bash
cd airflow/docker
docker-compose up
```

Visit `http://localhost:8080` to access the Airflow UI.

---

## Infrastructure Provisioning (Terraform)

The `infrastructure/` directory contains Terraform configuration to provision:

- GCS buckets
- Service accounts
- IAM roles

### Deploy with Terraform

```bash
cd infrastructure
terraform init
terraform apply
```

Ensure you are authenticated with Google Cloud CLI before running Terraform.

---

## Optional Enhancements

- Replace sklearn similarity with FAISS or Annoy for large-scale vector search.
- Add genre and tag filters for better discovery.
- Implement user sessions and personalization.
- Integrate usage analytics and dashboarding.
- Dockerize the app for local or containerized cloud deployment.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- [GoodBooks-10K Dataset](https://www.kaggle.com/datasets/zygmunt/goodbooks-10k)
- [Google Books API](https://developers.google.com/books)
- [SentenceTransformers](https://www.sbert.net/)
- [Streamlit](https://streamlit.io/)
- [Apache Airflow](https://airflow.apache.org/)
- [Terraform](https://www.terraform.io/)
