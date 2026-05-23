# translator_service.py
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor

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


def translate_en_to_ta(text: str) -> str:
    """
    Translate a single English string to Tamil.
    """
    batch = ip.preprocess_batch(
        [text],
        src_lang="eng_Latn",
        tgt_lang="tam_Taml"
    )

    inputs = tokenizer(
        batch,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        generated_tokens = model.generate(
            **inputs,
            num_beams=5,
            max_length=256
        )

    decoded = tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True
    )

    return ip.postprocess_batch(decoded, lang="tam_Taml")[0]


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