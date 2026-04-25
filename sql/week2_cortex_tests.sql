-- Week 2 tests: validate base tables and fallback retrieval

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE SNOWMIND_DB;

SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM SALES.ORDERS
UNION ALL
SELECT 'profiles' AS table_name, COUNT(*) AS row_count FROM USERS.PROFILES
UNION ALL
SELECT 'events' AS table_name, COUNT(*) AS row_count FROM EVENTS.APP_EVENTS
UNION ALL
SELECT 'kb_docs' AS table_name, COUNT(*) AS row_count FROM CORTEX.KNOWLEDGE_BASE;

-- Fallback retrieval (works even if Cortex Search service is unavailable)
SELECT doc_id, title, category, content
FROM CORTEX.KNOWLEDGE_BASE
WHERE content ILIKE '%refund%'
ORDER BY doc_id;
