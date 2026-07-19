"""backend_v2.py - Project TAMIL-AI.ME"""

from difflib import get_close_matches
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import chromadb, logging, os, random

os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from ai4bharat_service import ai4bharat
from translator_service import (
    translate_en_to_ta as translate_to_tamil,
    translate_batch_en_to_ta,
    TranslationError,
)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="English text to translate")


class TranslateBatchRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=32,
                              description="List of English strings to translate")


logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Tamil AI API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("tamil_corpus")
print(f"Ready! {collection.count()} verses in ChromaDB.")

# Build valid source list once at startup, not hardcoded — stays in sync with actual data
_meta = collection.get(include=["metadatas"])["metadatas"]
VALID_SOURCES = sorted({m.get("source", "") for m in _meta if m.get("source")})
print(f"Sources loaded: {len(VALID_SOURCES)}")


def resolve_source(source: str):
    """Case-insensitive + fuzzy match against real ingested sources."""
    s = source.strip().lower()
    if s == "all" or s in VALID_SOURCES:
        return s, None
    match = get_close_matches(s, VALID_SOURCES, n=1, cutoff=0.6)
    return (match[0], s) if match else (None, s)


def format_result(rid, doc, meta):
    return {
        "id": rid, "tamil": doc,
        "translation":     meta.get("translation", ""),
        "translation_ta":  meta.get("translation_ta", ""),
        "explanation":     meta.get("explanation", ""),
        "transliteration": meta.get("transliteration", ""),
        "couplet":         meta.get("couplet", ""),
        "source":          meta.get("source", ""),
        "poet":            meta.get("poet", ""),
        "number":          meta.get("number", ""),
        "topic":           meta.get("topic", ""),
        "period":          meta.get("period", ""),
    }


@app.get("/")
def root():
    return {
        "message": "Tamil AI API is running", "version": "2.0.0",
        "total_verses": collection.count(), "sources": VALID_SOURCES,
        "models": {
            "search": "paraphrase-multilingual-MiniLM-L12-v2",
            "translation": "ai4bharat/indictrans2-indic-en-dist-200M",
        }
    }


@app.get("/sources")
def sources():
    """Frontend dropdown can sync against this instead of a hardcoded list."""
    return {"sources": VALID_SOURCES}


@app.get("/search")
def search(query: str, source: str = "all", n: int = 5):
    if not query.strip():
        raise HTTPException(400, "query cannot be empty")
    resolved, original = resolve_source(source)
    if resolved is None:
        raise HTTPException(404, f"Unknown source '{original}'. Try /sources for the valid list.")

    where = {"source": resolved} if resolved != "all" else None
    embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=n, where=where)
    output = [
        format_result(results["ids"][0][i], results["documents"][0][i], results["metadatas"][0][i])
        for i in range(len(results["ids"][0]))
    ]
    resp = {"query": query, "results": output}
    if resolved != original and original not in (None, "all"):
        resp["note"] = f"'{original}' not found — matched closest source '{resolved}'"
    return resp


@app.get("/verse/{source}/{number}")
def get_verse(source: str, number: int):
    resolved, original = resolve_source(source)
    if resolved is None or resolved == "all":
        raise HTTPException(404, f"Unknown source '{original}'. Try /sources for the valid list.")

    results = collection.get(where={"$and": [{"source": resolved}, {"number": str(number)}]})
    if not results["ids"]:
        raise HTTPException(404, f"No verse #{number} found in '{resolved}'")

    resp = format_result(results["ids"][0], results["documents"][0], results["metadatas"][0])
    if resolved != original:
        resp["note"] = f"'{original}' not found — matched closest source '{resolved}'"
    return resp


@app.get("/random")
def random_verse(source: str = "all"):
    resolved, original = resolve_source(source)
    if resolved is None:
        raise HTTPException(404, f"Unknown source '{original}'. Try /sources for the valid list.")

    where = {"source": resolved} if resolved != "all" else None
    count = collection.count() if where is None else len(collection.get(where=where)["ids"])
    if count == 0:
        raise HTTPException(404, f"No verses found for source '{resolved}'")

    offset = random.randint(0, count - 1)
    results = collection.get(limit=1, offset=offset, where=where)
    return format_result(results["ids"][0], results["documents"][0], results["metadatas"][0])


@app.get("/translate")
def translate(text: str):
    if not text.strip():
        raise HTTPException(400, "text cannot be empty")
    return {"source_tamil": text, "english": ai4bharat.translate(text),
            "model": "ai4bharat/indictrans2-indic-en-dist-200M"}


@app.get("/explain")
def explain(verse: str):
    """NOTE: not real IndicBART — runs the same TA→EN model as /translate.
    Kept for frontend compatibility; relabel/replace before relying on it."""
    if not verse.strip():
        raise HTTPException(400, "verse cannot be empty")
    return {"verse": verse, "explanation_tamil": ai4bharat.explain(verse),
            "model": "ai4bharat/indictrans2-indic-en-dist-200M (mislabeled as IndicBART previously)"}


@app.get("/search-ai")
def search_with_ai(query: str, source: str = "all", n: int = 3):
    basic = search(query=query, source=source, n=n)
    enriched = []
    for r in basic["results"]:
        val = r["translation_ta"].strip() or r["translation"].strip() or ""
        enriched.append({**r, "ai_translation": val, "explanation_tamil": val})  # same value — see note below
    return {"query": query, "results": enriched, "pipeline": "MiniLM search → corpus metadata",
            "note": "ai_translation and explanation_tamil are currently identical — both pull from corpus fields, no live model runs here"}


@app.post("/translate-en-ta")
def translate_english_to_tamil(payload: TranslateRequest):
    try:
        return {
            "source_english": payload.text,
            "tamil": translate_to_tamil(payload.text),
            "model": "ai4bharat/indictrans2-en-indic-dist-200M",
        }
    except TranslationError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/translate-batch-en-ta")
def translate_batch_english_to_tamil(payload: TranslateBatchRequest):
    try:
        translations = translate_batch_en_to_ta(payload.texts)
        return {
            "source_english": payload.texts,
            "tamil": translations,
            "model": "ai4bharat/indictrans2-en-indic-dist-200M",
        }
    except TranslationError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/vram")
def vram():
    return ai4bharat.vram_info()


@app.get("/health")
def health():
    return {"status": "ok", "corpus_count": collection.count(), "vram": ai4bharat.vram_info()}