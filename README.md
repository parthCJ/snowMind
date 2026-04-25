# SnowMind

Multi-agent AI assistant on Snowflake using LangGraph + Cortex Analyst + Cortex Search + Streamlit.

## 1) Environment setup (Windows)

### Python environment

```powershell
cd d:\VSCODE\snowMind
"C:/Program Files/Python313/python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

### Snowflake CLIs

Installed:

- SnowSQL: `C:\Program Files\Snowflake SnowSQL\snowsql.exe`
- Snowflake CLI: `C:\Program Files\Snowflake CLI\snow.exe`

If command not found in current terminal, restart VS Code terminal.

### Verify setup

```powershell
cd d:\VSCODE\snowMind
.\scripts\verify_setup.ps1
```

## 2) Configure credentials

1. Copy `.env.example` to `.env`
2. Fill Snowflake account and Cortex endpoints
3. Copy `snowsql_config_template.ini` to your SnowSQL config location (`%USERPROFILE%\\.snowsql\\config`) and replace placeholders

## 3) Week 1 ingestion with SnowSQL

### Create DB, schemas, formats, stages, and tables

```powershell
& "C:\Program Files\Snowflake SnowSQL\snowsql.exe" -a <account> -u <user> -r ACCOUNTADMIN -w COMPUTE_WH -f sql\week1_setup.sql
```

### Upload and load data

- Put your CSV/JSON files in `data/structured/`
- Put your docs/PDF in `data/unstructured/`
- Use commands in `sql/week1_ingestion_commands.sql`

## 4) Run app locally

```powershell
cd d:\VSCODE\snowMind
.\.venv\Scripts\Activate.ps1
pip install -e .
streamlit run app\streamlit_app.py
```

## 5) Week 2 Cortex setup

### Cortex Search setup

```powershell
cd d:\VSCODE\snowMind
.\scripts\week2_setup_cortex.ps1 -Account <account> -User <user> -Role ACCOUNTADMIN -Warehouse COMPUTE_WH
```

Note: If your trial account/region does not support Cortex Search service DDL yet, the script will still complete base setup and continue with SQL fallback retrieval.

### Cortex Search test

```powershell
cd d:\VSCODE\snowMind
.\scripts\week2_test_cortex_search.ps1 -Account <account> -User <user> -Role ACCOUNTADMIN -Warehouse COMPUTE_WH
```

### Upload semantic model for Analyst

```powershell
cd d:\VSCODE\snowMind
.\scripts\week2_upload_semantic_model.ps1 -Account <account> -User <user> -Role ACCOUNTADMIN -Warehouse COMPUTE_WH
```

### Analyst API smoke test

```powershell
cd d:\VSCODE\snowMind
.\.venv\Scripts\python.exe scripts\test_cortex_analyst_api.py
```

Notebook starter for Week 2 checks: `notebooks/week2_cortex_checks.ipynb`.

## 6) Current architecture

LangGraph nodes:

- `intent_classifier`
- `route_to_analyst`
- `route_to_search`
- `response_synthesizer`

Implementation is in `src/snowmind/orchestration/state_graph.py`.

Week 3 behavior now uses API-first routing with automatic fallback:

- Structured questions: Cortex Analyst API -> fallback SQL query on Snowflake tables
- Knowledge questions: Cortex Search API -> fallback query on `CORTEX.KNOWLEDGE_BASE`

## 7) Next implementation tasks

- Replace heuristic intent classifier with Cortex LLM call
- Parse and format Cortex Analyst/Search responses
- Add Streamlit in-Snowflake deployment configuration
- Record and attach portfolio demo video
- Add Snowflake Notebook tests for Analyst and Search endpoints

## 8) Week 4 UI status

- Query history is persisted locally at `data/app/query_history.json`
- Feedback is logged at `data/app/feedback_log.jsonl`
- Latest response panel includes source attribution and one-click feedback buttons
