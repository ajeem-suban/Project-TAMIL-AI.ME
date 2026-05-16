import pathlib
import re

path = pathlib.Path(r'C:\Users\ajeem\.cache\huggingface\modules\transformers_modules\ai4bharat\indictrans2_hyphen_indic_hyphen_en_hyphen_dist_hyphen_200M\eb9e49d81077cfc5311e82ff36d8c1fc11557b5d\modeling_indictrans.py')

content = path.read_text(encoding='utf-8')

# Find the tie_weights method and show its current body
lines = content.splitlines()
for i, line in enumerate(lines):
    if 'tie_weights' in line:
        print(f"Line {i+1}: {line}")
        # Print next 5 lines to see the body
        for j in range(i+1, min(i+6, len(lines))):
            print(f"Line {j+1}: {lines[j]}")
        print("---")
