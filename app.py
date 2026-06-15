import os
import re
import sqlite3
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

CSV_TABLES = {
    "Data_CSV/Customers.csv": "Customers",
    "Data_CSV/sales_order.csv": "sales_order",
    "Data_CSV/Products.csv": "Products",
    "Data_CSV/Regions.csv": "Regions",
    "Data_CSV/State_Regions.csv": "State_Regions",
    "Data_CSV/2017_Budgets.csv": "Budgets_2017",
}

def ensure_database():
    db_path = "text_to_sql.db"
    conn = sqlite3.connect(db_path)
    existing = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    existing_tables = {row[0] for row in existing}
    for csv_file, table in CSV_TABLES.items():
        if table not in existing_tables and os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()

ensure_database()
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import evaluate
from ragas.metrics import RubricsScore, ContextPrecision
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset

st.set_page_config(page_title="Text-to-SQL", page_icon="🗄️", layout="wide")

# ── Cached init ──────────────────────────────────────────────────────────────
@st.cache_resource
def init():
    sqlite_uri = "sqlite:///text_to_sql.db"
    db = SQLDatabase.from_uri(sqlite_uri, sample_rows_in_table_info=3)

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0,
    )

    template = """Based on the table schema below, write a SQL query that would answer the user's question:
Remember: Only provide me the raw SQL query. Do not include markdown blocks like ```sql.
Provide the query in a single line without line breaks.

Table Schema: {schema}
Question: {question}
SQL Query:"""

    prompt = ChatPromptTemplate.from_template(template)
    sql_chain = (
        RunnablePassthrough.assign(schema=lambda _: db.get_table_info())
        | prompt
        | llm
        | StrOutputParser()
    )

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    evaluator_llm = LangchainLLMWrapper(llm)
    evaluator_embeddings = LangchainEmbeddingsWrapper(embeddings)

    return db, sql_chain, evaluator_llm

db, sql_chain, evaluator_llm = init()


def run_query(question: str):
    raw = sql_chain.invoke({"question": question}).strip()
    if "```" in raw:
        match = re.search(r"```(?:sql)?\s*(.*?)\s*```", raw, re.DOTALL | re.IGNORECASE)
        sql = match.group(1).strip() if match else raw
    else:
        sql = raw
    sql = " ".join(sql.split())
    result = db.run(sql)
    return sql, result


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🗄️ Text-to-SQL")
    st.caption("LLaMA 3.3 · RAGAS · LangChain")
    with st.expander("📋 DB Schema", expanded=False):
        st.code(db.get_table_info(), language="sql")

# ── Tabs ─────────────────────────────────────────────────────────────────────
chat_tab, eval_tab = st.tabs(["💬 Chat", "📊 Evaluate"])

# ── Chat ─────────────────────────────────────────────────────────────────────
with chat_tab:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                st.code(msg["sql"], language="sql")
                st.write("**Result:**", msg["result"])

    if question := st.chat_input("Ask something about your database…"):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Generating SQL…"):
                sql, result = run_query(question)
            st.code(sql, language="sql")
            st.write("**Result:**", result)

        st.session_state.messages.append({"role": "assistant", "sql": sql, "result": result})

# ── Eval ─────────────────────────────────────────────────────────────────────
with eval_tab:
    st.subheader("RAGAS Evaluation")

    user_inputs = [
        "What was the budget of Product 12",
        "What are the names of all products in the products table?",
        "List all customer names from the customers table.",
        "Find the name and state of all regions in the regions table.",
        "What is the name of the customer with Customer Index = 1",
    ]
    references = [
        "SELECT Budget FROM products WHERE ProductName = 'Product 12';",
        "SELECT ProductName FROM products;",
        "SELECT CustomerName FROM customers;",
        "SELECT RegionName, State FROM regions;",
        "SELECT CustomerName FROM customers WHERE CustomerIndex = 1;",
    ]

    st.write("**Test questions:**")
    for q in user_inputs:
        st.write(f"- {q}")

    if st.button("▶ Run Evaluation", type="primary"):
        context = db.get_table_info()
        helpfulness_rubrics = {
            "score1_description": "Response is useless/irrelevant, contains inaccurate/deceptive/misleading information, and/or contains harmful/offensive content.",
            "score2_description": "Response is minimally relevant and may provide some vaguely useful information, but it lacks clarity and detail.",
            "score3_description": "Response is relevant and provides some useful content, but could be more comprehensive.",
            "score4_description": "Response is very relevant, providing clearly defined information that addresses the instruction's core needs.",
            "score5_description": "Response is useful and very comprehensive with well-defined key details beyond what explicitly asked.",
        }

        rubrics_score = RubricsScore(name="helpfulness", rubrics=helpfulness_rubrics, llm=evaluator_llm)
        context_precision = ContextPrecision(llm=evaluator_llm)

        responses = []
        bar = st.progress(0, text="Generating SQL responses…")
        for i, q in enumerate(user_inputs):
            sql, _ = run_query(q)
            responses.append(sql)
            bar.progress((i + 1) / len(user_inputs), text=f"Query {i+1}/{len(user_inputs)}")

        samples = [
            SingleTurnSample(
                user_input=user_inputs[i],
                retrieved_contexts=[context],
                response=responses[i],
                reference=references[i],
            )
            for i in range(len(user_inputs))
        ]

        with st.spinner("Running RAGAS metrics…"):
            eval_result = evaluate(
                metrics=[context_precision, rubrics_score],
                dataset=EvaluationDataset(samples),
            )

        bar.empty()
        st.success("Done!")

        df = eval_result.to_pandas()
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)
        if "context_precision" in df.columns:
            col1.metric("Avg Context Precision", f"{df['context_precision'].mean():.3f}")
        if "helpfulness" in df.columns:
            col2.metric("Avg Helpfulness", f"{df['helpfulness'].mean():.3f}")
