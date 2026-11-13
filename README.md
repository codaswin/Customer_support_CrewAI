# BrewHaven Support (CrewAI)

Three sequential agents: Knowledge Base (RAG) -> Web Search fallback -> Gap Log writer.

```
cp .env.example .env   # add OPENAI_API_KEY
uv sync
uv run streamlit run app.py
uv run pytest          # no LLM calls
```
Documents live in `data/` (.txt/.pdf); rebuild the index with `uv run python ingest.py`. Fallback queries are logged to `logs/gap_log.txt`.
