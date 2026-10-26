---
title: searXNG on K3S
description: Install searXNG on K3S and configure hermes agent to work with
published: true
date: 2026-10-26T14:13:37.764Z
tags: kubernetes
editor: markdown
dateCreated: 2026-06-12T18:40:07.745Z
---

# SearXNG Setup — Self-Hosted Meta-Search Engine

---

## 1. Overview

**SearXNG** is a private, meta-searching engine that aggregates results from over 70 search engines. Unlike traditional search engines, it does not pass data to third parties and performs no tracking.

### Key Features

- **Privacy**: No logging, no tracking, no data sharing
- **Aggregation**: Combines results from Google, Bing, DuckDuckGo, Wikipedia, and many more
- **JSON API**: Machine-readable JSON format for programmatic access (e.g., AI agents)
- **Self-Hosted**: Full control over configuration and data

### Use Cases

- Internal search engine for teams/organizations
- Privacy-first search for end users
- API backend for AI agents and automated workflows
- Research and market analysis with aggregated results

---

## 2. Kubernetes Installation

### 2.1 Create Namespace

Create a dedicated namespace for SearXNG:

```bash
export KUBECONFIG=/path/to/kubeconfig
kubectl create namespace searxng --dry-run=client -o yaml | kubectl apply -f -
```

### 2.2 Add Helm Repository

Add the SearXNG Helm chart repository:

```bash
helm repo add kubitodev https://charts.kubito.dev
helm repo update kubitodev
```

### 2.3 Prepare Values File

Create a values file (`searxng-values.yaml`) with the following configuration:

```yaml
# SearXNG Values File
# Source: https://artifacthub.io/packages/helm/kubitodev/searxng

config:
  settings:
    enabled: true
    data: |
      use_default_settings: true

      server:
        secret_key: "<GENERATE-A-RANDOM-KEY-WITH-openssl-rand-hex-32>"
        limiter: false
        image_proxy: true
        port: 8080
        bind_address: "0.0.0.0"

      ui:
        static_use_hash: true

      search:
        safe_search: 0
        autocomplete: ""
        default_lang: ""
        formats:
          - html
          - json  # Critical for agentic tools!

  limiter:
    enabled: true
    data: |
      [botdetection.ip_limit]
      link_token = true

  granian:
    enabled: true
    workers: 1
    blocking_threads: 4
    backpressure: 20
    http1_buffer_size: 8192
    http1_keep_alive: false
    log_level: warning
    log_access_enabled: false

service:
  type: ClusterIP
  port: 8080

ingress:
  enabled: true
  className: ""
  annotations: {}
  hosts:
    - host: search.domain.tld  # Replace with your FQDN
      paths:
        - path: /
          pathType: Prefix
  tls: []

startupProbe: {}

livenessProbe:
  httpGet:
    path: /
    port: http

readinessProbe:
  httpGet:
    path: /
    port: http

resources: {}

nodeSelector: {}

tolerations: []

affinity: {}
```

> **⚠️ Important Notes:**
> - Replace `<GENERATE-A-RANDOM-KEY-WITH-openssl-rand-hex-32>` with a secure random key
> - Replace `search.domain.tld` with your actual FQDN
> - The JSON format entry in `search.formats` is essential for Agentic Tools

### 2.4 Deploy

Install SearXNG using the prepared values file:

```bash
export KUBECONFIG=/path/to/kubeconfig
helm upgrade --install searxng kubitodev/searxng \
  -n searxng \
  -f /path/to/searxng-values.yaml \
  --version 1.1.4 \
  --wait \
  --timeout 300s
```

### 2.5 Configure Ingress

The ingress is created automatically when `ingress.enabled: true` is set in the values file. Verify after deployment:

```bash
kubectl get ingress -n searxng
```

Expected output:

```
NAME              CLASS     HOSTS            ADDRESS         PORTS   AGE
searxng-searxng   traefik   search.domain.tld   <EXTERNAL-IP>   80      1m
```

Check pod status:

```bash
kubectl get all -n searxng
```

---

## 3. JSON Endpoint for Agentic Tools

SearXNG provides a JSON endpoint designed specifically for programmatic access by AI agents and automated workflows.

### Basic Usage

```bash
curl "https://search.domain.tld/search?q=example+query&format=json&limit=5"
```

### Response Structure

The JSON response contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | The searched query |
| `results` | array[] | Array of search results |
| `answers` | array[] | Direct answers (if available) |
| `corrections` | array[] | Spelling corrections |
| `infoboxes` | array[] | Infobox data (e.g., from Wikipedia) |
| `suggestions` | array[] | Suggestions for related searches |

### Per Result Object

Each result in `results` contains:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Result title |
| `url` | string | Target URL |
| `content` | string | Snippet/content description |
| `engine` | string | Search source (e.g., google, bing, wikipedia) |
| `category` | string | Category (general, news, science, etc.) |
| `publishedDate` | string | Publication date (if available) |
| `author` | string | Author (if available) |
| `img_src` | string | Thumbnail URL |
| `parsed_urls` | array[] | Parsed URL components |
| `engines` | array[] | Search engines that returned this result |
| `positions` | array[] | Positions in individual search engines |
| `score` | number | Relevance score |

### Practical Example for Agentic Tools

```bash
# Search for technical documentation
curl -s "https://search.domain.tld/search?q=kubernetes+deployment+guide&format=json&categories=general&limit=3" \
  | jq -r '.results[] | "\(.title)\n\(.url)\n\(.content[:200])\n"'
```

### Recommended Parameters for Agentic Tools

| Parameter | Value | Description |
|-----------|-------|-------------|
| `format` | `json` | Always use JSON for machine-readable output |
| `limit` | `3-10` | Number of results per search |
| `safesearch` | `0` | No safe-search for full results |
| `engines` | `google,bing` | Specify search engines |
| `categories` | `general,news` | Category filter |
| `time_range` | `week,month` | Time range filter |

---

## 4. Configure Hermes Agent

### 4.1 Install Skill

Install the official SearXNG search skill from Hermes Agent:

```bash
hermes skills install official/research/searxng-search
```

This creates the skill under `~/.hermes/skills/research/searxng-search/`.

### 4.2 Set Environment Variable

Add the SearXNG URL to the `.env` file:

```bash
# File: ~/.hermes/.env
SEARXNG_URL=https://search.domain.tld
```

> **Replace** `search.domain.tld` with your actual SearXNG installation FQDN.

### 4.3 Restart Gateway

Restart the Hermes gateway to load the new environment variable:

```bash
hermes gateway restart
```

### 4.4 Verify

Check that the skill is recognized and the SearXNG instance is reachable:

```bash
# Test SearXNG connection
curl -s --max-time 5 "${SEARXNG_URL}/search?q=test&format=json" | head -c 200
```

Expected output (excerpt):

```json
{"query": "test", "results": [...], "answers": [], "corrections": [], "infoboxes": [], "suggestions": [...]}
```

---

## 5. Troubleshooting

### Common Issues and Solutions

#### Issue: Skill not loaded

**Cause:** `SEARXNG_URL` is not set or unreachable.

**Solution:**
```bash
# Check environment variable
echo $SEARXNG_URL

# Test connectivity
curl -s --max-time 5 "${SEARXNG_URL}/search?q=test&format=json" | head -c 200
```

#### Issue: JSON format not supported

**Cause:** Old SearXNG version or incorrect configuration.

**Solution:**
- Ensure `formats: [json]` is included in `config.settings.data`
- Check SearXNG version (minimum v1.0.0)

#### Issue: Connection Refused

**Cause:** SearXNG instance is not running or incorrect URL.

**Solution:**
```bash
# Check pod status
kubectl get pods -n searxng
kubectl logs -n searxng deployment/searxng
```

#### Issue: Empty Results

**Cause:** SearXNG instance blocks requests or rate limiting.

**Solution:**
- Try a different SearXNG instance (self-hosted recommended)
- Check rate-limiting settings in SearXNG configuration
- Self-hosted instances avoid rate-limiting issues

#### Issue: Slow Response Times

**Cause:** Public SearXNG instances are often overloaded.

**Solution:**
- Host your own SearXNG instance (recommended)
- Use `time_range` parameter for temporal filtering
- Use `engines` parameter for specific search engines

### Best Practices

1. **Self-host:** Avoid public instances for production use
2. **Rate Limiting:** Configure `limiter` appropriately for your infrastructure
3. **JSON Format:** Always use `format=json` for programmatic access
4. **Timeouts:** Set `--max-time` on curl commands (recommended: 10 seconds)
5. **URL Encoding:** Special characters in queries must be URL-encoded (e.g., spaces → `+`)

---

## 6. References

- [SearXNG Documentation](https://github.com/searxng/searxng)
- [Helm Chart (kubitodev)](https://artifacthub.io/packages/helm/kubitodev/searxng)
- [Hermes Agent SearXNG Skill](https://hermes-agent.nousresearch.com/docs/user-guide/skills/optional/research/research-searxng-search)
- [JSON API Specification](https://docs.searxng.org/dev/search_api.html)


