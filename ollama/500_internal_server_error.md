---
title: Bugs & Fixes
description: Diagnose Ollama 500 errors and model loading failures.
published: false
date: 2026-10-26T14:13:17.507Z
tags: bugfix, ai, ollama
editor: markdown
dateCreated: 2026-04-13T15:24:56.172Z
---

# Ollama: Fix `500 Internal Server Error` & `unable to load model` (GGUF / Qwen3.5)

## Overview

When running certain HuggingFace GGUF models (e.g. Qwen 3.5 variants) in Ollama, the runtime may fail with a generic blob loading error—even though the model file exists and is valid.

This article documents:

* The **primary error**
* The **underlying root cause**
* A **reliable fix**
* Internal behavior of Ollama model layering

---

## Primary Error

```bash
ollama run hf.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive:Q4_K_M
```

Returns:

```text
Error: 500 Internal Server Error: unable to load model: /usr/share/ollama/.ollama/models/blobs/sha256-2ca636d9e81d3d23ca9b60c234fe185d30ec082eeba69ce770fdb0c76559a4f5
```

---

## Secondary (Hidden) Error

From logs:

```bash
journalctl -af
```

```text
llama_model_load: error loading model architecture: unknown model architecture: 'qwen35'
```

👉 Interpretation:

* **Primary error** = generic loader failure
* **Real cause** = architecture mismatch during initialization

---

## Verification

The blob exists and is readable:

```bash
ls -lah /usr/share/ollama/.ollama/models/blobs/sha256-2ca636...
```

Example:

```text
-rw-r--r-- 1 ollama ollama 5.3G Apr 13 16:53 sha256-2ca636...
```

👉 Confirms:

* No filesystem issue
* No missing model
* No permission problem

---

## Root Cause

### Broken Modelfile structure (auto-generated)

```bash
ollama show --modelfile <model> > Modelfile
```

Produces:

```Dockerfile
FROM /usr/share/ollama/.ollama/models/blobs/sha256-2ca636...
FROM /usr/share/ollama/.ollama/models/blobs/sha256-05f662...
TEMPLATE {{ .Prompt }}
```

### Problem

* **Two `FROM` directives**
* Ollama expects **exactly one base model**

This leads to:

* incorrect layer resolution
* invalid model composition
* runtime loader confusion → surfaces as:

```text
unable to load model: <blob>
```

---

## Why the Error Message Is Misleading

The error suggests:

* corrupted file
* missing blob
* I/O issue

But in reality:

👉 The loader fails because it receives an **invalid layered model definition**

Then falls back to a generic:

```text
unable to load model: <blob>
```

---

## Solution

### 1. Export Modelfile

```bash
ollama show --modelfile <model> > Modelfile
```

---

### 2. Fix Modelfile

```bash
vi Modelfile
```

Change:

```Dockerfile
FROM /usr/share/ollama/.ollama/models/blobs/sha256-2ca636...
FROM /usr/share/ollama/.ollama/models/blobs/sha256-05f662...
```

To:

```Dockerfile
FROM /usr/share/ollama/.ollama/models/blobs/sha256-2ca636...
# FROM /usr/share/ollama/.ollama/models/blobs/sha256-05f662...
```

👉 Keep only **one `FROM`**

---

### 3. Recreate model (correct syntax)

```bash
ollama create Qwen3.5-9B-Uncensored-HauhauCS-Aggressive -f ./Modelfile
```

---

### 4. Validate

```bash
ollama ls
```

```bash
ollama run Qwen3.5-9B-Uncensored-HauhauCS-Aggressive:latest
```

---

## Why This Fix Works

Ollama internally uses a **layered model system**:

| Layer    | Purpose             |
| -------- | ------------------- |
| 1st blob | GGUF weights        |
| 2nd blob | metadata / template |

However:

* `ollama show` exposes **internal layering**
* `ollama create` expects a **flattened Modelfile**

### By removing the second `FROM`

You:

* define a valid base model
* eliminate layer conflicts
* allow correct architecture detection (`qwen35`)
* resolve the loader failure

---

## Execution Trace (Successful Build)

```text
copying file sha256:2ca636... 100%
parsing GGUF
using existing layer sha256:2ca636...
creating new layer sha256:b507b9...
writing manifest
success
```

---

## Key Takeaways

* The blob error is **symptomatic**, not causal
* The real issue is **invalid multi-layer Modelfile**
* Always ensure:

  * **exactly one `FROM`**
* `ollama show --modelfile` output is **not directly reusable**

---

## Quick Fix

```bash
ollama show --modelfile <model> > Modelfile
vi Modelfile   # comment second FROM
ollama create <new-name> -f ./Modelfile
```

---

## Reference

* [https://github.com/ollama/ollama/issues/14503](https://github.com/ollama/ollama/issues/14503)
