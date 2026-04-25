import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("SNOWFLAKE_HOST", "").rstrip("/")
api_token = os.getenv("SNOWFLAKE_API_TOKEN", "")
semantic_model_stage_path = os.getenv(
    "ANALYST_SEMANTIC_MODEL_STAGE_PATH",
    "@SNOWMIND_DB.PUBLIC.STG_UNSTRUCTURED/semantic_model.yaml",
)

if not host or not api_token:
    raise SystemExit(
        "Set SNOWFLAKE_HOST and SNOWFLAKE_API_TOKEN in .env before running."
    )

url = f"{host}/api/v2/cortex/analyst/message"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json",
}
payload = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What were total sales by region in March 2026?",
                }
            ],
        }
    ],
    "semantic_model_file": semantic_model_stage_path,
}

response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
print(f"status_code={response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)
