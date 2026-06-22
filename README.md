# 🧠 Microsoft Intelligent System

### AI CEO Strategic Intelligence Agent

An AI-powered Strategic Intelligence Platform that combines Retrieval-Augmented Generation (RAG), Hybrid Search (FAISS + BM25), Sentiment Analysis, Competitor Intelligence, and Executive Decision Support to generate evidence-based recommendations for leadership teams.

---

## 📌 Project Overview

Organizations generate massive amounts of information through news articles, technology blogs, competitor announcements, market reports, and product releases.

Manually analyzing this information is time-consuming and often results in missed opportunities and risks.

The Microsoft Intelligent System automatically collects, processes, analyzes, and transforms unstructured business intelligence into executive-level insights using NLP, Information Retrieval, and Large Language Models.

The system acts as an AI-powered CEO advisor capable of:

* Monitoring Microsoft and competitor activity
* Detecting strategic opportunities and risks
* Performing sentiment and topic analysis
* Retrieving relevant evidence using Hybrid Search
* Generating CEO-level strategic briefings
* Producing actionable business recommendations

---

# 🎯 Objectives

* Build a complete NLP pipeline for strategic intelligence
* Implement Retrieval-Augmented Generation (RAG)
* Use Hybrid Search (FAISS + BM25)
* Analyze sentiment and strategic signals
* Compare Microsoft against competitors
* Generate evidence-based executive recommendations
* Visualize intelligence through an interactive dashboard

---

# 🏗️ System Architecture

![Workflow](screenshots/workflow.png)

---

# 🔄 Data Flow Diagram
![Data Flow](screenshots/data flow.png)

---
# 📸 Dashboard Screenshots

The AI CEO Strategic Intelligence Agent provides an interactive Streamlit dashboard for executive decision support.

---

## 🧠 CEO Briefing

Generates evidence-based executive recommendations using Hybrid Retrieval (FAISS + BM25), RAG, and a local LLM.

![CEO Briefing](screenshots/ceo_briefing.png)
---

## 📊 Project Overview

Provides a high-level summary of the strategic intelligence platform, workflow, and business objectives.

![Overview](screenshots/overview.png)

---

## 📈 Sentiment Intelligence

Analyzes sentiment, topics, and strategic signals across collected intelligence documents.

![Sentiment Intelligence](screenshots/sentiment.png)

---

## 🌍 Market Intelligence

Tracks market trends, topic distribution, source coverage, and competitor activity.

![Market Intelligence](screenshots/market.png)

---

## 🏁 Competitor Intelligence

Compares Microsoft against AWS, Google Cloud, OpenAI, NVIDIA, and other competitors.

![Competitor Intelligence](screenshots/competitor.png)

---

## 🚀 Opportunity Monitor

Identifies business growth opportunities and emerging strategic initiatives.

![Opportunity Monitor](screenshots/opportunity.png)

---

## ⚠️ Risk Monitor

Tracks cybersecurity, governance, compliance, and competitive risk signals.

![Risk Monitor](screenshots/risk.png)

---

## ✅ Executive Recommendations

Provides strategic recommendations derived from retrieved evidence and intelligence analysis.

![Recommendations](screenshots/recommendation.png)


# 🚀 Key Features

## 1. Competitor Intelligence

Tracks strategic activity from:

* Microsoft
* AWS
* Google Cloud
* OpenAI
* NVIDIA

Provides comparative intelligence and competitor monitoring.

---

## 2. Hybrid Retrieval (FAISS + BM25)

Combines:

### Semantic Search

* Sentence Transformers
* FAISS Vector Database

### Keyword Search

* BM25 Ranking

Benefits:

* Better recall
* Better precision
* Improved retrieval diversity
* Stronger evidence quality
## Retrieval Evaluation

The system uses a Hybrid Retrieval approach combining FAISS Semantic Search and BM25 Keyword Search.

### Why Hybrid Retrieval?

FAISS retrieves documents based on semantic meaning and contextual similarity, while BM25 retrieves documents using exact keyword matching.

In strategic intelligence systems, both capabilities are important:

- Semantic retrieval helps identify related business developments even when different wording is used.
- Keyword retrieval ensures that exact company names, technologies, products, and competitors are not missed.
- Hybrid retrieval combines both approaches to improve evidence quality for executive decision-making.

### Retrieval Comparison

| Query | FAISS Retrieval | BM25 Retrieval | Hybrid Retrieval |
|---------|---------|---------|---------|
| Microsoft AI investments | Retrieved semantically related AI investment articles | Retrieved exact Microsoft investment announcements | Combined both relevant context and exact evidence |
| Azure cloud competition | Retrieved cloud market trends and related competitors | Retrieved articles containing Azure and competitor names | Produced the most complete competitive analysis |
| NVIDIA partnership announcements | Retrieved semiconductor and AI partnership content | Retrieved exact NVIDIA partnership news | Improved evidence coverage |
| OpenAI enterprise adoption | Retrieved enterprise AI adoption discussions | Retrieved exact OpenAI references | Generated stronger business intelligence context |

### Observations

- FAISS performs well when similar concepts are expressed using different wording.
- BM25 performs well when exact terms such as company names, products, regulations, or technologies are present.
- Hybrid Retrieval consistently produced the highest quality evidence because it combines semantic understanding with keyword precision.

### Conclusion

The Hybrid Retrieval architecture was selected because executive intelligence tasks require both semantic reasoning and exact fact retrieval. Combining FAISS and BM25 improves retrieval accuracy, evidence diversity, and recommendation quality.
---

## 3. Strategic Signal Detection

Documents are classified into:

* Opportunity
* Risk
* Neutral
* Irrelevant

Used for executive-level decision support.

---

## 4. Sentiment Analysis

Analyzes:

* Positive sentiment
* Negative sentiment
* Neutral sentiment

Provides market perception and business sentiment insights.

---

## 5. CEO Strategic Briefing

Supports questions such as:

* What AI strategy should Microsoft prioritize?
* How should Microsoft compete with AWS and Google Cloud?
* What are Microsoft's biggest cybersecurity risks?
* What strategic opportunities should Microsoft pursue?

The system retrieves relevant evidence and generates executive recommendations.

---

# 🛠️ Technologies Used

| Category | Technologies |
|-----------|-------------|
| Programming Language | Python |
| NLP | Sentence Transformers, Transformers |
| Retrieval | FAISS, BM25 |
| RAG | Hybrid Retrieval + Context Builder |
| LLM | Ollama |
| Data Processing | Pandas, NumPy |
| Dashboard | Streamlit |
| Data Collection | RSS Feeds, Technology Blogs |
| Storage | JSON Files |
| Visualization | Streamlit Charts |

---
# ⚙️ Design Decisions

## Why Hybrid Retrieval?

The system combines FAISS semantic retrieval with BM25 keyword retrieval.

Reasons:

- FAISS captures semantic similarity between documents and queries.
- BM25 captures exact keywords and company names.
- Combining both improves retrieval accuracy and evidence diversity.
- Better evidence leads to higher-quality strategic recommendations.

---

## Why Character-Based Chunking?

The project uses overlapping character-based chunking.

Reasons:

- Produces consistent chunk sizes for embeddings.
- Preserves context using overlap.
- Improves retrieval recall.
- Works effectively with FAISS vector search.

Although some evidence previews may begin mid-sentence, retrieval quality and LLM reasoning remain unaffected.

---

## Why Local LLM (Ollama)?

The system uses Ollama to run Large Language Models locally.

Benefits:

- No API costs.
- Better privacy.
- Offline execution.
- Easier academic demonstration.

---

## Why Streamlit?

Streamlit provides a lightweight framework for building interactive dashboards.

Benefits:

- Rapid development.
- Easy visualization of intelligence outputs.
- Supports interactive executive decision-making workflows.


# 📂 Project Structure

```text
Microsoft-Intelligent-System/
│
├── collectors/
├── preprocessing/
├── embeddings/
├── vectorstore/
├── retrieval/
├── sentiment/
├── intelligence/
├── dashboard/
├── utils/
├── data/
│
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

# 🤖 AI Pipeline

The project follows a complete NLP and Retrieval-Augmented Generation (RAG) pipeline:

```text
Document Collection
(RSS feeds, blogs, news, competitor sources)
        │
        ▼
Data Cleaning & Deduplication
(Remove HTML, normalize text, remove duplicates)
        │
        ▼
Chunking & Metadata Enrichment
(Create overlapping chunks and add source information)
        │
        ▼
Embedding Generation
(Sentence Transformers)
        │
        ▼
Index Construction
(FAISS Vector Index + BM25 Keyword Index)
        │
        ▼
Hybrid Retrieval
(Combine semantic and keyword search results)
        │
        ▼
Evidence Retrieval
(Select most relevant document chunks)
        │
        ▼
NLP Analysis
• Sentiment Analysis
• Topic Classification
• Strategic Signal Detection
        │
        ▼
RAG Context Builder
(Prepare structured context for the LLM)
        │
        ▼
Local LLM (Ollama)
(Generate strategic insights and reasoning)
        │
        ▼
CEO Briefing Generation
(Risks, Opportunities, Recommendations)
        │
        ▼
Dashboard Visualization
(Streamlit Dashboard with executive insights)
```


---

# ▶️ Installation

Clone the repository:

```bash
git clone https://github.com/janvimahapadi-hub/Microsoft-Intelligent-System.git
cd Microsoft-Intelligent-System
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

---

# 🧪 Example Strategic Questions

* How should Microsoft compete with AWS and Google Cloud in AI infrastructure?
* What are Microsoft's top strategic opportunities?
* Which competitor poses the biggest threat?
* How should Microsoft monetize AI agents?
* What risks could slow enterprise AI adoption?

---

# 📈 Future Improvements

* Real-time news monitoring
* Automated weekly intelligence reports
* Multi-company benchmarking
* Advanced topic modeling
* Agent-based intelligence workflows
* Forecasting and trend prediction

---

# 🎓 Academic Relevance

This project demonstrates concepts from:

* Natural Language Processing
* Information Retrieval
* Retrieval-Augmented Generation (RAG)
* Sentiment Analysis
* Vector Databases
* Semantic Search
* Executive Decision Support Systems
* Strategic Intelligence Platforms

---

# 👩‍💻 Author

Janvi Mahapadi

Master's Student – Applied Data Science & Artificial Intelligence

SRH University Heidelberg

Germany
