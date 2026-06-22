# AI CEO Strategic Intelligence Agent

## Project Overview

This project is an AI-powered Strategic Intelligence Agent built for Microsoft. It collects and processes public information, converts it into a searchable knowledge repository, retrieves evidence using FAISS vector search, and generates strategic insights for executive decision-making.

The system is designed to support a CEO or senior management team by identifying market signals, opportunities, risks, public sentiment, and evidence-based strategic recommendations. It also includes a CEO Briefing module powered by a local open-source LLM through Ollama, with follow-up Q&A support.

## Company Selected

**Company:** Microsoft
**Industry:** Technology, Cloud Computing, AI, Software, Productivity, Gaming, Cybersecurity

## Key Features

### 1. Company Overview

Shows repository health and source coverage:

* Raw documents
* Cleaned documents
* Chunks
* Indexed FAISS vectors
* Unique sources
* Last data update
* Source distribution

### 2. Market Intelligence

Classifies collected documents into strategic market signals:

* Company announcements
* Competitor activity
* Emerging technologies
* Opportunity signals
* Risk signals

The user can filter by topic, such as AI, Copilot, Azure, Windows, GitHub, Xbox, security, or regulation.

### 3. Opportunity Monitor

Identifies strategic opportunities from collected evidence.

Each opportunity includes:

* Opportunity theme
* Impact level
* Confidence score
* Strategic rationale
* Supporting evidence

### 4. Risk Monitor

Detects potential strategic risks.

Each risk includes:

* Risk category
* Severity level
* Confidence score
* Suggested mitigation
* Supporting evidence

Risk categories include cybersecurity, AI governance, regulatory compliance, competitive pressure, product adoption, cloud infrastructure, reputation, and partner ecosystem risk.

### 5. Sentiment Analysis

Analyzes public, news, and official sentiment signals using transparent lexicon-based scoring.

The sentiment page includes:

* Overall sentiment score
* Positive, negative, and neutral distribution
* Sentiment by source group
* Sentiment trend over time
* Most positive and most negative documents
* Public/community sentiment where available

### 6. Strategic Recommendations

Combines opportunity signals, risk signals, sentiment, and evidence into prioritized strategic recommendation cards.

Each recommendation includes:

* Priority
* Confidence
* Expected impact
* Risk assessment
* Execution plan
* Recommended owners
* KPIs
* Supporting evidence
* Related risks

### 7. CEO Briefing

Generates an evidence-based executive briefing using:

* FAISS retrieval
* Local open-source LLM through Ollama
* Prompt engineering
* Retrieved evidence
* Confidence scoring
* Fallback playbook if the LLM is slow or incomplete

The CEO Briefing supports dynamic questions, such as:

* What should Microsoft do about Xbox?
* How should Microsoft improve GitHub developer strategy?
* What should Microsoft prioritize for Copilot adoption?
* What risks are emerging around AI regulation?
* What should Microsoft do next with Windows strategy?

### 8. Strategic Follow-up Q&A

After a CEO briefing is generated, the user can ask follow-up questions.

Examples:

* How should Microsoft execute Action 1 in the next 90 days?
* What KPIs should the CEO track?
* Which business unit should own this recommendation?
* What risks could block this strategy?
* What additional evidence would improve confidence?

### 9. Data Pipeline & Refresh

The project includes a refreshable intelligence pipeline:

* Data collection
* Cleaning
* Deduplication
* Chunking
* Embedding generation
* FAISS index building
* Repository audit

For demo reliability, the dashboard uses cached indexed data. The pipeline can be rerun to refresh the repository.

## Architecture

```text
Public Sources
    ↓
Collectors
    ↓
Raw Documents
    ↓
Cleaning and Deduplication
    ↓
Chunking
    ↓
SentenceTransformer Embeddings
    ↓
FAISS Vector Index
    ↓
Retriever
    ↓
Strategic Intelligence Modules
    ↓
Dashboard Pages
    ↓
CEO Briefing + Follow-up Q&A
```

## Project Structure

```text
Microsoft_Strategic_Intelligence_Agent/
│
├── app.py
├── main.py
├── README.md
├── requirements.txt
│
├── collectors/
│   ├── manager.py
│   ├── microsoft_blog_collector.py
│   ├── azure_blog_collector.py
│   ├── security_blog_collector.py
│   ├── reddit_collector.py
│   ├── news_collector.py
│   └── extra_sources_collector.py
│
├── data/
│   ├── raw_documents.json
│   ├── cleaned_documents.json
│   ├── chunks.json
│   ├── embeddings.npy
│   └── faiss_index/
│       ├── index.faiss
│       └── metadata.pkl
│
├── preprocessing/
│   ├── cleaner.py
│   ├── duplication.py
│   └── chunker.py
│
├── embeddings/
│   └── embedder.py
│
├── vectorstore/
│   └── faiss_store.py
│
├── retrieval/
│   └── retriever.py
│
├── intelligence/
│   ├── market_analyzer.py
│   ├── opportunity_analyzer.py
│   ├── risk_analyzer.py
│   ├── recommendation_engine.py
│   └── strategic_analyzer.py
│
├── sentiment/
│   └── sentiment_analyzer.py
│
├── llm/
│   ├── ollama_client.py
│   └── prompts.py
│
├── dashboard/
│   ├── overview.py
│   ├── market_intelligence.py
│   ├── opportunity_monitor.py
│   ├── risk_monitor.py
│   ├── sentiment_view.py
│   ├── recommendations.py
│   ├── pipeline_status.py
│   └── ceo_briefing_view.py
│
└── utils/
    ├── config.py
    ├── data_loader.py
    ├── pipeline_runner.py
    └── audit_project.py
```

## Technologies Used

* Python
* Streamlit
* FAISS
* SentenceTransformers
* Ollama
* Local open-source LLM
* Pandas
* NumPy
* Requests
* BeautifulSoup
* JSON and Pickle-based storage

## LLM Setup

The system uses Ollama for local LLM generation.

Recommended live demo model:

```powershell
ollama pull llama3.2:3b
$env:OLLAMA_MODEL="llama3.2:3b"
streamlit run app.py
```

Optional deeper model:

```powershell
ollama pull qwen3:8b
$env:OLLAMA_MODEL="qwen3:8b"
streamlit run app.py
```

For live presentation, a smaller model is recommended because executive dashboards need stable response time.

## How to Run

### 1. Activate virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Start Ollama

```powershell
ollama serve
```

If Ollama is already running, skip this step.

### 3. Run Streamlit dashboard

```powershell
streamlit run app.py
```

### 4. Open the dashboard

Usually:

```text
http://localhost:8501
```

## Manual Pipeline Refresh

Run these commands from the project root if a full refresh is needed:

```powershell
python -m collectors.manager
python -m preprocessing.cleaner
python -m preprocessing.duplication
python -m preprocessing.chunker
python -m embeddings.embedder
python -m vectorstore.faiss_store
python -m utils.audit_project
```

For live demos, it is safer to run only:

```powershell
python -m utils.audit_project
```

## Reliability Design

The dashboard is designed to avoid depending completely on a live LLM call.

Reliability features include:

* Cached FAISS retriever
* Cached embedding model loading
* Streaming Ollama responses
* Short fast briefing mode
* Deep playbook mode
* Fallback strategic playbook if the LLM fails
* Repository audit page
* Manual refresh commands
* Evidence display for transparency

## Current Repository Status

At the time of development, the system contained approximately:

* 115 raw documents
* 114 cleaned documents
* 1421 chunks
* 1421 FAISS-indexed vectors
* 10 unique sources

## Limitations

* The system can only answer well for topics represented in the collected repository.
* Sentiment analysis uses a lightweight lexicon-based method, so it should be interpreted as a weak signal rather than a final decision.
* Live data collection depends on source availability, internet connection, and page structure.
* Local LLM performance depends on the machine and selected Ollama model.
* The system is a prototype and not a production-grade enterprise deployment.

## Future Improvements

* Add scheduled background refresh jobs
* Add stronger competitor intelligence sources
* Add financial and stock market signals
* Add more Reddit/community sources
* Add model-based sentiment classification
* Add user authentication
* Add persistent chat history
* Add exportable PDF CEO briefings
* Add evaluation metrics for retrieval quality
* Add source freshness scoring
* Deploy dashboard to a cloud platform

## Final Project Positioning

This project is not only a chatbot. It is a strategic intelligence system that combines data collection, preprocessing, vector search, evidence retrieval, risk analysis, opportunity detection, sentiment analysis, recommendation generation, and executive briefing.

The CEO Briefing module acts as the conversational decision layer on top of a structured intelligence pipeline.
