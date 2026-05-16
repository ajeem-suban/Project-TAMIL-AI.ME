"""
merge_datasets.py — Tamil AI Corpus Merger
============================================
Merges all TamilThagaval datasets into the existing corpus.json schema.

USAGE:
  python merge_datasets.py

ADDING FUTURE DATASETS:
  1. Drop the new JSON/CSV file into the DATASETS_DIR folder
  2. Add an entry to DATASET_CONFIG at the bottom of this file
  3. Re-run the script

OUTPUT:
  corpus_merged.json  — existing corpus + all new entries
  merge_report.txt    — counts and any skipped entries

SCHEMA (matches existing corpus.json):
  id, source, number, original_tamil,
  line1, line2, transliteration,
  translation_en, translation_ta,
  explanation, couplet, poet, period, topic
"""

import json
import csv
import os
import sys
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURATION — edit paths here
# ─────────────────────────────────────────────

EXISTING_CORPUS  =  r"data\corpus.json"       # your current corpus file
DATASETS_DIR     = "new_datasets"         # folder where you put new files
OUTPUT_FILE      =  r"data\corpus_merged.json"  # output file
REPORT_FILE      = "merge_report.txt"     # summary report

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def to_str(val):
    """Safely convert any value (str, list, None) to a single string."""
    if val is None:
        return ""
    if isinstance(val, list):
        return "\n".join(str(v).strip() for v in val if v)
    return str(val).strip()


def split_lines(text):
    """Split poem text into line1 and line2 (best effort)."""
    if not text:
        return "", ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) == 0:
        return "", ""
    elif len(lines) == 1:
        return lines[0], ""
    else:
        return lines[0], "\n".join(lines[1:])


def make_entry(source, number, original_tamil, poet="",
               translation_ta="", explanation="", topic="",
               period="sangam"):
    """Build a single corpus entry matching the existing schema."""
    original_tamil = to_str(original_tamil)
    line1, line2   = split_lines(original_tamil)
    return {
        "id":              f"{source}_{str(number).zfill(4)}",
        "source":          source,
        "number":          number,
        "original_tamil":  original_tamil,
        "line1":           line1,
        "line2":           line2,
        "transliteration": "",                   # not available in these datasets
        "translation_en":  "",                   # not available in these datasets
        "translation_ta":  to_str(translation_ta),
        "explanation":     to_str(explanation),
        "couplet":         "",
        "poet":            to_str(poet),
        "period":          period,
        "topic":           to_str(topic),
    }


# ─────────────────────────────────────────────
# PARSERS — one per schema type
# ─────────────────────────────────────────────

def parse_flat_poem_explanation(data, source, period="sangam"):
    """
    Schema: [{poem, explanation}, ...]
    Used by: iniyavainarpadhu, innanarpadhu, naanmanikadikai,
             thirikadugam, mudhumozhikanchi
    """
    entries = []
    for i, row in enumerate(data, start=1):
        entries.append(make_entry(
            source         = source,
            number         = i,
            original_tamil = row.get("poem", ""),
            translation_ta = row.get("explanation", ""),
            explanation    = row.get("explanation", ""),
            topic          = row.get("athikaram", ""),  # mudhumozhikanchi uses athikaram
            period         = period,
        ))
    return entries


def parse_kurunthogai(data, source, period="sangam"):
    """
    Schema: [{id, topic, poem, poet, explanation, mudippu, karuthu}, ...]
    """
    entries = []
    for i, row in enumerate(data, start=1):
        expl = to_str(row.get("explanation", "")) or \
               to_str(row.get("mudippu", "")) or \
               to_str(row.get("karuthu", ""))
        entries.append(make_entry(
            source         = source,
            number         = row.get("id", i),
            original_tamil = row.get("poem", ""),
            poet           = row.get("poet", ""),
            translation_ta = expl,
            explanation    = expl,
            topic          = row.get("topic", ""),
            period         = period,
        ))
    return entries


def parse_kalithogai(data, source, period="sangam"):
    """
    Schema: [{id, title, poem, poet}, ...]
    """
    entries = []
    for i, row in enumerate(data, start=1):
        entries.append(make_entry(
            source         = source,
            number         = row.get("id", i),
            original_tamil = row.get("poem", ""),
            poet           = row.get("poet", ""),
            topic          = row.get("title", ""),
            period         = period,
        ))
    return entries


def parse_acharakovai(data, source, period="sangam"):
    """
    Schema: [{number, topic, venbha, poem, explanation, karuthurai}, ...]
    """
    entries = []
    for i, row in enumerate(data, start=1):
        poem_text = to_str(row.get("venbha", "")) or to_str(row.get("poem", ""))
        expl = to_str(row.get("explanation", "")) or to_str(row.get("karuthurai", ""))
        entries.append(make_entry(
            source         = source,
            number         = row.get("number", i),
            original_tamil = poem_text,
            translation_ta = expl,
            explanation    = expl,
            topic          = row.get("topic", ""),
            period         = period,
        ))
    return entries


def parse_naaladiyar(data, source, period="post-sangam"):
    """
    Schema: [{topic, poem, explanation, paal, iyal}, ...]
    """
    entries = []
    for i, row in enumerate(data, start=1):
        entries.append(make_entry(
            source         = source,
            number         = i,
            original_tamil = row.get("poem", ""),
            translation_ta = row.get("explanation", ""),
            explanation    = row.get("explanation", ""),
            topic          = f"{row.get('paal','')} - {row.get('iyal','')} - {row.get('topic','')}".strip(" -"),
            period         = period,
        ))
    return entries


def parse_nested_topic_poems(data, source, period="sangam"):
    """
    Schema: [{topic, poems: [{poem, explanation}, ...]}, ...]
    Used by: MaduraiKanji, malaipadukadam, nedunalvaadai,
             Kurijipattu, Pattinapalai, MullaiPattu, perumpanatrupadai
    """
    entries = []
    counter = 1
    for section in data:
        topic = to_str(section.get("topic", ""))
        poems = section.get("poems", [])
        # nedunalvaadai has explanation at section level too
        section_expl = to_str(section.get("explanation", ""))
        for poem_obj in poems:
            # poems can be a list of dicts OR a list of strings
            if isinstance(poem_obj, str):
                poem_text = poem_obj.strip()
                expl      = section_expl
            else:
                poem_text = to_str(poem_obj.get("poem", ""))
                expl      = to_str(poem_obj.get("explanation", "")) or section_expl
            if not poem_text:
                continue
            entries.append(make_entry(
                source         = source,
                number         = counter,
                original_tamil = poem_text,
                translation_ta = expl,
                explanation    = expl,
                topic          = topic,
                period         = period,
            ))
            counter += 1
    return entries


def parse_paripadal(data, source, period="sangam"):
    """
    Schema: [{title, sections: [{heading, content}, ...]}, ...]
    Each section becomes one entry.
    """
    entries = []
    counter = 1
    for poem in data:
        title    = to_str(poem.get("title", ""))
        sections = poem.get("sections", [])
        for section in sections:
            content = to_str(section.get("content", ""))
            heading = to_str(section.get("heading", ""))
            if not content:
                continue
            entries.append(make_entry(
                source         = source,
                number         = counter,
                original_tamil = content,
                topic          = f"{title} — {heading}".strip(" —"),
                period         = period,
            ))
            counter += 1
    return entries


def parse_pathirruppattu(data, source, period="sangam"):
    """
    Schema: [{title, துறை, வண்ணம், தூக்கு, பெயர், poem}, ...]
    Tamil-key metadata fields.
    """
    entries = []
    for i, row in enumerate(data, start=1):
        entries.append(make_entry(
            source         = source,
            number         = i,
            original_tamil = row.get("poem", ""),
            poet           = row.get("பெயர்", ""),      # பெயர் = name/poet
            topic          = row.get("title", ""),
            period         = period,
        ))
    return entries


def parse_narrinai_csv(filepath, source, period="sangam"):
    """
    CSV Schema: poem_number, poem, poet, note, explanation
    """
    entries = []
    import pandas as pd
    df = pd.read_csv(filepath)
    for _, row in df.iterrows():
        expl = str(row.get("explanation", "") or "")
        entries.append(make_entry(
            source         = source,
            number         = int(row.get("poem_number", 0)),
            original_tamil = str(row.get("poem", "") or ""),
            poet           = str(row.get("poet", "") or ""),
            translation_ta = expl,
            explanation    = expl,
            topic          = str(row.get("note", "") or ""),
            period         = period,
        ))
    return entries


# ─────────────────────────────────────────────
# DATASET CONFIG
# Add new datasets here in future — just add an entry!
# ─────────────────────────────────────────────
# Format:
#   "filename_in_DATASETS_DIR": {
#       "source":  "source_name_for_id",
#       "parser":  parser_function,
#       "period":  "sangam" | "post-sangam" | etc.
#   }

DATASET_CONFIG = {
    "acharakovai_poems_clean.json": {
        "source": "acharakovai",
        "parser": parse_acharakovai,
        "period": "post-sangam",
    },
    "iniyavainarpadhu_poems.json": {
        "source": "iniyavainarpadhu",
        "parser": parse_flat_poem_explanation,
        "period": "post-sangam",
    },
    "innanarpadhu_poems.json": {
        "source": "innanarpadhu",
        "parser": parse_flat_poem_explanation,
        "period": "post-sangam",
    },
    "kalithogai_merged.json": {
        "source": "kalithogai",
        "parser": parse_kalithogai,
        "period": "sangam",
    },
    "kurunthogai_merged.json": {
        "source": "kurunthogai",
        "parser": parse_kurunthogai,
        "period": "sangam",
    },
    "MaduraiKanji_cleaned.json": {
        "source": "madurai_kanji",
        "parser": parse_nested_topic_poems,
        "period": "sangam",
    },
    "malaipadukadam_cleaned.json": {
        "source": "malaipadukadam",
        "parser": parse_nested_topic_poems,
        "period": "sangam",
    },
    "mudhumozhikanchi.json": {
        "source": "mudhumozhikanchi",
        "parser": parse_flat_poem_explanation,
        "period": "post-sangam",
    },
    "naaladiyar_all_poems_with_paal_iyal.json": {
        "source": "naaladiyar",
        "parser": parse_naaladiyar,
        "period": "post-sangam",
    },
    "naanmanikadikai_poems.json": {
        "source": "naanmanikadikai",
        "parser": parse_flat_poem_explanation,
        "period": "post-sangam",
    },
    "narrinai_clean1.csv": {
        "source": "narrinai",
        "parser": None,          # handled separately (CSV)
        "period": "sangam",
    },
    "nedunalvaadai_clean.json": {
        "source": "nedunalvaadai",
        "parser": parse_nested_topic_poems,
        "period": "sangam",
    },
    "paripadal_all.json": {
        "source": "paripadal",
        "parser": parse_paripadal,
        "period": "sangam",
    },
    "pathirruppattu_all.json": {
        "source": "pathirruppattu",
        "parser": parse_pathirruppattu,
        "period": "sangam",
    },
    "Pathupattu-Kurijipattu.json": {
        "source": "kurinjippattu",
        "parser": parse_nested_topic_poems,
        "period": "sangam",
    },
    "Pathupattu-Pattinapalai.json": {
        "source": "pattinapalai",
        "parser": parse_nested_topic_poems,
        "period": "sangam",
    },
    "Patthupattu-MullaiPattu.json": {
        "source": "mullaipattu",
        "parser": parse_nested_topic_poems,
        "period": "sangam",
    },
    "perumpanatrupadai_cleaned.json": {
        "source": "perumpanatrupadai",
        "parser": parse_nested_topic_poems,
        "period": "sangam",
    },
    "thirikadugam_poems.json": {
        "source": "thirikadugam",
        "parser": parse_flat_poem_explanation,
        "period": "post-sangam",
    },
}


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    report_lines = []

    # 1. Load existing corpus
    if os.path.exists(EXISTING_CORPUS):
        with open(EXISTING_CORPUS, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"✅ Loaded existing corpus: {len(existing)} entries")
        report_lines.append(f"Existing corpus: {len(existing)} entries")
    else:
        existing = []
        print("⚠️  No existing corpus found — starting fresh")
        report_lines.append("No existing corpus — starting fresh")

    # 2. Collect existing IDs to avoid duplicates
    existing_ids = {entry["id"] for entry in existing}

    # 3. Process each new dataset
    all_new_entries = []
    datasets_path   = Path(DATASETS_DIR)

    for filename, config in DATASET_CONFIG.items():
        filepath = datasets_path / filename
        if not filepath.exists():
            print(f"⚠️  MISSING: {filename} — skipping")
            report_lines.append(f"MISSING: {filename}")
            continue

        source = config["source"]
        period = config.get("period", "sangam")
        parser = config["parser"]

        try:
            # CSV path
            if filename.endswith(".csv"):
                entries = parse_narrinai_csv(filepath, source, period)
            else:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                entries = parser(data, source, period)

            # Deduplicate against existing corpus
            new_entries = [e for e in entries if e["id"] not in existing_ids]
            skipped     = len(entries) - len(new_entries)

            all_new_entries.extend(new_entries)
            for e in new_entries:
                existing_ids.add(e["id"])

            msg = f"✅ {source:<25} {len(new_entries):>4} entries added"
            if skipped:
                msg += f"  ({skipped} duplicates skipped)"
            print(msg)
            report_lines.append(msg)

        except Exception as ex:
            msg = f"❌ ERROR in {filename}: {ex}"
            print(msg)
            report_lines.append(msg)

    # 4. Merge and save
    merged = existing + all_new_entries
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # 5. Print summary
    summary = [
        "",
        "=" * 50,
        f"Existing entries  : {len(existing)}",
        f"New entries added : {len(all_new_entries)}",
        f"Total in output   : {len(merged)}",
        f"Output file       : {OUTPUT_FILE}",
        "=" * 50,
    ]
    print("\n".join(summary))
    report_lines.extend(summary)

    # 6. Write report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"📄 Report saved to {REPORT_FILE}")


if __name__ == "__main__":
    main()