import json
import re
import os

def load_thirukkural(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = []
    # handle both {"kural": [...]} and plain list
    if isinstance(data, list):
        items = data
    else:
        items = data.get("kural") or data.get("kurals") or list(data.values())[0]
    for item in items:
        results.append({
            "id": "thirukkural_" + str(item["Number"]).zfill(4),
            "source": "thirukkural",
            "number": item["Number"],
            "original_tamil": item.get("Line1", "") + " " + item.get("Line2", ""),
            "line1": item.get("Line1", ""),
            "line2": item.get("Line2", ""),
            "transliteration": item.get("transliteration1", "") + " " + item.get("transliteration2", ""),
            "translation_en": item.get("Translation") or item.get("explanation") or "",
            "translation_ta": item.get("mv", ""),
            "explanation": item.get("explanation", ""),
            "couplet": item.get("couplet", ""),
            "poet": "திருவள்ளுவர்",
            "period": "sangam"
        })
    print("  Thirukkural: " + str(len(results)) + " kurals loaded")
    return results

def load_purananuru(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    blocks = re.split(r'\n(?=\d+\.)', content)
    results = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        first_line = lines[0].strip()
        num_match = re.match(r'^(\d+)\.\s*(.*)', first_line)
        if not num_match:
            continue
        poem_number = int(num_match.group(1))
        title = num_match.group(2).strip()
        poet = ""
        subject = ""
        tinai = ""
        thurai = ""
        poem_lines = []
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if line.startswith("பாடியவர்"):
                poet = re.sub(r'^பாடியவர்\s*[:]\s*', '', line).strip()
            elif line.startswith("பாடப்பட்டோன்"):
                subject = re.sub(r'^பாடப்பட்டோன்\s*[:]\s*', '', line).strip()
            elif line.startswith("திணை"):
                tinai = re.sub(r'^திணை\s*[:]\s*', '', line).strip()
            elif line.startswith("துறை"):
                thurai = re.sub(r'^துறை\s*[:]\s*', '', line).strip()
            elif line.startswith("சிறப்பு"):
                pass
            else:
                poem_lines.append(line)
        poem_text = "\n".join(poem_lines).strip()
        if not poem_text:
            continue
        results.append({
            "id": "purananuru_" + str(poem_number).zfill(4),
            "source": "purananuru",
            "number": poem_number,
            "title": title,
            "original_tamil": poem_text,
            "transliteration": "",
            "translation_en": "",
            "translation_ta": "",
            "poet": poet,
            "subject": subject,
            "tinai": tinai,
            "thurai": thurai,
            "period": "sangam"
        })
    print("  Purananuru: " + str(len(results)) + " poems loaded from " + filepath)
    return results

def load_akananuru(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = []
    if isinstance(data, list):
        poems = data
    else:
        poems = data.get("poems") or data.get("akananuru") or list(data.values())[0]
    for item in poems:
        number = item.get("number") or item.get("Number") or 0
        tamil = item.get("tamil") or item.get("original_tamil") or item.get("poem") or item.get("text") or ""
        transl = item.get("translation") or item.get("translation_en") or item.get("Translation") or ""
        poet = item.get("poet") or item.get("author") or ""
        results.append({
            "id": "akananuru_" + str(number).zfill(4),
            "source": "akananuru",
            "number": number,
            "original_tamil": tamil,
            "transliteration": item.get("transliteration", ""),
            "translation_en": transl,
            "translation_ta": item.get("translation_ta", ""),
            "explanation": item.get("explanation", ""),
            "poet": poet,
            "tinai": item.get("tinai", ""),
            "thurai": item.get("thurai", ""),
            "period": "sangam"
        })
    print("  Akananuru: " + str(len(results)) + " poems loaded")
    return results

if __name__ == "__main__":
    print("Tamil AI Corpus Converter")
    print("-" * 40)

    corpus = []

    tk_path = "data/thirukkural.txt"  # JSON inside .txt file
    pura_paths = [
        "data/purananuru_1-100",
        "data/purananuru_101-200",
        "data/purananuru_201-300",
        "data/purananuru_301-400"
    ]
    aka_path = "data/agananooru_cleaned.json"
    out_path = "data/corpus.json"

    if os.path.exists(tk_path):
        corpus += load_thirukkural(tk_path)
    else:
        print("WARNING: Thirukkural not found at " + tk_path)

    for ppath in pura_paths:
        if os.path.exists(ppath):
            corpus += load_purananuru(ppath)
        else:
            print("WARNING: Not found: " + ppath)

    if os.path.exists(aka_path):
        corpus += load_akananuru(aka_path)
    else:
        print("WARNING: Akananuru not found at " + aka_path)

    os.makedirs("data", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    print("-" * 40)
    print("DONE! Total: " + str(len(corpus)) + " entries saved to " + out_path)