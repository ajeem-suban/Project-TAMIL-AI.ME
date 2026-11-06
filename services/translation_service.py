"""
services/translation_service.py — TAMIL-AI.ME
================================================
IndicTrans2 (en -> indic) translation service.

Design decisions:
  - Model + tokenizer + processor are loaded ONCE at module import time,
    not per-request. Reloading a 200M param model per call would make
    every translation request pay multi-second load latency.
  - Batch-first API: translate_batch() is the primitive, translate_single()
    is a thin convenience wrapper over it. RAG will need to translate
    multiple retrieved chunks per query — building single-string-only now
    just means rewriting this when that need shows up.
  - No FastAPI imports here. This module is transport-agnostic; the
    FastAPI route layer calls into it. Keeps it testable without spinning
    up the API, and reusable if you ever need translation outside the
    HTTP layer (e.g. batch corpus preprocessing scripts).
"""

import logging
import os
from typing import List

# Must be set before any HF import — no-op if set after.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

try:
    from IndicTransToolkit.processor import IndicProcessor
except ImportError:
    from IndicTransToolkit import IndicProcessor

logger = logging.getLogger("tamil_ai.translation_service")

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"
SRC_LANG = "eng_Latn"

# Extend this map as you add target languages beyond Tamil.
SUPPORTED_TARGETS = {
    "ta": "tam_Taml",
}

_MAX_BATCH_SIZE = 32  # guard against an unbounded request blowing up memory/latency


class TranslationServiceError(Exception):
    """Raised for translation-layer failures the API route should map to a 5xx/4xx."""


class TranslationService:
    """
    Loads the IndicTrans2 model once and exposes batch/single translation.
    Instantiate ONE instance per process (module-level singleton below) —
    do not construct this per-request.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Loading IndicTrans2 model '%s' on %s", model_name, self._device)

        self._tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float32,
        )
        self._model.eval()
        self._model.to(self._device)

        self._processor = IndicProcessor(inference=True)
        logger.info("IndicTrans2 model ready.")

    def translate_batch(self, sentences: List[str], target_lang: str = "ta") -> List[str]:
        """
        Translate a batch of English sentences to the target Indic language.

        Args:
            sentences: list of source sentences (English). Empty strings are
                rejected rather than silently passed through, since IndicTrans2
                doesn't have well-defined behavior on empty input.
            target_lang: short code, e.g. "ta" for Tamil. Extend
                SUPPORTED_TARGETS to add languages.

        Returns:
            List of translated strings, same order/length as input.

        Raises:
            TranslationServiceError: on invalid input or inference failure.
        """
        if not sentences:
            return []

        if len(sentences) > _MAX_BATCH_SIZE:
            raise TranslationServiceError(
                f"Batch size {len(sentences)} exceeds max {_MAX_BATCH_SIZE}. "
                f"Split the request into smaller batches."
            )

        if any(not s or not s.strip() for s in sentences):
            raise TranslationServiceError("Empty or whitespace-only sentence in batch.")

        if target_lang not in SUPPORTED_TARGETS:
            raise TranslationServiceError(
                f"Unsupported target_lang '{target_lang}'. "
                f"Supported: {list(SUPPORTED_TARGETS.keys())}"
            )

        tgt_tag = SUPPORTED_TARGETS[target_lang]

        try:
            preprocessed = self._processor.preprocess_batch(
                sentences, src_lang=SRC_LANG, tgt_lang=tgt_tag
            )

            inputs = self._tokenizer(
                preprocessed,
                truncation=True,
                padding="longest",
                return_tensors="pt",
            ).to(self._device)

            with torch.no_grad():
                generated = self._model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    num_return_sequences=1,
                )

            decoded = self._tokenizer.batch_decode(
                generated,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )

            return self._processor.postprocess_batch(decoded, lang=tgt_tag)

        except TranslationServiceError:
            raise
        except Exception as e:
            # Don't leak raw model/tensor internals to API consumers —
            # log full detail, raise a clean service-level error.
            logger.exception("Translation batch failed")
            raise TranslationServiceError(f"Translation failed: {e}") from e

    def translate_single(self, sentence: str, target_lang: str = "ta") -> str:
        """Convenience wrapper for single-sentence translation."""
        result = self.translate_batch([sentence], target_lang=target_lang)
        return result[0]


# Module-level singleton — import this in the FastAPI route layer.
# This is what guarantees "loaded once," not once per request.
#
#   from services.translation_service import translation_service
#   translation_service.translate_single("Hello", target_lang="ta")
#
# NOTE: this means the model loads at process import time, which adds
# to your FastAPI cold-start time. That's the correct tradeoff for a
# long-running API process — pay the load cost once at startup, not
# on every request. If you ever move to a serverless/cold-start-sensitive
# deployment, this singleton pattern needs to change to lazy init.
translation_service = TranslationService()