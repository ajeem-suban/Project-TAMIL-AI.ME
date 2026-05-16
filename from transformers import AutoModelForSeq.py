from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from aksharamukha import transliterate
import torch

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"

class TranslationService:
    def __init__(self):
        print("[TranslationService] Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME, trust_remote_code=True
        )
        print("[TranslationService] Loading model...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("[TranslationService] Ready!")

    def english_to_tamil(self, text: str) -> str:
        input_text = f"eng_Latn tam_Taml {text}"
        inputs = self.tokenizer(
            input_text, return_tensors="pt"
        ).to("cuda")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, max_length=256, num_beams=5
            )
        raw_output = self.tokenizer.decode(
            outputs[0], skip_special_tokens=True
        )
        return transliterate.process("Devanagari", "Tamil", raw_output)

# Singleton instance
_service = None

def get_translation_service() -> TranslationService:
    global _service
    if _service is None:
        _service = TranslationService()
    return _service

def translate_to_tamil(text: str) -> str:
    return get_translation_service().english_to_tamil(text)