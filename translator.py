import os
os.environ["HF_HUB_DISABLE_XET"] = "1"

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from IndicTransToolkit import IndicProcessor

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"

print("[Translator] Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("[Translator] Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()

print(f"[Translator] Ready on device: {device}")

ip = IndicProcessor(inference=True)


def translate_en_to_ta(text: str) -> str:
    batch = ip.preprocess_batch(
        [text],
        src_lang="eng_Latn",
        tgt_lang="tam_Taml"
    )

    inputs = tokenizer(
        batch,
        return_tensors="pt",
        padding=True,
        truncation=True
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        generated_tokens = model.generate(
            **inputs,
            max_length=256,
            num_beams=5
        )

    outputs = tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True
    )

    outputs = ip.postprocess_batch(outputs, lang="tam_Taml")
    return outputs[0]