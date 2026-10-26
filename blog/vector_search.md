---
title: Vector Search Overview
description: Popular AI Data Search Products
published: true
date: 2026-10-26T09:12:19.844Z
tags: ai, agent, vector
editor: markdown
dateCreated: 2026-10-26T09:12:19.844Z
---


# Vector Search Products

This page compares twelve commonly used tools for vector search, semantic retrieval, and retrieval-augmented generation (RAG). The products range from managed vector databases to database extensions, search platforms, and low-level libraries.

![vector_search.png](/pics/vector_search.png)



# Overview

GitHub stars and origin year are included for open-source or source-available products where a canonical repository was checked. Star counts were checked on 2026-07-08.

| Name | Vendor / maintainer | Description | License / model | GitHub stars | Origin year |
|---|---|---|---|---:|---:|
| Pinecone | Pinecone Systems, Inc. | Fully managed vector database for semantic search, hybrid search, RAG, and AI applications without operating database infrastructure. | Proprietary managed SaaS / commercial service. | — | — |
| Weaviate | Weaviate B.V. / Weaviate project | Open-source vector database with object schema, hybrid BM25 + vector search, modules, multi-tenancy, and managed cloud offering. | BSD 3-Clause for the open-source repository. | 16,536 | 2016 |
| Milvus | LF AI & Data Foundation / Zilliz | Distributed open-source vector database designed for large-scale similarity search and high-volume embedding workloads. | Apache License 2.0. | 45,129 | 2019 |
| Qdrant | Qdrant Solutions GmbH / Qdrant project | Vector search engine and vector database focused on performance, filtering, payload metadata, and production APIs. | Apache License 2.0. | 33,020 | 2020 |
| Chroma | Chroma / Chroma project | Developer-friendly embedding database for local and application-level RAG workflows, with local, HTTP, and cloud usage patterns. | Apache License 2.0. | 28,725 | 2022 |
| pgvector | pgvector project / PostgreSQL ecosystem | PostgreSQL extension that adds vector data types, vector indexes, and similarity search directly inside PostgreSQL. | PostgreSQL-style permissive license. | 22,110 | 2021 |
| FAISS | Meta AI / Facebook Research | Low-level library for efficient similarity search and clustering of dense vectors; often embedded into custom systems. | MIT License. | 40,462 | 2017 |
| Vespa | Vespa.ai / Vespa Engine project | Open-source serving engine for search, recommendation, vector retrieval, ranking, and structured data at large scale. | Apache License 2.0. | 6,996 | 2016 |
| MongoDB Atlas Vector Search | MongoDB, Inc. | Managed MongoDB Atlas feature for storing embeddings and querying vector search indexes inside MongoDB Atlas collections. | Proprietary managed Atlas feature; MongoDB server code is SSPL in community distributions. | — | — |
| Redis Vector Search | Redis Ltd. / Redis project | Vector search through Redis Query Engine / RediSearch-style capabilities, suited for low-latency real-time workloads and semantic cache patterns. | Redis 8+ uses RSALv2 / SSPLv1 / AGPLv3 tri-license; Redis 7.2 and earlier used BSD 3-Clause. | 75,330 | 2009 |
| Elasticsearch | Elastic N.V. | Search and analytics engine with keyword, structured, vector, hybrid, and ES,QL search capabilities. | Elasticsearch source is generally triple-licensed under AGPLv3-only, SSPLv1, and Elastic License 2.0, with some components under Apache-compatible or Elastic-only terms. | 77,457 | 2010 |
| LanceDB | LanceDB / Lance project | Embedded and serverless vector database built around the Lance columnar format; useful for local multimodal AI and vector search applications. | Apache License 2.0. | 10,824 | 2023 |

# Product notes

## Pinecone

**Concrete application example:** A SaaS support portal indexes help-center articles, product documentation, and resolved support tickets in Pinecone. The chatbot embeds a user question, retrieves the most relevant chunks from Pinecone, and sends them to an LLM for grounded answers with citations.

**MCP and n8n support:** n8n has native Pinecone Vector Store and Pinecone Assistant integrations for RAG workflows. Pinecone can also be exposed to MCP clients through n8n workflow templates or a custom MCP wrapper, but the checked public sources did not show a product-native Pinecone MCP server equivalent to the official Weaviate, Qdrant, Redis, or MongoDB servers.

## Weaviate

**Concrete application example:** An internal knowledge base stores documents with metadata such as department, document type, owner, and validity period. Users can run hybrid keyword + vector searches, while filters restrict results to the correct department and current documents.

**MCP and n8n support:** Supported. Weaviate includes an MCP server from Weaviate v1.38 when enabled with `MCP_SERVER_ENABLED=true`. n8n has a Weaviate Vector Store node that can insert documents, retrieve documents, act as a retriever, or connect directly to an AI Agent as a tool.

## Milvus

**Concrete application example:** A media archive stores image and video embeddings in Milvus. Editors can upload a reference image and retrieve visually similar assets across millions of stored vectors.

**MCP and n8n support:** Supported. Milvus documents an MCP setup using `zilliztech/mcp-server-milvus`, with tools for listing collections, vector search, hybrid search, insert, upsert, and delete operations. n8n has a Milvus Vector Store node for RAG workflows and AI Agent tool usage.

## Qdrant

**Concrete application example:** An e-commerce search service stores product embeddings and payload metadata such as category, price range, availability, and brand. Qdrant performs semantic search while payload filters enforce stock and category constraints.

**MCP and n8n support:** Supported. Qdrant maintains an official `qdrant/mcp-server-qdrant` server with tools such as `qdrant-store` and `qdrant-find`. n8n has a Qdrant Vector Store node supporting document insert, retrieval, retriever mode, and AI Agent tool mode.

## Chroma

**Concrete application example:** A developer runs a local RAG prototype on a laptop, indexing Markdown notes and API documentation into Chroma before moving the design to a production vector store.

**MCP and n8n support:** Supported. Chroma has `chroma-core/chroma-mcp`, an MCP server for local, persistent, HTTP, and Chroma Cloud client modes. n8n has a Chroma Vector Store node for insert, retrieval, retriever mode, and AI Agent tool mode.

## pgvector

**Concrete application example:** A product database already runs on PostgreSQL. The team adds a `vector` column to store embeddings for products or documents, then uses pgvector indexes to support semantic search without introducing a separate vector database.

**MCP and n8n support:** Partially supported. n8n has a PGVector Vector Store node for PostgreSQL tables with vector columns. For MCP, pgvector itself does not appear to provide a dedicated official MCP server; practical integration is usually through PostgreSQL MCP servers, custom SQL tools, or a custom MCP wrapper that knows the pgvector schema.

## FAISS

**Concrete application example:** A research team builds an offline benchmark that compares embedding models over a static dataset. FAISS stores the vectors locally and performs fast nearest-neighbor search without running a database service.

**MCP and n8n support:** Not directly supported as a product integration in the checked sources. FAISS is a library rather than a server product. It can be used behind a custom API, Python service, LangChain component, or custom MCP server. n8n does not have a standard FAISS Vector Store node comparable to its Pinecone, Qdrant, Milvus, Chroma, Weaviate, PGVector, MongoDB Atlas, or Redis nodes.

## Vespa

**Concrete application example:** A recommendation platform combines structured filters, text relevance, vector similarity, and custom ranking functions to serve personalized search results under low latency.

**MCP and n8n support:** Not directly supported in the checked sources. Vespa exposes APIs that can be called from n8n using HTTP Request or custom code, but no native n8n Vespa Vector Store node was verified. No official Vespa MCP server was verified; MCP integration would normally require a custom wrapper around Vespa query and document APIs.

## MongoDB Atlas Vector Search

**Concrete application example:** An application already stores customer-facing content in MongoDB Atlas. It adds embeddings and a Vector Search index to the same collection, allowing semantic search without moving data to a separate vector database.

**MCP and n8n support:** Supported. n8n has a MongoDB Atlas Vector Store node for Atlas Vector Search indexes. MongoDB also provides `mongodb-js/mongodb-mcp-server`, an MCP server for MongoDB databases and MongoDB Atlas clusters. The MCP server is database-oriented; vector-search-specific behavior depends on how the Atlas collection and indexes are modeled.

## Redis Vector Search

**Concrete application example:** A chat application uses Redis as a semantic cache. Incoming prompts are embedded and compared against previous prompts; if a close match exists, the application reuses a cached response or context instead of calling a costly LLM path.

**MCP and n8n support:** Supported. n8n has a Redis Vector Store node that requires Redis Query Engine / Redis Open Source 8.0+ capabilities. Redis also maintains `redis/mcp-redis`, an official MCP server that supports managing and searching data in Redis, including vector-search-style use cases.

## Elasticsearch

**Concrete application example:** A log analytics platform combines traditional keyword search, structured filters, vector search over embedded incident notes, and ranking to find similar historical incidents during on-call investigations.

**MCP and n8n support:** Partially supported. n8n has a generic Elasticsearch node, but the checked n8n docs did not expose a native Elasticsearch Vector Store node path. Elastic has an Elasticsearch MCP server repository, but it is marked deprecated and superseded by Elastic Agent Builder MCP endpoint support in Elastic 9.2.0+ and Elasticsearch Serverless projects.

## LanceDB

**Concrete application example:** A local AI application stores image embeddings and text embeddings on disk using LanceDB, then performs multimodal search without running a separate server.

**MCP and n8n support:** Not directly supported in the checked sources. LanceDB can be used from Python/JavaScript applications and wrapped behind a custom HTTP service, custom MCP server, or n8n Code/HTTP workflow. No native n8n LanceDB Vector Store node or official LanceDB MCP server was verified from the checked sources.

# Practical selection guidance

| Situation | Good candidates |
|---|---|
| Fastest managed vector DB setup | Pinecone, MongoDB Atlas Vector Search, Weaviate Cloud, Qdrant Cloud, Zilliz Cloud |
| Self-hosted open-source vector database | Weaviate, Milvus, Qdrant, Chroma, Vespa |
| Existing PostgreSQL estate | pgvector |
| Existing MongoDB Atlas estate | MongoDB Atlas Vector Search |
| Existing Redis estate / semantic cache | Redis Vector Search |
| Existing Elasticsearch estate | Elasticsearch vector and hybrid search |
| Local prototype / embedded application | Chroma, LanceDB, FAISS |
| Very large-scale distributed vector workloads | Milvus, Vespa, Qdrant, Weaviate |
| Low-level custom nearest-neighbor library | FAISS |

# Sources

- Pinecone n8n integration: https://docs.pinecone.io/integrations/n8n
- n8n Vector Store docs: Pinecone, Weaviate, Milvus, Qdrant, Chroma, PGVector, MongoDB Atlas, Redis
- Weaviate MCP server docs: https://docs.weaviate.io/weaviate/configuration/mcp-server
- Milvus MCP and n8n docs: https://milvus.io/docs/milvus_and_mcp.md and https://milvus.io/docs/milvus_and_n8n.md
- Qdrant MCP server: https://github.com/qdrant/mcp-server-qdrant
- Chroma MCP server: https://github.com/chroma-core/chroma-mcp
- MongoDB MCP server: https://github.com/mongodb-js/mongodb-mcp-server
- Redis MCP server: https://github.com/redis/mcp-redis
- Elasticsearch MCP server: https://github.com/elastic/mcp-server-elasticsearch
- GitHub license metadata and license files for Weaviate, Milvus, Qdrant, Chroma, pgvector, FAISS, Vespa, LanceDB, Elasticsearch, and Redis
