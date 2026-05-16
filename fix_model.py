import pathlib
import re

path = pathlib.Path(r'C:\Users\ajeem\.cache\huggingface\modules\transformers_modules\ai4bharat\indictrans2_hyphen_indic_hyphen_en_hyphen_dist_hyphen_200M\eb9e49d81077cfc5311e82ff36d8c1fc11557b5d\modeling_indictrans.py')

content = path.read_text(encoding='utf-8')

# Fix: make tie_weights accept **kwargs so newer transformers doesn't break it
# Find patterns like: def tie_weights(self): or def tie_weights(self, some_args):
old_patterns = [
    "def tie_weights(self):",
    "def tie_weights(self, recompute_mapping=False):",
]

fixed = False
for old in old_patterns:
    if old in content:
        content = content.replace(old, "def tie_weights(self, **kwargs):")
        fixed = True
        print(f"Fixed: {old}")
        break

if not fixed:
    # Search with regex for any tie_weights definition
    match = re.search(r'def tie_weights\(self[^)]*\):', content)
    if match:
        old_sig = match.group(0)
        content = content.replace(old_sig, "def tie_weights(self, **kwargs):")
        fixed = True
        print(f"Fixed via regex: {old_sig}")

if fixed:
    path.write_text(content, encoding='utf-8')
    print("Done! modeling_indictrans.py fixed successfully.")
else:
    print("tie_weights not found — printing all method signatures for inspection:")
    for i, line in enumerate(content.splitlines()):
        if 'def ' in line:
            print(f"  Line {i+1}: {line.strip()}")
