"""
IndicTrans2 Standalone Terminal Test — TAMIL-AI.ME
=====================================================
Run this BEFORE wiring IndicTrans2 into the FastAPI backend.
Confirms, in isolation:
  - Model loads cleanly under tamil-ai-310 (transformers==4.40.0)
  - Target-language tag handling resolves correctly for Tamil
  - HF_HUB_DISABLE_XET=1 avoids the hub-download path that caused
    install friction on Windows
  - IndicTransToolkit pre/post-processing round-trips correctly

Usage:
    conda activate tamil-ai-310
    python test_indictrans2.py
"""

import os
import sys

# Must be set BEFORE any HF imports — this is the env var that fixed
# the Windows download issue. Setting it after import is a no-op.
os.environ["HF_HUB_DISABLE_XET"] = "1"

try:
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
except ImportError as e:
    sys.exit(
        f"[FATAL] Missing core dependency: {e}\n"
        f"        Confirm you're in the right env: conda activate tamil-ai-310"
    )

try:
    # Package layout has changed across IndicTransToolkit versions —
    # try both import paths rather than assuming one.
    from IndicTransToolkit.processor import IndicProcessor
except ImportError:
    try:
        from IndicTransToolkit import IndicProcessor
    except ImportError as e:
        sys.exit(
            f"[FATAL] IndicTransToolkit not importable: {e}\n"
            f"        Re-check the Windows Cython build-tools install path "
            f"that bit you previously."
        )

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"
SRC_LANG = "eng_Latn"
TGT_LANG = "tam_Taml"

TEST_SENTENCES = [
    "The sun rises in the east.",
    "Classical Tamil literature has a history of over two thousand years.",
    "This is a test of the translation pipeline.",
]


def load_pipeline():
    """Load tokenizer, model, and IndicTrans preprocessor once."""
    print(f"[1/4] Loading tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

    print("[2/4] Loading model (first run downloads weights — be patient)")
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        torch_dtype=torch.float32,  # fp32 first for a correctness baseline
    )
    model.eval()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"      Device: {device}")

    print("[3/4] Initializing IndicProcessor")
    ip = IndicProcessor(inference=True)

    return tokenizer, model, ip, device


def translate_batch(sentences, tokenizer, model, ip, device):
    """Run one batch through the full pre-process -> generate -> post-process cycle."""
    batch = ip.preprocess_batch(sentences, src_lang=SRC_LANG, tgt_lang=TGT_LANG)

    # Debug visibility: this is exactly where the <2tam> tag bug would show up.
    # If the tag is missing/malformed here, generation will be wrong downstream
    # regardless of model quality.
    print("      Tagged input (first sentence):")
    print(f"      {batch[0]!r}\n")

    inputs = tokenizer(
        batch,
        truncation=True,
        padding="longest",
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            use_cache=True,
            min_length=0,
            max_length=256,
            num_beams=5,
            num_return_sequences=1,
        )

    decoded = tokenizer.batch_decode(
        generated,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
    )

    return ip.postprocess_batch(decoded, lang=TGT_LANG)


def main():
    print("=" * 60)
    print("IndicTrans2 Terminal Test — TAMIL-AI.ME")
    print("=" * 60)

    tokenizer, model, ip, device = load_pipeline()

    print("\n[4/4] Running translation batch\n")
    try:
        translations = translate_batch(TEST_SENTENCES, tokenizer, model, ip, device)
    except Exception as e:
        sys.exit(f"[FATAL] Translation batch failed: {e!r}")

    print("-" * 60)
    for src, tgt in zip(TEST_SENTENCES, translations):
        print(f"EN : {src}")
        print(f"TA : {tgt}")
        print("-" * 60)

    print("\nPASS criteria: Tamil text above should be well-formed, grammatical,")
    print("and clearly correspond to the English input — not garbled, not just")
    print("the source echoed back, not empty.")


if __name__ == "__main__":
    main()