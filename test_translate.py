from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model_name = "ai4bharat/indictrans2-indic-en-dist-200M"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

print("Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True)

print("Translating...")
tamil = "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு"

# Prepend BOTH src and tgt language tags
tagged_input = "tam_Taml eng_Latn " + tamil

inputs = tokenizer(tagged_input, return_tensors="pt")

target_lang_id = tokenizer.convert_tokens_to_ids("eng_Latn")

output = model.generate(
    **inputs,
    forced_bos_token_id=target_lang_id,
    max_new_tokens=100
)
result = tokenizer.decode(output[0], skip_special_tokens=True)

print(f"\nTamil  : {tamil}")
print(f"English: {result}")