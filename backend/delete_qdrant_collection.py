# File: delete_qdrant_collection.py

from qdrant_client import QdrantClient

# Configuration — adjust if needed
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "documents_collection"

# Connect to Qdrant
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Confirm and delete collection
if COLLECTION_NAME in [c.name for c in client.get_collections().collections]:
    client.delete_collection(collection_name=COLLECTION_NAME)
    print(f"✅ Collection '{COLLECTION_NAME}' deleted successfully.")
else:
    print(f"⚠️ Collection '{COLLECTION_NAME}' does not exist.")
