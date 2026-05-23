import json
import chromadb
from sentence_transformers import SentenceTransformer

# Load corpus
print("Loading corpus...")
with open("data/corpus.json", "r", encoding="utf-8") as f:
    data = json.load(f)
print("Total entries: " + str(len(data)))

# Filter empty entries
data = [item for item in data if item.get("original_tamil", "").strip()]
print("Valid entries after filtering: " + str(len(data)))

# Load Tamil embedding model
print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# ChromaDB setup
print("Setting up ChromaDB...")
client = chromadb.PersistentClient(path="./chroma_db")

# Delete old collection if exists
try:
    client.delete_collection("tamil_corpus")
    print("Old collection cleared")
except:
    pass

collection = client.create_collection("tamil_corpus")

# Ingest in batches of 100
BATCH_SIZE = 100
total = len(data)
print("Starting ingestion...")
print("-" * 40)

for i in range(0, total, BATCH_SIZE):
    batch = data[i:i + BATCH_SIZE]
    ids = [item["id"] + "_" + str(i + idx) for idx, item in enumerate(batch)]
    documents = [item["original_tamil"] for item in batch]
    metadatas = [
        {
            "source":          item.get("source", ""),
            "number":          str(item.get("number", "")),
            "translation":     item.get("translation_en", ""),
            "translation_ta":  item.get("translation_ta", ""),
            "explanation":     item.get("explanation", ""),
            "transliteration": item.get("transliteration", ""),
            "couplet":         item.get("couplet", ""),
            "poet":            item.get("poet", ""),
            "period":          item.get("period", "sangam"),
            "topic":           item.get("topic", ""),
        }
        for item in batch
    ]
    embeddings = model.encode(documents).tolist()
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    print("Ingested " + str(min(i + BATCH_SIZE, total)) + " / " + str(total))

print("-" * 40)
print("ChromaDB ingestion complete!")
print("Collection count: " + str(collection.count()))