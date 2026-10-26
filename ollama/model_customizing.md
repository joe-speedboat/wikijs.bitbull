---
title: Customize Models
description: Customize Ollama models with Modelfiles.
published: true
date: 2026-10-26T14:13:19.141Z
tags: ai, ollama
editor: markdown
dateCreated: 2026-04-13T15:41:51.175Z
---

# Ollama: Customizing Models with Modelfile

## Overview

Ollama allows you to **create customized models** by defining a `Modelfile`.

A `Modelfile` acts as a **blueprint** that defines:

* base model (`FROM`)
* runtime parameters (`PARAMETER`)
* prompt behavior (`TEMPLATE`, `SYSTEM`)
* optional tuning layers

👉 In practice, this behaves similarly to a **Dockerfile for LLMs**.

---

## Core Concept

A `Modelfile` consists of instructions:

```text
INSTRUCTION arguments
```

Key instructions:

| Instruction | Purpose               |
| ----------- | --------------------- |
| `FROM`      | Base model (required) |
| `PARAMETER` | Runtime tuning        |
| `TEMPLATE`  | Prompt structure      |
| `SYSTEM`    | Default system prompt |
| `ADAPTER`   | LoRA / fine-tuning    |
| `LICENSE`   | Metadata              |

([docs.ollama.com][1])

---

## Workflow: Customize an Existing Model

### 1. Export existing Modelfile

```bash
ollama show --modelfile qwen3.5:9b > Modelfile-qwen3.5:9b
```

Example output:

```Dockerfile
FROM /usr/share/ollama/.ollama/models/blobs/sha256-dec52a44...
TEMPLATE {{ .Prompt }}
RENDERER qwen3.5
PARSER qwen3.5
PARAMETER presence_penalty 1.5
PARAMETER temperature 1
PARAMETER top_k 20
PARAMETER top_p 0.95
```

---

### 2. Create your custom Modelfile

Example:

```Dockerfile
FROM qwen3.5:9b

# large context window
PARAMETER num_ctx 131072

# max output tokens
PARAMETER num_predict 8192

# Qwen tuning
PARAMETER temperature 0.6
PARAMETER top_p 0.8
PARAMETER top_k 20
PARAMETER min_p 0

PARAMETER presence_penalty 0.1
PARAMETER repeat_penalty 1.1
PARAMETER repeat_last_n 64

# deterministic output
PARAMETER seed 42
```

---

### 3. Build the custom model

```bash
ollama create qwen3.5-9b-bot -f Modelfile
```

---

### 4. Run it

```bash
ollama run qwen3.5-9b-bot
```

---

## Understanding Key Parameters

### Temperature

```text
PARAMETER temperature 0.6
```

* lower → more deterministic
* higher → more creative ([docs.ollama.com][1])

---

### Top-p / Top-k

```text
PARAMETER top_p 0.8
PARAMETER top_k 20
```

* control randomness filtering
* lower values → more focused output ([docs.ollama.com][1])

---

### Context Size

```text
PARAMETER num_ctx 131072
```

* defines how much input the model can process
* critical for long prompts / RAG setups ([docs.ollama.com][1])

---

### Output Length

```text
PARAMETER num_predict 8192
```

* max tokens generated
* prevents early truncation ([docs.ollama.com][1])

---

### Repetition Control

```text
PARAMETER repeat_penalty 1.1
PARAMETER repeat_last_n 64
```

* reduces looping / repeated text ([docs.ollama.com][1])

---

## TEMPLATE and SYSTEM (Behavior Control)

### TEMPLATE

Defines how prompts are structured:

```Dockerfile
TEMPLATE {{ .Prompt }}
```

Advanced templates can include:

```Dockerfile
TEMPLATE """
{{ if .System }}{{ .System }}{{ end }}
{{ .Prompt }}
"""
```

---

### SYSTEM

Defines model personality:

```Dockerfile
SYSTEM You are a strict Linux consultant.
```

👉 This is the most effective way to:

* enforce tone
* constrain responses
* specialize behavior

---

## Common Customization Patterns

### 1. Deterministic Assistant

```Dockerfile
PARAMETER temperature 0
PARAMETER seed 42
```

Use for:

* automation
* scripting
* reproducible outputs

---

### 2. Creative Assistant

```Dockerfile
PARAMETER temperature 1.2
PARAMETER top_p 0.95
```

Use for:

* brainstorming
* content generation

---

### 3. Long-context RAG model

```Dockerfile
PARAMETER num_ctx 131072
PARAMETER num_predict 4096
```

Use for:

* document processing
* embeddings pipelines

---

### 4. “Strict / low-noise” model

```Dockerfile
PARAMETER temperature 0.5
PARAMETER repeat_penalty 1.2
PARAMETER top_k 20
```

Use for:

* technical answers
* precise outputs

---

## Important Notes

### 1. `FROM` best practice

Prefer:

```Dockerfile
FROM qwen3.5:9b
```

instead of blob paths:

```Dockerfile
FROM /usr/share/ollama/.ollama/models/blobs/sha256-...
```

👉 More portable and stable

---

### 2. Modelfile is not static

* syntax evolves
* features like TEMPLATE are model-specific ([docs.ollama.com][1])

---

### 3. Model duplication

Creating models:

```bash
ollama create ...
```

* does **not duplicate full weights**
* uses shared blobs + new metadata layer

---

## Quick Example (Minimal)

```Dockerfile
FROM llama3

PARAMETER temperature 0.7
PARAMETER num_ctx 4096

SYSTEM You are a helpful assistant.
```

---

## Quick Setup

```bash
ollama show --modelfile <model> > Modelfile
vi Modelfile   # adjust parameters
ollama create <new-name> -f ./Modelfile
ollama run <new-name>
```

---

## Summary

* Modelfiles define **how a model behaves**, not just what it is
* Customization = **parameter tuning + prompt structure**
* `ollama create` builds a **new model layer**, not new weights
* Best practice: start from existing models and **iterate**


[1]: https://docs.ollama.com/modelfile"Modelfile Reference - Ollama"
