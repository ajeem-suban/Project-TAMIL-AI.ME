import pathlib

path = pathlib.Path(r'C:\Users\ajeem\.cache\huggingface\modules\transformers_modules\ai4bharat\indictrans2_hyphen_indic_hyphen_en_hyphen_dist_hyphen_200M\eb9e49d81077cfc5311e82ff36d8c1fc11557b5d\tokenization_indictrans.py')

content = path.read_text(encoding='utf-8')

# Fix: add _special_tokens_map init before special tokens are set
old = "        self.src_vocab_fp = src_vocab_fp"
new = "        self._special_tokens_map = {}\n        self.src_vocab_fp = src_vocab_fp"

if old in content:
    content = content.replace(old, new)
    path.write_text(content, encoding='utf-8')
    print("Done! tokenization_indictrans.py fixed successfully.")
else:
    print("Pattern not found - file may already be fixed or has changed.")
