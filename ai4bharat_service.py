# ai4bharat_service.py
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor

class AI4BharatService:

    def __init__(self):
        self.model_name = "ai4bharat/indictrans2-indic-en-dist-200M"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print("[AI4Bharat] Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        print("[AI4Bharat] Loading model...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        self.model.to(self.device)
        self.model.eval()
        self.ip = IndicProcessor(inference=True)
        print(f"[AI4Bharat] Ready on device: {self.device}")

    def translate(self, text: str) -> str:
        """Tamil → English translation."""
        batch = self.ip.preprocess_batch(
            [text],
            src_lang="tam_Taml",
            tgt_lang="eng_Latn"
        )

        inputs = self.tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                num_beams=5,
                max_length=256
            )

        decoded = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )

        return self.ip.postprocess_batch(decoded, lang="eng_Latn")[0]

    def explain(self, verse: str) -> str:
        """Placeholder explanation — translates Tamil verse to English as explanation."""
        try:
            return self.translate(verse)
        except Exception as e:
            return f"Explanation unavailable: {str(e)}"

    def vram_info(self) -> dict:
        """Returns GPU memory info if available."""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**2
            reserved = torch.cuda.memory_reserved() / 1024**2
            return {
                "gpu": torch.cuda.get_device_name(0),
                "allocated_mb": round(allocated, 2),
                "reserved_mb": round(reserved, 2)
            }
        return {"gpu": "none", "device": "cpu"}


# single instance — imported by backend_v2.py
ai4bharat = AI4BharatService()