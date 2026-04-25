-- Optional Week 2 test: Cortex Search preview

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE SNOWMIND_DB;

SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
  'SNOWMIND_DB.CORTEX.KB_SEARCH',
  '{"query": "Explain refund policy", "columns": ["TITLE", "CONTENT", "CATEGORY"], "limit": 3}'
) AS preview_json;
