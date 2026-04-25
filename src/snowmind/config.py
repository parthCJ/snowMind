from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    account: str = os.getenv("SNOWFLAKE_ACCOUNT", "")
    user: str = os.getenv("SNOWFLAKE_USER", "")
    password: str = os.getenv("SNOWFLAKE_PASSWORD", "")
    role: str = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    warehouse: str = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    database: str = os.getenv("SNOWFLAKE_DATABASE", "SNOWMIND_DB")
    schema: str = os.getenv("SNOWFLAKE_SCHEMA", "SALES")
    analyst_endpoint: str = os.getenv("CORTEX_ANALYST_ENDPOINT", "")
    search_endpoint: str = os.getenv("CORTEX_SEARCH_ENDPOINT", "")
    api_token: str = os.getenv("SNOWFLAKE_API_TOKEN", "")


settings = Settings()
