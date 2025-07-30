# Azerbaijani Stopwords

`azerbaijani_stopwords` is a lightweight Python package that provides a curated list of Azerbaijani stopwords for natural language processing (NLP) tasks.

## Why?

When processing Azerbaijani text for tasks like sentiment analysis, classification, or search, it's often necessary to remove common words that do not carry much meaning—like "və", "da", or "ilə". This package helps you do that easily.

## Installation

```bash```
You can use the following command to install library
```pip install azerbaijani_stopwords```

## How to use?

```python
from azerbaijani_stopwords import AZERBAIJANI_STOPWORDS

text = "Bu gün hava çox gözəldir və mən parkda gəzirəm."
words = text.lower().split()

filtered_words = [word for word in words if word not in AZERBAIJANI_STOPWORDS]

print(filtered_words)

# Output: ['gün', 'hava', 'gözəldir', 'parkda', 'gəzirəm.']

```

