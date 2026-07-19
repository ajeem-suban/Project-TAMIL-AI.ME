# translator_service.py
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"

print("[TranslatorService] Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("[TranslatorService] Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()

ip = IndicProcessor(inference=True)

print(f"[TranslatorService] Ready on device: {device}")

_MAX_BATCH_SIZE = 32  # tune against actual VRAM/latency once RAG is wired in


class TranslationError(Exception):
    """Raised on invalid input or inference failure. Route layer maps this to HTTP errors."""


def translate_batch_en_to_ta(texts: list[str]) -> list[str]:
    """
    Translate a batch of English strings to Tamil in a single forward pass.
    Reuses the already-loaded module-level model/tokenizer/ip — does NOT
    reload anything.

    Use this for RAG (translating multiple retrieved chunks at once).
    translate_en_to_ta() below routes through this so there's a single
    code path instead of two implementations to keep in sync.
    """
    if not texts:
        return []

    if len(texts) > _MAX_BATCH_SIZE:
        raise TranslationError(
            f"Batch size {len(texts)} exceeds max {_MAX_BATCH_SIZE}."
        )

    if any(not t or not t.strip() for t in texts):
        raise TranslationError("Empty or whitespace-only string in batch.")

    try:
        batch = ip.preprocess_batch(texts, src_lang="eng_Latn", tgt_lang="tam_Taml")

        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            generated_tokens = model.generate(
                **inputs,
                num_beams=5,
                max_length=256,
            )

        decoded = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        return ip.postprocess_batch(decoded, lang="tam_Taml")

    except TranslationError:
        raise
    except Exception as e:
        # Log full detail server-side, don't leak tensor/model internals to callers.
        print(f"[TranslatorService] Batch translation failed: {e!r}")
        raise TranslationError(f"Translation failed: {e}") from e


def translate_en_to_ta(text: str) -> str:
    """
    Translate a single English string to Tamil.
    Thin wrapper over translate_batch_en_to_ta() — single source of truth
    for the actual translation logic.
    """
    return translate_batch_en_to_ta([text])[0]


if __name__ == "__main__":
    tests = [
        "Hello my friend",
        "Tamil is a classical language",
        "The Thirukkural is ancient wisdom"
    ]
    for t in tests:
        print(f"EN: {t}")
        print(f"TA: {translate_en_to_ta(t)}")
        print()