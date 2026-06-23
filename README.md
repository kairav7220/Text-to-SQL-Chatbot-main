<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=Text-to-SQL%20Chatbot&fontSize=50&fontAlignY=35&desc=Natural%20Language%20%E2%86%92%20SQL%20%E2%86%92%20Answers&descAlignY=55" />
</p>

<p align="center">
  <a href="https://text-to-sql-chatbot-main-qlt4z8jx8aewbafdybguyt.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Live Demo"/>
  </a>
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#evaluation">Evaluation</a> ·
  <a href="#project-structure">Structure</a> ·
  <a href="#comparison">Comparison</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white" alt="Python 3.11"/>
  <img src="https://img.shields.io/badge/LangChain-LCEL-important?logo=langchain" alt="LangChain"/>
  <img src="https://img.shields.io/badge/Gemini-2.5%20Flash-yellow" alt="Gemini 2.5 Flash"/>
  <img src="https://img.shields.io/badge/HuggingFace-all--MiniLM--L6--v2-orange?logo=huggingface" alt="all-MiniLM-L6-v2"/>
  <img src="https://img.shields.io/badge/Groq-llama--3.3--70b-orange" alt="Groq"/>
  <img src="https://img.shields.io/badge/Streamlit-UI-red?logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/RAGAS-Evaluation-success" alt="RAGAS"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"/>
</p>

---

Natural language to SQL query chatbot using LangChain, LangGraph, Groq LLM, and RAGAS evaluation.

## Features

- **Natural Language → SQL** — Ask in plain English, get SQL queries + query results
- **Agentic & Chain Modes** — LangGraph ReAct agent (tool-calling) + LangChain LCEL chain
- **Multi-LLM Support** — Groq (Llama 3.3 70B) + Google Gemini (2.0/2.5 Flash)
- **RAGAS Evaluation** — Built-in quality scoring (Context Precision, Helpfulness Rubrics)
- **Streamlit UI** — Chat interface with live schema viewer and evaluation dashboard
- **CSV → SQLite Pipeline** — Zero-config database setup from CSV files

## Architecture

```mermaid
flowchart LR
  User["🙋 User Question"] --> UI["Streamlit UI"]
  UI --> Chain["LCEL Chain<br/>(Prompt → LLM → Parser)"]
  UI --> Agent["LangGraph Agent<br/>(ReAct: Tools + LLM)"]
  
  Chain --> LLM1["Groq Llama 3.3<br/>or Gemini 2.5 Flash"]
  Agent --> Tools["SQL Toolkit<br/>(List/Query/Schema/Check)"]
  Tools --> DB[("SQLite Database")]
  LLM1 --> DB
  
  DB --> Results["Query Results"]
  Results --> UI
  
  UI --> Eval["RAGAS Evaluator<br/>(Context Precision + Helpfulness)"]
  Eval --> Dashboard["Evaluation Dashboard"]
```

| Component | Stack |
|---|---|
| **Frontend** | Streamlit (chat + eval tabs) |
| **Orchestration** | LangChain LCEL + LangGraph `create_react_agent` |
| **LLM** | Groq `llama-3.3-70b-versatile`, Gemini `2.0-flash` / `2.5-flash` |
| **Database** | SQLite (auto-seeded from CSVs) |
| **Evaluation** | RAGAS (Context Precision, Rubrics-based Helpfulness) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |

## Quick Start

```bash
git clone https://github.com/kairav7220/Text-to-SQL-Chatbot-main.git
cd Text-to-SQL-Chatbot-main
pip install -r requirements.txt
```

Set your API keys in `.env`:

```env
GROQ_API_KEY="gsk_..."
GOOGLE_API_KEY="AIza..."
```

```bash
streamlit run app.py
```

## Usage

```bash
streamlit run app.py   # Chat + Evaluation UI
python 1.py            # Gemini chain (single query)
python 2.py            # Groq chain + RAGAS on 5 queries
python create_db.py    # Reload CSVs into SQLite
```

## Evaluation

Sample RAGAS results (Groq Llama 3.3 70B on 5 benchmark queries):

| Metric | Score |
|---|---|
| Context Precision | 1.0000 |
| Helpfulness (Rubrics) | 3.80 / 5.00 |

## Comparison

| Feature | This Project | LangChain SQL Agent | SQLAlchemy + Hand-coded |
|---|---|---|---|
| UI | ✅ Streamlit | ❌ CLI only | ❌ |
| RAGAS Evaluation | ✅ Built-in | ❌ | ❌ |
| Agentic Reasoning | ✅ LangGraph | ✅ | ❌ |
| Multi-LLM | ✅ Groq + Gemini | ✅ | ❌ |
| CSV → DB Seeding | ✅ Auto | ❌ | ❌ |


## Project Structure

```
Text-to-SQL-Chatbot-main/
├── app.py                  # Streamlit app (chat + eval)
├── 1.py                    # Gemini LCEL chain
├── 2.py                    # Groq chain + RAGAS script
├── create_db.py            # CSV → SQLite migration
├── Data_CSV/               # Source CSV files (7 tables)
├── data_dump/              # Additional CSV exports
├── requirements.txt        # Python dependencies
├── CONTRIBUTING.md         # Contribution guide
├── llms.txt                # AI assistant context
├── .gitignore
└── LICENSE
```

## License

MIT © [kairav7220](https://github.com/kairav7220)

---

<p align="center">
  Built with <a href="https://python.langchain.com">LangChain</a> ·
  <a href="https://langchain-ai.github.io/langgraph">LangGraph</a> ·
  <a href="https://groq.com">Groq</a> ·
  <a href="https://docs.ragas.io">RAGAS</a>
</p>
