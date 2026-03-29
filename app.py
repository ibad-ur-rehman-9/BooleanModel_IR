# app.py — Flask backend for IR Assignment 1
# Loads saved indexes and processes queries via web interface

from flask import Flask, render_template, request, jsonify
import json
import re
import os
from nltk.stem import PorterStemmer

app = Flask(__name__)
stemmer = PorterStemmer()

BASE_DIR = r"C:\Users\Ibad Ur Rehman\Desktop\IR_Assignment1"

#load stopwords 
def load_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())

#load indexes
def load_index(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_positional_index(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    return {term: {int(doc_id): positions for doc_id, positions in doc_dict.items()}
            for term, doc_dict in raw.items()}

stopwords        = load_stopwords(os.path.join(BASE_DIR, "stopwords.txt"))
inverted_index   = load_index(os.path.join(BASE_DIR, "inverted_index.json"))
positional_index = load_positional_index(os.path.join(BASE_DIR, "positional_index.json"))

#total docs (for NOT queries)
with open("inverted_index.json") as f:
    idx = json.load(f)
    all_terms = idx
ALL_DOC_IDS = set()
for postings in inverted_index.values():
    ALL_DOC_IDS.update(postings)

#preprocessing
def preprocess_query_term(term):
    term = term.lower().strip()
    if term in stopwords:
        return None
    return stemmer.stem(term)

#boolean operations
def get_posting(term):
    stemmed = preprocess_query_term(term)
    if stemmed is None or stemmed not in inverted_index:
        return set()
    return set(inverted_index[stemmed])

def boolean_NOT(term):
    return ALL_DOC_IDS - get_posting(term)

#proximity query
def proximity_query(query):
    parts = query.strip().split('/')
    k = int(parts[1].strip())
    terms = parts[0].strip().split()
    if len(terms) != 2:
        return []

    stemmed1 = preprocess_query_term(terms[0])
    stemmed2 = preprocess_query_term(terms[1])
    if not stemmed1 or not stemmed2:
        return []
    if stemmed1 not in positional_index or stemmed2 not in positional_index:
        return []

    common_docs = set(positional_index[stemmed1].keys()) & set(positional_index[stemmed2].keys())
    result = []
    for doc_id in common_docs:
        positions1 = positional_index[stemmed1][doc_id]
        positions2 = positional_index[stemmed2][doc_id]
        found = any(abs(p1 - p2) <= k for p1 in positions1 for p2 in positions2)
        if found:
            result.append(doc_id)
    return sorted(result)

#main query parser 
def parse_and_execute(query):
    query = query.strip()

    if '/' in query:
        return proximity_query(query)

    if query.upper().startswith('NOT '):
        return sorted(boolean_NOT(query[4:].strip()))

    paren_match = re.match(
        r'^(\w+)\s+(AND|OR)\s+\((\w+)\s+(AND|OR)\s+(\w+)(?:\s+(AND|OR)\s+(\w+))?\)$',
        query, re.IGNORECASE
    )
    if paren_match:
        t1       = paren_match.group(1)
        outer_op = paren_match.group(2).upper()
        t2       = paren_match.group(3)
        inner_op = paren_match.group(4).upper()
        t3       = paren_match.group(5)
        t4       = paren_match.group(7)

        inner_result = (get_posting(t2) & get_posting(t3)) if inner_op == 'AND' else (get_posting(t2) | get_posting(t3))
        if t4:
            inner_result = (inner_result & get_posting(t4)) if inner_op == 'AND' else (inner_result | get_posting(t4))

        outer = get_posting(t1)
        result = (outer & inner_result) if outer_op == 'AND' else (outer | inner_result)
        return sorted(result)

    if ' AND ' in query.upper() or ' OR ' in query.upper():
        parts  = re.split(r'\s+(AND|OR)\s+', query, flags=re.IGNORECASE)
        terms  = parts[0::2]
        ops    = parts[1::2]
        result = get_posting(terms[0])
        for i, op in enumerate(ops):
            result = (result & get_posting(terms[i+1])) if op.upper() == 'AND' else (result | get_posting(terms[i+1]))
        return sorted(result)

    return sorted(get_posting(query))

#route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data  = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'results': [], 'count': 0, 'query': query})
    results = parse_and_execute(query)
    return jsonify({'results': results, 'count': len(results), 'query': query})

if __name__ == '__main__':
    app.run(debug=True)