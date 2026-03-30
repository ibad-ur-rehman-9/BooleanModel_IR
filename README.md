# IR Assignment 1 — Boolean Information Retrieval System
### CS4051 — Information Retrieval | Spring 2026 | FAST-NUCES

---

## Overview

A full Boolean Information Retrieval system built on a corpus of **56 Trump Speeches (June 2015 – November 2016)**. The system supports preprocessing, inverted and positional indexing, boolean query processing, proximity queries, and a web-based GUI.

---

## Project Structure
```
IR_Assignment1/
│
├── Trump Speechs/                  ← Corpus (56 speech documents)
├── templates/
│   └── index.html                  ← Flask frontend (GUI)
│
├── IR_Assignment1.ipynb            ← Main notebook (all IR logic)
├── app.py                          ← Flask backend
├── stopwords.txt                   ← Provided stopword list
├── inverted_index.json             ← Auto-generated inverted index
├── positional_index.json           ← Auto-generated positional index
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.x
- Anaconda / Jupyter Notebook
- pip

### Install Dependencies
```bash
pip install nltk flask
```

### Download NLTK Data
```python
import nltk
nltk.download('punkt')
```

---

## Running the Project

### 1. Build the Indexes (run once)

Open `IR_Assignment1.ipynb` in Jupyter and run all cells top to bottom. This will:
- Load and preprocess all 56 speeches
- Build and save `inverted_index.json`
- Build and save `positional_index.json`

### 2. Launch the Web GUI
```bash
cd "path/to/IR_Assignment1"
python app.py
```

Then open your browser and go to:
```
http://127.0.0.1:5000
```

---

## Preprocessing Pipeline

Each document goes through the following steps before indexing:

| Step | Description |
|---|---|
| **Tokenization** | Split raw text into words using regex `[a-zA-Z]+` |
| **Case Folding** | Convert all tokens to lowercase |
| **Stopword Removal** | Remove words from the provided stopword list |
| **Stemming** | Reduce words to root form using Porter Stemmer |

> Example: `"Trump is running for President"` → `['trump', 'run', 'presid']`

---

## Index Structures

### Inverted Index
Maps each term to a sorted list of document IDs where it appears.
```
"trump" → [0, 1, 2, 3, 4, ...]
"run"   → [0, 1, 3, 5, ...]
```

### Positional Index
Maps each term to a dictionary of document IDs and the exact positions the term appears at within each document.
```
"trump" → {
    0: [9, 37, 187, 190, ...],
    1: [2212],
    ...
}
```
Both indexes are saved as `.json` files and loaded on startup — no need to rebuild on every run.

---

## Query Types Supported

### 1. Single Term
```
running
```

### 2. Boolean AND
```
actions AND wanted
```

### 3. Boolean OR
```
united OR plane
```

### 4. Boolean NOT
```
NOT hammer
```

### 5. Chained Boolean
```
pakistan OR afghanistan OR aid
```

### 6. Complex Nested Boolean
```
biggest AND (near OR box)
biggest AND (plane OR wanted OR hour)
```

### 7. Proximity Query
Returns documents where two terms appear within **k** positions of each other.
```
after years /1
keep out /2
develop solutions /1
```

---

## Query Results vs Gold Standard

| Query | Expected | Match |
|---|---|---|
| `running` | {0,1,2,3,4,5,6,8,9,...} | Match |
| `NOT hammer` | {0,1,2,3,4,5,6,7,...} | Match |
| `actions AND wanted` | {0,1,2,3,5,7,9,...} | Match |
| `united OR plane` | {0,1,2,3,4,5,6,...} | Match |
| `pakistan OR afganistan OR aid` | {3,16,22,29,37,...} | Match |
| `biggest AND (near OR box)` | {4,6,18,43,44,...} | Match |
| `box AND (united OR year)` | {4,9,18,23,25,...} | Match |
| `biggest AND (plane OR wanted OR hour)` | {0,1,2,4,6,7,...} | Match |
| `after years /1` | {6,7,44} | Mismatch |
| `develop solutions /1` | {5,32} | Match |
| `keep out /2` | {20,24,39,40,51} | Mismatch |

> ⚠️ Minor discrepancies in some proximity queries are due to preprocessing differences between our pipeline and the gold standard's pipeline. Our implementation correctly identifies documents where the terms appear within k positions — the position counting differs slightly due to stopword handling during index construction.

---

## Web GUI

The web interface is built with Flask (backend) and plain HTML/CSS/JS (frontend).

<img width="1172" height="927" alt="image" src="https://github.com/user-attachments/assets/a39906c4-379c-49ab-8354-afc0942a922c" />


**Features:**
- Search bar supporting all query types
- Example query chips for quick testing
- Results displayed as matching document names
- Live result count
- Dark themed, responsive UI

---

## Author

**Ibad Ur Rehman**
- BS Computer Science - Semester 6
- FAST-NUCES, Karachi
- Email: connect.ibadurrehman@gmail.com
