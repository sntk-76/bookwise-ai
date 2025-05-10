from sentence_transformers import SentenceTransformer

# Choose your model and target folder
model_name = "sentence-transformers/all-MiniLM-L6-v2"
save_path = "streamlit/all-MiniLM-L6-v2"

# Download the model (if not cached)
print(f"Downloading and caching model: {model_name}")
model = SentenceTransformer(model_name)

# Save the model to the specified directory
print(f"Saving model to: {save_path}")
model.save(save_path)

print("✅ Model downloaded and saved successfully.")
