"""
ai4bharat_service.py
Place this in: C:/Users/ajeem/Project-TAMIL-AI.ME/

Models used:
  - ai4bharat/indictrans2-indic-en-dist-200M  -> Tamil to English translation
  - ai4bharat/IndicBART                        -> Tamil explanation generation

Keeps existing ChromaDB (MiniLM embeddings) untouched.
AI4Bharat models are added ON TOP for translation + explanation.
"""

import torch
import logging
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    MBartForConditionalGeneration,
    MBart50TokenizerFast,
)

logger = logging.getLogger(__name__)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[AI4Bharat] Using device: {DEVICE}")


# ─────────────────────────────────────────────────────────────
# MODEL 1: IndicTrans2 — Tamil → English Translation (~800MB)
# ─────────────────────────────────────────────────────────────
class TamilTranslator:
    def __init__(self):
        model_name = "ai4bharat/indictrans2-indic-en-dist-200M"
        print(f"[AI4Bharat] Loading: {model_name}")
        print("[AI4Bharat] First run downloads ~800MB from HuggingFace...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, trust_remote_code=True
        ).to(DEVICE)
        self.model.eval()
        print("[AI4Bharat] Translator ready!")

    def translate(self, tamil_text: str) -> str:
        try:
            # IndicTrans2 format: src_lang tgt_lang <text>
            input_text = f"tam_Taml eng_Latn {tamil_text}"
            self.tokenizer._switch_to_input_mode()
            encoded = self.tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256,
            ).to(DEVICE)

            target_lang_id = self.tokenizer.convert_tokens_to_ids("eng_Latn")

            with torch.no_grad():
                generated = self.model.generate(
                    **encoded,
                    forced_bos_token_id=target_lang_id,
                    max_new_tokens=256,
                    num_beams=4,
                    early_stopping=True,
                )
            self.tokenizer._switch_to_target_mode()
            result = self.tokenizer.decode(generated[0], skip_special_tokens=True)
            self.tokenizer._switch_to_input_mode()
            return result
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return "[Translation failed]"


# ─────────────────────────────────────────────────────────────
# MODEL 2: IndicBART — Tamil Explanation Generator (~600MB)
# ─────────────────────────────────────────────────────────────
class TamilExplainer:
    def __init__(self):
        model_name = "ai4bharat/IndicBART"
        print(f"[AI4Bharat] Loading: {model_name}")
        print("[AI4Bharat] First run downloads ~600MB from HuggingFace...")
        self.tokenizer = MBart50TokenizerFast.from_pretrained(
            model_name, src_lang="ta_IN"
        )
        self.model = MBartForConditionalGeneration.from_pretrained(
            model_name
        ).to(DEVICE)
        self.model.eval()
        self.tamil_id = self.tokenizer.lang_code_to_id["ta_IN"]
        print("[AI4Bharat] Explainer ready!")

    def explain(self, verse_text: str) -> str:
        try:
            prompt = f"விளக்கம்: {verse_text}"
            self.tokenizer.src_lang = "ta_IN"
            encoded = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=256,
            ).to(DEVICE)

            with torch.no_grad():
                generated = self.model.generate(
                    **encoded,
                    forced_bos_token_id=self.tamil_id,
                    max_length=200,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                )
            return self.tokenizer.decode(generated[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Explanation error: {e}")
            return "[Explanation failed]"


# ─────────────────────────────────────────────────────────────
# SERVICE — Lazy-loads models only when first called
# ─────────────────────────────────────────────────────────────
class AI4BharatService:
    def __init__(self):
        self._translator = None
        self._explainer = None

    @property
    def translator(self):
        if self._translator is None:
            self._translator = TamilTranslator()
        return self._translator

    @property
    def explainer(self):
        if self._explainer is None:
            self._explainer = TamilExplainer()
        return self._explainer

    def translate(self, text: str) -> str:
        return self.translator.translate(text)

    def explain(self, verse: str) -> str:
        return self.explainer.explain(verse)

    def vram_info(self) -> dict:
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            allocated = torch.cuda.memory_allocated() / 1e9
            total = props.total_memory / 1e9
            return {
                "gpu": props.name,
                "total_gb": round(total, 2),
                "used_gb": round(allocated, 2),
                "free_gb": round(total - allocated, 2),
            }
        return {"device": "cpu"}


# Global singleton — imported by backend.py
ai4bharat = AI4BharatService()
