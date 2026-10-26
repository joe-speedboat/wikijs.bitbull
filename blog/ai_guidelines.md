---
title: AI Guidelines for IT Admins
description: How get aware of risks when using AI
published: true
date: 2026-10-26T14:13:02.417Z
tags: helpers, blog, ai
editor: markdown
dateCreated: 2026-03-10T14:08:45.776Z
---

# Use of AI in the IT Team
> **Note:** These guidelines apply to the entire use of AI-supported chat systems within the IT team.  
> **Principle:** No finger-pointing; improvement is the goal.

## Target Audience
- IT service providers
- IT staff

---

## Sensitivity Classification

| Sensitivity Level | Examples | Notes |
|:------------------|:---------|:------|
| **Low** | Domain names<br>Company names<br>Organizational data | This data can be publicly found. |
| **Medium** | FQDNs / IPs<br>Groups, accounts, DNs<br>Confidential documentation (e.g., IT documentation)<br>Error messages (copy/paste) | Always read before inserting into ChatGPT and neutralize if necessary. |
| **High** | Credentials<br>Tokens<br>Social engineering–relevant data | Anything that could be abused to impersonate a trusted entity (e.g., scenarios like technician visits). |

---

## Choice of Anonymity

| Mode | Description |
|:-----|:------------|
| **Native Mode** | Data may be used to train models.<br>Comparable to publishing on the internet (homepage, public GitHub repository, etc.). |
| **Temporary Session** | Activation via the icon in the top right of the chat window.<br>No storage in chat history.<br>No use for model training.<br>Data is internally stored for 30 days for security reasons. |
| **API Usage (Aider, OpenWebUI, etc.)** | Better data protection than a temporary session.<br>Data may still be internally reviewed.<br>Usage is subject to costs.<br>See: [OpenAI Enterprise Privacy](https://openai.com/enterprise-privacy/) |

---

## Usage Guidelines

- Before any input into ChatGPT, the following must be known:
  - **Sensitivity of the data** (see table above)
  - **Selected security level** (see choice of anonymity)

- Sensitive data must be anonymized or abstracted before use.

---

## Damage Mitigation

| Sensitivity Level | Security Level | Procedure |
|:------------------|:--------------|:----------|
| **Low** | Any | No special measures required. |
| **Medium** | Temporary session or API call | Not a major problem, but avoid in the future ("Bad boy"). |
| **Medium** | Native mode | **Immediate reporting** to the IT team to ensure transparency. |
| **High** | Any | **Immediate reporting** to the IT team.<br>**Damage mitigation** for possible social engineering risks.<br>**Renewal** of affected data (e.g., passwords, tokens). |

---

## Auditing

- **Regular searches** using AI for potential leaks or exposure of internal information.
  - Canary Tokens may help?
- **Auditing** of employees’ ChatGPT accounts by mutual agreement:
  - Awareness and training on the use of AI tools.
  - Promotion of an open error culture.

---

## Use of Code
During the implementation of AI-generated code (vibe coding), every employee must ensure:

* No sensitive data has been leaked (see above)
* The employee understands the code
* The code has been documented (at least within the code)
* Positive function testing (all intended scenarios)
    * Error-handling tests (all scenarios deviating from the positive tests)