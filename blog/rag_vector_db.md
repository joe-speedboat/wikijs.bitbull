---
title: Qdrant Vector DB overview
description: Get started with vector DBs and RAG
published: true
date: 2026-10-26T14:13:12.402Z
tags: ai, rag, qdrant
editor: markdown
dateCreated: 2026-03-19T07:33:55.141Z
---

# Vector DB with Qdrant & RAG (Practical Guide)

---

# What is RAG?

**Retrieval-Augmented Generation (RAG)** is a pattern that combines:

* a **vector database (retrieval)**
* a **large language model (generation)**

to produce **accurate, context-aware answers**.

> RAG integrates external data retrieval into LLM generation to improve accuracy and relevance. ([Qdrant][1])

---

## Why RAG exists

LLMs alone:

* ❌ hallucinate
* ❌ don’t know your internal data
* ❌ are static (training cutoff)

RAG solves this:

```text
LLM + your data = grounded answers
```

---

## Core Idea

```text
User Query
   ↓
Embedding
   ↓
Vector DB (Qdrant)
   ↓
Relevant Documents
   ↓
LLM
   ↓
Answer
```

---

# RAG Components (Minimal Mental Model)

A RAG system always consists of:

## 1. Data Pipeline (Indexing)

```text
documents → chunking → embeddings → stored in Qdrant
```

* split documents into chunks
* convert chunks → vectors
* store in vector DB

👉 enables similarity search ([Qdrant][1])

---

## 2. Retriever (Qdrant)

* receives query embedding
* finds **nearest neighbors**
* returns top-k relevant chunks

---

## 3. Generator (LLM)

* takes:

  * user query
  * retrieved documents
* generates final answer

👉 retrieval feeds generation ([Qdrant][1])

---

# Your Real Use Case

## ❓ Question

```text
"how can I setup ascender ldap auth?"
```

---

## 🧠 What happens internally

### Step 1 — Query → Embedding

```text
"how to configure ldap in awx ascender"
→ vector
```

---

### Step 2 — Qdrant Search

Qdrant finds relevant chunks like:

```text
LDAP AUTH HACKS
LDAP Group Search
LDAP User Attribute Map
```

---

### Step 3 — LLM

LLM receives:

```text
Question + retrieved content
```

→ generates structured answer

---

## ✅ Result

Instead of hallucination:

```text
"I think LDAP works like..."
```

You get:

```text
"Use LDAP Server URI ldap://192.168.11.202:389..."
```

→ grounded in your actual wiki

---

# Your Data Model (Real Example)

## Example Point (from your system)

```json
{
  "id": "b11fbb1d-5a46-45c9-83c7-d47ea973cf08",
  "payload": {
    "content": "...LDAP AUTH HACKS...",
    "metadata": {
      "source": "https://wiki.bitbull.ch/en/ansible/awx_ascender/ldap_auth",
      "title": "Ascender LDAP Auth",
      "tag": ["ansible", "freeipa", "awx", "ldap"],
      "date": "2026-02-15T08:14:27.031Z"
    }
  }
}
```

---

## Key Design Pattern

```text
content  → semantic search (vector)
metadata → filtering (exact match)
```

---

# Real Queries (Qdrant)

---

## 1. Payload Filtering (what you already use)

```http
POST /collections/wiki/points/scroll
{
  "filter": {
    "should": [
      {
        "key": "metadata.source",
        "match": {
          "value": "https://wiki.bitbull.ch/en/ansible/awx_ascender/ldap_auth"
        }
      }
    ]
  }
}
```

### What this is

```text
NOT vector search
→ just filtering
```

Equivalent:

```sql
SELECT * WHERE metadata.source = ...
```

---

## 2. Semantic Search (actual RAG)

```http
POST /collections/wiki/points/query
{
  "query": [0.12, -0.3, ...],
  "limit": 5,
  "with_payload": true
}
```

### What this does

* finds similar documents
* returns ranked results

```json
{
  "result": [
    {
      "id": "...",
      "score": 0.82,
      "payload": {...}
    }
  ]
}
```

---

## 3. Hybrid Query (real production pattern)

```http
POST /collections/wiki/points/query
{
  "query": [0.12, -0.3, ...],
  "filter": {
    "must": [
      {
        "key": "metadata.tag",
        "match": { "value": "ldap" }
      }
    ]
  },
  "limit": 5
}
```

---

## Meaning

```text
semantic search + exact filter
```

→ best of both worlds

---

# Internal Mechanics (What actually happens)

## Inside Qdrant

1. Query vector enters HNSW graph
2. graph traversal finds nearest nodes
3. optional payload filter applied
4. top-k results returned

---

## Inside RAG

1. retrieve top-k documents
2. optionally rerank
3. inject into prompt
4. LLM generates answer

---

# Example End-to-End Flow (Your LDAP Case)

```text
User:
"how to configure ldap in awx?"

↓
Embedding

↓
Qdrant returns:
- LDAP config snippet
- AWX settings
- group mapping

↓
LLM prompt:

"Answer using this context:
[LDAP snippet]
[AWX config]"

↓
Answer:
step-by-step LDAP config
```

---

# Practical Use Cases (Your System)

## 1. Wiki Search

```text
"ldap config awx"
```

→ finds correct page without keyword match

---

## 2. Debug / Inspection

```text
scroll API
```

→ inspect chunks from a source

---

## 3. Tag-based Isolation

```json
"metadata.tag": "ansible"
```

→ restrict domain

---

## 4. Time Filtering

```json
"metadata.date > now-30d"
```

→ only recent configs

---

## 5. Multi-tenant Setup

```json
"metadata.user_id": "123"
```

→ isolate users

---

# Key Takeaways

## 1. Your data is already correct

You already have:

* chunked content
* metadata
* structured payload

👉 ready for RAG

---

## 2. Missing piece

You currently use:

```text
scroll API → filtering only
```

You need:

```text
query API → semantic retrieval
```

---

## 3. Core rule

```text
vector = meaning
payload = control
```

---

## 4. Real bottleneck

Not Qdrant:

* embedding quality
* chunking strategy
* prompt design

---

# Final Mental Model

```text
Qdrant = brain memory
LLM = reasoning engine
RAG = connection between both
```

