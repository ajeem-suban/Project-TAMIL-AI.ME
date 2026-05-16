from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

print("Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float16,
    device_map="auto"
)
print("Model loaded successfully!")

def translate_english_to_tamil(text):
    input_text = f"<2tam> {text}"
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=256, num_beams=5)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    text = "India is building powerful AI systems."
    print("English:", text)
    print("Tamil:", translate_english_to_tamil(text))