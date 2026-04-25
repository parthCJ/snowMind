-- Week 2 setup: Cortex foundation (base objects)

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE SNOWMIND_DB;

CREATE SCHEMA IF NOT EXISTS CORTEX;

CREATE OR REPLACE TABLE CORTEX.KNOWLEDGE_BASE (
  doc_id STRING,
  title STRING,
  category STRING,
  content STRING
);

INSERT OVERWRITE INTO CORTEX.KNOWLEDGE_BASE (doc_id, title, category, content)
SELECT 'DOC-001', 'Refund Policy', 'policy',
       'Customers can request a refund within 14 days of purchase. Enterprise contracts may include custom refund terms.'
UNION ALL
SELECT 'DOC-002', 'Shipping Policy', 'policy',
       'Standard shipping takes 3 to 5 business days in APAC. Expedited shipping is available for enterprise orders.'
UNION ALL
SELECT 'DOC-003', 'Sales Metric Definition', 'analytics',
       'Monthly sales refers to total invoiced order amount grouped by order_date month and region.';
