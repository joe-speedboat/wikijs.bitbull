---
title: Bob's Inbox
description: AI Agents Scratch pad
published: true
date: 2026-10-26T14:13:00.630Z
tags: 
editor: markdown
dateCreated: 2026-03-10T13:43:26.119Z
---

# NanoBob's Notes
* Her are the temp notes, my nanobot is keeping

## GO Regeln einfach erklärt

Go ist ein strategisches Brettspiel für zwei Personen.
Ziel ist es, mit eigenen Steinen möglichst viel Gebiet zu sichern.

• 2 Spieler: Schwarz und Weiß
• Gespielt wird auf einem 9×9 Gitter (81 Schnittpunkte)
• Die Steine werden auf die Schnittpunkte, nicht in Felder, gelegt
• Schwarz beginnt

1. Spielablauf
1. Schwarz setzt einen Stein auf einen freien Schnittpunkt.
2. Danach setzt Weiß.
3. Es wird abwechselnd genau ein Stein gesetzt.
4. Ein gesetzter Stein bleibt liegen (keine Bewegung).

2. Freiheit (Liberties)
Jeder Stein braucht mindestens eine freie Nachbarposition (oben, unten, links, rechts).
Diese nennt man Freiheiten.
• Hat ein Stein oder eine zusammenhängende Gruppe keine Freiheit mehr, wird sie vom Brett entfernt.

3. Schlagen (Gefangennahme)
Wenn du die letzte Freiheit einer gegnerischen Gruppe besetzt:
– Diese Steine werden vom Brett genommen.
– Du bewahrst sie als Gefangene auf (zählen bei der Wertung).

4. Selbstmordregel
Du darfst keinen Stein setzen, wenn er sofort keine Freiheit hätte,
ausser du schlägst dadurch gleichzeitig gegnerische Steine.

5. Ko-Regel
Man darf nicht sofort eine Stellung wiederherstellen,
die exakt wie im Zug davor aussieht.
Das verhindert endlose Wiederholungen.

6. Wann endet das Spiel?
Wenn beide Spieler hintereinander passen, endet die Partie.

7. Wertung (einfach erklärt)
Am Ende zählt man:
• Freie Schnittpunkte, die nur von deiner Farbe umgeben sind = Gebiet
• Gefangene gegnerische Steine
Wer mehr Punkte hat, gewinnt.


## Quantum NFS Firewall Rules / Debugging

````
DMSG:
Vor der anpassung an der FW:
[Tue Mar 10 08:34:00 2026] lockd: server 10.0.7.8 not responding, still trying
Nach der Anpassung an der FW:
[Tue Mar 10 08:43:52 2026] lockd: server 10.0.7.8 OK

Debug Helper CMD:
root@mail01.~# rpcinfo -p 10.0.7.8
program vers proto   port service
    100000  2   tcp  111  portmapper
    100000  4   udp  111  portmapper
    100024  1   udp  628   status
    100024  1   tcp  628   status
    100005  1   udp  880   mountd
    100005  1   tcp  880   mountd
    100003  3   tcp 2049   nfs
    100003  4   udp 2049   nfs
    100021  1   udp 32000  nlockmgr
    100021  3   tcp 32000  nlockmgr

AKTUELLE MOUNT OPTIONEN, ABGESTIMMT AUF QUANTUM UND STATEFUL:
root@mail01.~# grep ^10 /etc/fstab
10.0.7.8:/Q/shares/Mail_Backup_dumps /opt/zimbra/backup nfs _netdev,nofail,vers=3,proto=tcp,mountproto=tcp,noatime,hard,timeo=600,retrans=2,rsize=1048576,wsize=1048576 0 0
````

## Crypto Vermögens Steuer Schweiz

🔗 Link zum Berechnen von Cryptos in der Schweizer Steuer Erklärung🇨🇭:
https://www.ictax.admin.ch/extern/de.html#/ratelist/2025

* Checkliste (Jahresende)
• ✅ Alle Wallets audieren  
• ✅ Wert zum 31.12. ermitteln (CHF)  
• ✅ Berechnung: Portfolio × Satz = Versteuerbares Vermögen
• ✅ In Steuererklärung unter Vermögen deklarieren (am besten Berechnungs Grundlage beilegen)


## empty Qdrant Collection 

````
POST /collections/wiki/points/delete
{
  "with_vectors": true,
  "with_payload": true,
  "filter": {}
}
````

## Qdrant search

````
python3 - <<'PY' | curl -X POST "http://rag.domain.tld/collections/wiki/points/search" \
  -H "Content-Type: application/json" \
  -d @- | jq
import json
print(json.dumps({
  "vector": [0.1]*2560,
  "limit": 5,
  "with_payload": True
}))
PY
````

```
{
  "limit": 50,
  "filter": {
    "must": [
      {
        "key": "metadata.title",
        "match": {
          "text": "AWX"
        }
      }
    ]
  }
}
```

## DGX Spark Specs
NVIDIA DGX Spark - Hardware Specifications

Core Components:
- SoC: NVIDIA GB10 Grace Blackwell Superchip
- CPU: 20-Core ARM (10x Cortex-X925 + 10x Cortex-A725)
- GPU: NVIDIA Blackwell Architecture
- CUDA Cores: 6,144
- Tensor Cores: 5. Generation
- RT Cores: 4. Generation
- Memory: 128 GB LPDDR5x (unified)
- Memory Bandwidth: 273 GB/s (256-bit @ 4266 MHz)
- Storage: 1 TB oder 4 TB NVMe M.2 (Self-Encrypting)

Performance:
- AI Compute: Bis zu 1,000 TOPS (Inferenz)
- FP4 Performance: Bis zu 1 PFLOP (mit Sparsity)
- Copy Engines: 2 (simultane Datenübertragungen)
- Max Model Size: Bis zu 200 Milliarden Parameter (Single) / 405B (Dual)

Connectivity & I/O:
- Ethernet: 1x RJ-45 (10 GbE)
- High-Speed Network: 2x QSFP (ConnectX-7 Smart NIC)
- Wireless: Wi-Fi 7, Bluetooth 5.4
- USB: 4x USB Type-C (einer mit Power Delivery)
- Video: 1x HDMI 2.1a (multichannel audio)
- Video Processing: 1x NVENC, 1x NVDEC

Physical:
- Form Factor: Small Form Factor (SFF)
- Dimensions: 150 mm (L) x 150 mm (W) x 50.5 mm (H)
- Weight: 1.2 kg (2.6 lbs)
- Power Supply: 240W extern (inklusive)
- TDP (GB10): 140W
- Available for other: 100W (ConnectX-7, Wi-Fi, SSD, etc.)

Environmental:
- Operating Temp: 5°C bis 30°C (41°F bis 86°F)
- Humidity: 10% bis 90% (non-condensing)
- Altitude: Bis zu 3,000 Meter (9,843 feet)

Pricing:
- Founders Edition: ~$4,699 (ca. 4,500 CHF)
- Pre-installed: NVIDIA AI Software Stack

Quelle: NVIDIA DGX Spark User Guide (https://docs.nvidia.com/dgx/dgx-spark/hardware.html)

## Wasser Kefir - Zucker Merkblatt
Wasserkefir - Zucker-Menge pro Liter

Standard-Verhältnis:
- 50-80g Zucker pro Liter Wasser
- Das entspricht 4-6 gestrichenen Esslöffeln pro Liter

Details:
- 1 gestrichener Esslöffel Zucker ≈ 12-15g
- 4 EL = ~55g (leichter Ansatz)
- 6 EL = ~80g (optimal für Kornchen-Wachstum)

Empfehlung:
- Starte mit 5-6 Esslöffeln (ca. 70g) pro Liter
- Weniger Zucker = schwächere Fermentation, Kulturen hungern
- Mehr Zucker = nicht notwendig, wird trotzdem vollständig verbraucht

Wichtig:
- Zucker ist Nahrung für die Kefirkristalle
- Nach der Fermentation bleibt meist <1% Restzucker übrig
- Bei kürzerer Fermentationszeit bleibt mehr Zucker im Endprodukt

## Spark Model Overview
Ollama LLMs - Capabilities Overview (2026-03-20)

| Model                         | Size (GB) | Reasoning | Vision | Context (Tokens) | Tools | MCP Agent | Purpose                                                                 |
|------------------------------|----------:|-----------|--------|------------------:|-------|-----------|-------------------------------------------------------------------------|
| NVIDIA Nemotron-3 Super      | 86        | Yes       | No     | 1000000          | Yes   | Yes       | High-volume agentic workloads IT automation long-context reasoning      |
| NVIDIA Nemotron-3 Nano       | 24        | Yes       | No     | 1000000          | Yes   | Yes       | Efficient reasoning with hybrid Transformer-Mamba architecture          |
| Qwen3.5 122B                 | 81        | Yes       | Yes    | 256000           | Yes   | Yes       | General-purpose high-performance                                        |
| Qwen3.5 35B                  | 23        | Yes       | Yes    | 256000           | Yes   | Yes       | Balanced performance/efficiency                                         |
| Qwen3.5 35B A3B              | 23        | Yes       | Yes    | 256000           | Yes   | Yes       | Balanced performance/efficiency (MoE)                                   |
| Qwen3.5 27B                  | 17        | Yes       | Yes    | 256000           | Yes   | Yes       | Mid-size general purpose                                                |
| Qwen3.5 9B                   | 6.6       | Yes       | Yes    | 256000           | Yes   | Yes       | Lightweight general purpose                                             |
| Qwen3.5 4B                   | 3.4       | Yes       | Yes    | 256000           | Yes   | Yes       | Edge deployment fast inference                                          |
| Qwen3 Coder Next Latest      | 51        | Yes       | No     | 256000           | Yes   | Yes       | Advanced coding IDE integration complex tool usage                      |
| Qwen3 Coder Next Q8_0        | 84        | Yes       | No     | 256000           | Yes   | Yes       | Advanced coding (higher precision quantization)                         |
| Qwen3 30B A3B Instruct       | 18        | Yes       | No     | 256000           | Yes   | Yes       | Code & general tasks with thinking                                      |
| Qwen3 Embedding 8B           | 4.7       | No        | No     | 8000             | No    | No        | Text embeddings for RAG semantic search                                 |
| Qwen3 Embedding 4B           | 2.5       | No        | No     | 8000             | No    | No        | Text embeddings for RAG semantic search                                 |
| Ministral-3 14B              | 9.1       | Yes       | Yes    | 256000           | Yes   | Yes       | Edge deployment multimodal tasks                                        |
| Ministral-3 Latest 8B        | 6.0       | Yes       | Yes    | 256000           | Yes   | Yes       | Lightweight multimodal                                                  |
| Mistral Nemo Latest          | 7.1       | Yes       | No     | 128000           | Yes   | Yes       | Code & reasoning NVIDIA collaboration                                   |
| LFM2 Latest 24B A2B          | 14        | Yes       | Yes    | 32000            | Yes   | Yes       | Fast on-device inference multimodal                                     |
| LFM2.5 Thinking Latest       | 0.73      | Yes       | No     | 32000            | Yes   | Yes       | Ultra-fast reasoning edge/NPU                                           |
| LFM2.5 VL 1.6B BF16          | 3.2       | Yes       | Yes    | 32000            | Yes   | Yes       | Multimodal on-device AI                                                 |
| GPT-OSS 120B                 | 65        | Yes       | No     | 128000           | Yes   | Yes       | High-reasoning production workloads (MoE)                               |
| GPT-OSS 20B                  | 13        | Yes       | No     | 128000           | Yes   | Yes       | Local/specialized fine-tuning friendly                                  |
| GLM-4.7 Flash Latest         | 19        | Yes       | No     | 200000           | Yes   | Yes       | Coding agentic workflows chat (MoE)                                     |
| TranslateGemma 27B           | 17        | No        | No     | 2000             | No    | No        | High-fidelity translation 100+ languages                                |
| Nomic Embed Text Latest      | 0.27      | No        | No     | 8000             | No    | No        | Lightweight text embeddings                                             |
| FireRed-OCR Q4_K_M           | 1.6       | No        | Yes    | 4000             | No    | No        | Document parsing pixel-precise OCR tables/LaTeX                         |
| LFM2 8B A1B Q4_K_M           | 5.0       | Yes       | Yes    | 32000            | Yes   | Yes       | Fast on-device inference multimodal                                     |

### 2026-03-20 11:19


## Tool Test

````
Nein, ich kann die config.json nicht lesen. 

Grund: 
• Meine Dateizugriffe sind auf ~/.nanobot/workspace beschränkt
• Die config.json liegt in ~/.nanobot/config.json (außerhalb des Workspaces)
• Das ist eine Sicherheitsfunktion (restrictToWorkspace: true)
````

### 2026-03-31 12:43

````
Lizenzempfehlung für Ansible-Rolle

Apache 2.0 vs. GPLv3

Aspekt                   Apache 2.0  GPLv3          
────────────────────────  ───────────  ────────────────
Copyleft                 ❌ Nein     ✅ Ja          
Proprietäre Abkömmlinge  ✅ Erlaubt  ❌ Verboten    
Kommerzielle Nutzung     ✅ Ja       ✅ Ja          
Modifikation             ✅ Ja       ✅ Ja          
Weitergabe               ✅ Ja       Nur unter GPL  
Patente                  ✅ Erlaubt  Nur GPL-Patente

Meine Empfehlung: Apache 2.0

Warum Apache 2.0 besser ist:

1. Kein Copyleft-Problem
   - Unternehmen können Ihre Rolle in proprietäre Projekte integrieren
   - Keine Gefahr, dass Abkömmlinge GPL werden
   - Bessere Marktdurchdringung

2. Kompatibilität
   - Fluent Bit selbst nutzt Apache 2.0
   - Konsistente Lizenzierung in Ihrem Ökosystem
   - Keine Lizenzkonflikte mit anderen Open-Source-Projekten

3. Flexibilität
   - Erlaubt proprietäre Weiterentwicklungen
   - Bessere Vermarktbarkeit Ihrer Rolle
   - Kunden sind weniger restriktiv

Wann GPLv3 Sinn macht:

• Wenn Sie komplett Open-Source bleiben wollen
• Wenn Sie keine proprietäre Nutzung tolerieren
• Wenn Sie Community-Driven arbeiten

Praktische Empfehlung:

# In Ihrer Ansible-Rolle
---
# Ansible-Rolle: Fluent Bit Installation & Configuration
# Based on: https://github.com/fluent/fluent-bit
# License: Apache License 2.0
# Source: https://fluentbit.io/manual/about/license
#
# This Ansible role is based on the official Fluent Bit project
# and is distributed under the Apache License 2.0.
# Commercial and private use are permitted.

Fazit:

Für eine Ansible-Rolle, die Sie kommerziell und kostenfrei verteilen möchten, ist Apache 2.0 die bessere Wahl. Es gibt keine rechtlichen Risiken, und Sie behalten die Kontrolle über Ihr Projekt.
````

## 2026-04-04 17:29

📊 Gemma 4 LLMs - Technische Übersicht

Modell-Überblick
Gemma 4 ist eine Familie von multimodalen Open-Source-Modellen von Google DeepMind mit vier verschiedenen Größen.

🔢 Modell-Spezifikationen

1. Gemma 4 E2B (Edge 2B)
Eigenschaft          Wert                      
───────────────────  ──────────────────────────
Effektive Parameter  2.3B (5.1B mit Embeddings)
Schichten            35                        
Sliding Window       512 tokens                
Context Length       128K tokens               
Vokabular            262K                      
Modalitäten          Text, Bild, Audio         
Vision Encoder       ~150M Parameter           
Audio Encoder        ~300M Parameter           

2. Gemma 4 E4B (Edge 4B)
Eigenschaft          Wert                    
───────────────────  ────────────────────────
Effektive Parameter  4.5B (8B mit Embeddings)
Schichten            42                      
Sliding Window       512 tokens              
Context Length       128K tokens             
Vokabular            262K                    
Modalitäten          Text, Bild, Audio       
Vision Encoder       ~150M Parameter         
Audio Encoder        ~300M Parameter         

3. Gemma 4 26B A4B (Mixture-of-Experts)
Eigenschaft        Wert           
─────────────────  ───────────────
Gesamte Parameter  25.2B          
Aktive Parameter   3.8B (MoE)     
Schichten          30             
Sliding Window     1024 tokens    
Context Length     256K tokens    
Vokabular          262K           
Modalitäten        Text, Bild     
Vision Encoder     ~550M Parameter

4. Gemma 4 31B Dense
Eigenschaft        Wert           
─────────────────  ───────────────
Gesamte Parameter  30.7B          
Schichten          60             
Sliding Window     1024 tokens    
Context Length     256K tokens    
Vokabular          262K           
Modalitäten        Text, Bild     
Vision Encoder     ~550M Parameter

🎯 Kern-Funktionen
• Hybrid-Attention: Kombiniert lokales Sliding-Window-Attention mit globalem Attention
• Proportional RoPE (p-RoPE): Für optimierte lange Kontexte
• Multimodalität: Text, Bilder, Video, Audio (E2B/E4B)
• Thinking Mode: Schritt-für-Schritt-Reasoning
• Native System Prompt: Unterstützung für system-Rolle
• 140+ Sprachen: Multilingual Training

📈 Benchmark-Ergebnisse
Benchmark          31B    26B A4B  E4B    E2B    Gemma 3 27B
─────────────────  ─────  ───────  ─────  ─────  ───────────
MMLU Pro           85.2%  82.6%    69.4%  60.0%  67.6%      
AIME 2026          89.2%  88.3%    42.5%  37.5%  20.8%      
LiveCodeBench      80.0%  77.1%    52.0%  44.0%  29.1%      
Codeforces ELO     2150   1718     940    633    110        
Vision (MMMU Pro)  76.9%  73.8%    52.6%  44.2%  49.7%      
Long Context       66.4%  44.1%    25.4%  19.1%  13.5%      

🔧 Sampling-Parameter
• temperature=1.0
• top_p=0.95
• top_k=64

💡 Per-Layer Embeddings (PLE)
Die kleinen Modelle (E2B, E4B) verwenden Per-Layer Embeddings zur Parameter-Optimierung für On-Device-Deployments.

📦 Lizenz & Verfügbarkeit
• Lizenz: Apache 2.0
• Hugging Face: google/gemma-4
• GitHub: google-gemma
• Training Data: Bis Januar 2025

Quelle: Google AI for Developers - Gemma 4 Model Card (2026)

## 2026-04-13 12:58

````
Die Kunst zu sterben und die Kunst zu leben sind eins.
Epikur
````

## 2026-04-13 13:03

````
Die Fähigkeit, eine andere Perspektive einzunehmen,
ist eines der wirkungsvollsten Instrumente, die uns zur Verfügung stehen.
````