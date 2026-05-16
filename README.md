---
license: mit
task_categories:
- text-classification
language:
- ta
tags:
- art
pretty_name: Kalithogai
size_categories:
- n<1K
---
## Kalithogai (கலித்தொகை)

Kalithogai (கலித்தொகை) is one of the Ettuthokai (Eight Anthologies) of Tamil Sangam literature, consisting of 150 poems written in the Kali meter.
The poems cover inner-life themes (Akam) such as love, separation, and human emotions, often mapped to the landscapes (thinai) like Kurinji, Mullai, Marutham, Neithal, and Palai.

This dataset provides each poem along with metadata such as title, poet, and structured text.
It is useful for NLP research, poetry generation, translation, cultural preservation, and linguistic studies.

## Supported Tasks and Benchmarks

Text Classification: Categorize poems by thinai (landscape/emotion).

Text Generation: Train models for classical Tamil poetry generation.

Translation: Build Tamil–English parallel datasets.

Information Retrieval: Retrieve poems by poet or theme.

Linguistic Analysis: Study Sangam-era grammar and meter (Kali meter).

## Languages

Primary Language: Tamil (ta)

## Dataset Structure
Data Fields

Each entry in the dataset contains the following fields:

id: Unique identifier for the poem (integer)

title: Title of the poem (string)

poem: Full Tamil poem text (string)

poet: Name of the poet (string)

## Example
{
  "id": 1,
  "title": "கலித்தொகை - 1. கடவுள்வாழ்த்து",
  "poem": "ஆறு அறி அந்தணர்க்கு அரு மறை பல பகர்ந்து,\nதேறு நீர் சடைக் கரந்து, திரிபுரம் தீ மடுத்து,...",
  "poet": "பெருங்கடுங்கோ"
}

## Source Data
Original Source

The poems were sourced from TamilSurangam and other public Tamil literary repositories that host Sangam texts.

## License

The dataset is distributed under the MIT License.

Dataset Creation
Motivation

The dataset was created to make Tamil Sangam literature accessible for computational linguistics, NLP research, and digital preservation of Tamil classics.

## Who can use it?

Researchers: For Tamil NLP and historical text studies.

Educators & Students: For learning Tamil classical poetry.

Developers: To build cultural and literary AI applications.

## Citation

If you use this dataset, please cite it as:

@dataset{TamilThagaval/Kalithogai,
  title     = {Kalithogai (கலித்தொகை) Dataset},
  author    = {TamilThagaval Community},
  year      = {2025},
  publisher = {Hugging Face},
  license   = {MIT}
}

## How to Load

You can load the dataset directly from Hugging Face:

from datasets import load_dataset

dataset = load_dataset("TamilThagaval/Kalithogai")

print(dataset["train"][0])

## Tags

#tamil #nlp #poetry #sangam #classical-literature #digital-humanities
#tamilnlp #literature #dataset #open-source #ancient-texts
#language-models #culture #Kalithogai #Ettuthokai