"""
backend.py - Project TAMIL-AI.ME
Upgraded with AI4Bharat translation + explanation on top of existing ChromaDB.
Place in: C:/Users/ajeem/Project-TAMIL-AI.ME/
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import chromadb
import logging
import os

os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from ai4bharat_service import ai4bharat
from translation_service import translate_to_tamil

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Tamil AI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def get_collection():
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_collection("tamil_corpus")

collection = get_collection()
print(f"Ready! {collection.count()} verses in ChromaDB.")


# ── Existing endpoints (unchanged) ──────────────────────────

@app.get("/")
def root():
    return {
        "message": "Tamil AI API is running",
        "version": "2.0.0",
        "total_verses": collection.count(),
        "models": {
            "search": "paraphrase-multilingual-MiniLM-L12-v2",
            "translation": "ai4bharat/indictrans2-indic-en-dist-200M",
            "explanation": "ai4bharat/IndicBART",
        }
    }

@app.get("/search")
def search(query: str, source: str = "all", n: int = 5):
    col = get_collection()
    embedding = model.encode(query).tolist()
    where = {"source": source} if source != "all" else None
    results = col.query(query_embeddings=[embedding], n_results=n, where=where)
    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "id":          results["ids"][0][i],
            "tamil":       results["documents"][0][i],
            "translation": results["metadatas"][0][i].get("translation", ""),
            "source":      results["metadatas"][0][i].get("source", ""),
            "poet":        results["metadatas"][0][i].get("poet", ""),
            "number":      results["metadatas"][0][i].get("number", "")
        })
    return {"query": query, "results": output}

@app.get("/verse/{source}/{number}")
def get_verse(source: str, number: int):
    col = get_collection()
    results = col.get(where={"$and": [{"source": source}, {"number": str(number)}]})
    if not results["ids"]:
        return {"error": "Verse not found"}
    return {
        "id":          results["ids"][0],
        "tamil":       results["documents"][0],
        "translation": results["metadatas"][0].get("translation", ""),
        "poet":        results["metadatas"][0].get("poet", "")
    }

@app.get("/random")
def random_verse():
    import random
    col = get_collection()
    offset = random.randint(0, col.count() - 1)
    results = col.get(limit=1, offset=offset)
    return {
        "id":          results["ids"][0],
        "tamil":       results["documents"][0],
        "translation": results["metadatas"][0].get("translation", ""),
        "source":      results["metadatas"][0].get("source", ""),
        "poet":        results["metadatas"][0].get("poet", "")
    }

# ── New AI4Bharat endpoints ──────────────────────────────────

@app.get("/translate")
def translate(text: str):
    """Tamil → English using IndicTrans2."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    return {
        "source_tamil": text,
        "english": ai4bharat.translate(text),
        "model": "ai4bharat/indictrans2-indic-en-dist-200M"
    }

@app.get("/explain")
def explain(verse: str):
    """Tamil verse explanation using IndicBART."""
    if not verse.strip():
        raise HTTPException(status_code=400, detail="verse cannot be empty")
    return {
        "verse": verse,
        "explanation_tamil": ai4bharat.explain(verse),
        "model": "ai4bharat/IndicBART"
    }

@app.get("/search-ai")
def search_with_ai(query: str, source: str = "all", n: int = 3):
    """
    DEMO ENDPOINT: Search + AI4Bharat translation + explanation in one call.
    Use this for hackathon demos!
    """
    basic = search(query=query, source=source, n=n)
    enriched = []
    for r in basic["results"]:
        enriched.append({
            **r,
            "ai_translation": ai4bharat.translate(r["tamil"]),
            "explanation_tamil": ai4bharat.explain(r["tamil"]),
        })
    return {
        "query": query,
        "results": enriched,
        "pipeline": "MiniLM search → IndicTrans2 → IndicBART"
    }
@app.get("/translate-en-ta")
def translate_english_to_tamil(text: str):
    """English → Tamil using IndicTrans2 en-indic model."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    try:
        result = translate_to_tamil(text)
        return {
            "source_english": text,
            "tamil": result,
            "model": "ai4bharat/indictrans2-en-indic-dist-200M"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vram")
def vram():
    return ai4bharat.vram_info()

@app.get("/health")
def health():
    return {"status": "ok", "corpus_count": collection.count(), "vram": ai4bharat.vram_info()}
