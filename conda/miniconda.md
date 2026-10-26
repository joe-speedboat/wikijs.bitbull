---
title: miniconda
description: miniconda reference card
published: true
date: 2026-10-26T14:13:24.032Z
tags: ai, python, venv, conda
editor: markdown
dateCreated: 2026-04-22T05:04:05.533Z
---

# Miniconda Best Practices & Planning (Ubuntu / RHEL)

## 1) Installation Strategy

* Prefer **Miniconda over Anaconda** for minimal footprint and reproducibility.
* Install per-user in `$HOME/miniconda3` unless you explicitly need multi-user.
* Avoid system-wide installs (`/opt`) unless you manage permissions + modules.
* Always use **bash installer + SHA256 verification** in production.

## 2) Channel Management

* Standardize on:

  * `conda-forge` (primary)
  * optionally `defaults`
* Enforce priority:

  ```bash
  conda config --set channel_priority strict
  ```

## 3) Environment Isolation

* Never install into `base`
* One project = one env
* Name environments clearly (`nanobot`, `llama-hf`)

## 4) Reproducibility

* Export environments:

  ```bash
  conda env export > env.yml
  ```
* Prefer `--from-history` for minimal spec:

  ```bash
  conda env export --from-history
  ```

## 5) Performance

* Install **mamba** (faster solver):

  ```bash
  conda install -n base -c conda-forge mamba
  ```

## 6) Updates

* Avoid blind `conda update --all` in production
* Pin critical packages when needed

## 7) Migration / Backup

* Use:

  * `conda-pack` (binary relocation)
  * OR `env.yml` recreation (preferred for clean rebuild)

---

# RefCard: Miniconda (Ubuntu / RHEL)

## Intro

Miniconda is a minimal Python distribution providing:

* `conda` package & environment manager
* Lightweight alternative to Anaconda
* Ideal for reproducible, isolated environments

Supported platforms:

* Ubuntu / Debian
* RHEL / Rocky / AlmaLinux / CentOS

---

## Install

### 1. Download

```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

(Use `aarch64` if ARM)

### 2. Verify (recommended)

```bash
sha256sum Miniconda3-latest-Linux-x86_64.sh
```

### 3. Install

```bash
bash Miniconda3-latest-Linux-x86_64.sh
```

* Install path: `$HOME/miniconda3`
* Answer **yes** to `conda init`

### 4. Activate

```bash
source ~/.bashrc
```

### 5. Update base

```bash
conda update -n base -c defaults conda
```

### 6. Configure channels

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
```

---

## Uninstall

```bash
rm -rf ~/miniconda3
rm -rf ~/.conda ~/.condarc ~/.continuum
```

Remove from shell config:

```bash
# edit ~/.bashrc and remove conda init block
```

---

## Create Environments

### General pattern

```bash
conda create -n <env-name> python=3.11
conda activate <env-name>
```

---

### Env: nanobot

```bash
conda create -n nanobot python=3.11
conda activate nanobot

# example dependencies (adjust to your stack)
conda install -c conda-forge requests fastapi uvicorn
```

---

### Env: llama.cpp + HuggingFace

```bash
conda create -n llama-hf python=3.11
conda activate llama-hf
```

Install core packages:

```bash
conda install -c conda-forge llama-cpp
conda install -c conda-forge llama-cpp-python
conda install -c conda-forge huggingface_hub
```

Verify:

```bash
llama-cli
hf
```

---

### Example: Download model

```bash
mkdir -p ~/models/qwen
cd ~/models/qwen

hf download HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive \
  --local-dir ./model
```

---

## Update Environments

### Update nanobot

```bash
conda activate nanobot
conda update --all
```

### Update llama-hf

```bash
conda activate llama-hf
conda update --all
```

### Safer alternative (recommended)

```bash
conda update <package-name>
```

---

## Move Environment to New VM

### Option A (Recommended): YAML export

#### 1. Export

```bash
conda activate llama-hf
conda env export --from-history > llama-hf.yml

conda activate nanobot
conda env export --from-history > nanobot.yml
```

#### 2. Copy files to new VM

#### 3. Recreate

```bash
conda env create -f llama-hf.yml
conda env create -f nanobot.yml
```

---

### Option B: Full binary relocation (conda-pack)

#### 1. Install tool

```bash
conda install -c conda-forge conda-pack
```

#### 2. Pack env

```bash
conda activate llama-hf
conda-pack -o llama-hf.tar.gz
```

#### 3. Transfer + unpack

```bash
mkdir -p ~/envs/llama-hf
tar -xzf llama-hf.tar.gz -C ~/envs/llama-hf
```

#### 4. Fix paths

```bash
~/envs/llama-hf/bin/conda-unpack
```

---

## Operational Tips

* Never pollute `base`
* Use `mamba` for speed:

  ```bash
  mamba install <pkg>
  ```
* Keep environments small and purpose-specific
* Store models outside env (e.g. `/data/models`)
* Use `.condarc` for consistent team setups

# What is Mamba?

**Mamba** is a high-performance drop-in replacement for the `conda` package manager. It is designed to solve one of conda’s biggest operational pain points: **slow dependency resolution**.

---

## Core Concept

* Written in **C++** (vs Python for conda)
* Uses **libsolv** (same solver as `dnf`/`zypper`)
* Fully compatible with conda environments, channels, and workflows

In practice:
You keep your existing Miniconda setup — just replace `conda install` with `mamba install`.

---

## Why Use Mamba

### 1. Speed (Primary Advantage)

* Dependency solving is often **10–100× faster**
* Especially noticeable with:

  * large envs (ML / AI stacks)
  * `conda-forge` heavy usage

### 2. Deterministic Resolution

* More predictable solver behavior under complex constraints

### 3. Drop-in Compatibility

* Same syntax as conda:

  ```bash
  mamba install numpy
  mamba create -n test python=3.11
  ```

---

## Install Mamba

Install into base environment:

```bash
conda install -n base -c conda-forge mamba
```

---

## Typical Usage

### Create environment

```bash
mamba create -n llama-hf python=3.11
```

### Install packages

```bash
mamba install -c conda-forge llama-cpp huggingface_hub
```

### Update environment

```bash
mamba update --all
```

---

## Mamba vs Conda

| Feature              | conda  | mamba            |
| -------------------- | ------ | ---------------- |
| Language             | Python | C++              |
| Solver speed         | Slow   | Very fast        |
| Compatibility        | Native | Fully compatible |
| Default in Miniconda | Yes    | No               |

---

## Important Notes

* Mamba **does not replace conda entirely**

  * `conda` still handles:

    * environment activation
    * configuration (`.condarc`)
* Best practice:

  * Use **mamba for installs/updates**
  * Keep **conda for env management if needed**

---

## Advanced Option: Micromamba

* Even lighter, standalone binary
* No base environment required
* Ideal for:

  * CI/CD
  * containers
  * minimal systems

---

## Bottom Line

If you're working with:

* AI/ML stacks (like `llama.cpp`, `huggingface`)
* large dependency graphs
* repeated environment builds

👉 **Mamba is effectively mandatory for efficiency** on Ubuntu/RHEL systems.

---

If you want, I can refactor your refcard to use **mamba-first workflows** (recommended for your use case).
