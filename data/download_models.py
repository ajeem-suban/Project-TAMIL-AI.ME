from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM

print("Downloading indic-bert...")
AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
AutoModel.from_pretrained("ai4bharat/indic-bert")
print("✅ indic-bert done!")

print("Downloading IndicBART...")
AutoTokenizer.from_pretrained("ai4bharat/IndicBART")
AutoModelForSeq2SeqLM.from_pretrained("ai4bharat/IndicBART")
print("✅ IndicBART done!")

print("Downloading IndicTrans2...")
AutoTokenizer.from_pretrained("ai4bharat/indictrans2-indic-en-1B")
AutoModelForSeq2SeqLM.from_pretrained("ai4bharat/indictrans2-indic-en-1B")
print("✅ IndicTrans2 done!")

print("\n🎉 All models downloaded successfully!")