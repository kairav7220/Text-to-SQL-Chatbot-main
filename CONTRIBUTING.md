# Contributing

## Setup

```bash
git clone https://github.com/kairav7220/Text-to-SQL-Chatbot-main.git
cd Text-to-SQL-Chatbot-main
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

## Development

- Fork the repo, create a feature branch.
- Run `python create_db.py` to regenerate the SQLite database from CSVs.
- Test with `streamlit run app.py`.
- Add evaluation test queries to `user_inputs` in `app.py:134`.
- Ensure `git status` shows no `.env`, `*.db`, or `.venv/` changes.

## PR Guidelines

- One feature/fix per PR.
- Include RAGAS evaluation results if changing the LLM or prompt.
- Update `requirements.txt` if adding dependencies.

## Code Style

- `ruff` for linting (no config file needed — defaults are fine).
- Type hints on function signatures.
- No hardcoded secrets — always use `.env`.
