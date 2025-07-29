# pyBioMedLink

*pyBioMedLink* is an open-source python library for bio-medical term linking.


## Usage

```Python
from pybiomedlink.linker import BM25Linker

corpus = [
"Hello there good man!",
"It is quite windy in London",
"How is the weather today?"
]
query = "windy London"

bm25_linker = BM25Linker(corpus)
top_k = 2
predictions = bm25_linker.predict(query, top_k)
print(f"Predictions for query '{query}': {predictions}")
# ['It is quite windy in London', 'How is the weather today?']

pred_score_results = bm25_linker.predict_with_scores(query, top_k)
print(f"Predictions with scores for query '{query}': {pred_score_results}")
# {'labels': ['It is quite windy in London', 'How is the weather today?', 'Hello there good man!'], 'scores': [0.9372947225064051, 0.0, 0.0]}
```

## Supported Models

**Zero-shot models:**
- BM25Linker: A BM25-based linker
- LevenshteinLinker: A Levenshtein distance-based linker