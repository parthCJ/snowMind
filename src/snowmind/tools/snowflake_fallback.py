from __future__ import annotations

from typing import Any

import snowflake.connector

from snowmind.config import settings


def _has_credentials() -> bool:
    return bool(settings.account and settings.user and settings.password)


def _connect():
    return snowflake.connector.connect(
        account=settings.account,
        user=settings.user,
        password=settings.password,
        role=settings.role,
        warehouse=settings.warehouse,
        database=settings.database,
        schema=settings.schema,
    )


def analyst_fallback(question: str) -> str:
    if not _has_credentials():
        return "Snowflake fallback unavailable: set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD in .env."

    q = question.lower()
    if "sales" in q and "region" in q:
        sql = (
            "SELECT region, ROUND(SUM(amount), 2) AS total_sales "
            "FROM SNOWMIND_DB.SALES.ORDERS "
            "GROUP BY region ORDER BY total_sales DESC"
        )
    elif "sales" in q and ("total" in q or "overall" in q):
        sql = (
            "SELECT ROUND(SUM(amount), 2) AS total_sales FROM SNOWMIND_DB.SALES.ORDERS"
        )
    elif "users" in q or "profiles" in q:
        sql = "SELECT country, COUNT(*) AS users FROM SNOWMIND_DB.USERS.PROFILES GROUP BY country ORDER BY users DESC"
    else:
        sql = "SELECT COUNT(*) AS orders FROM SNOWMIND_DB.SALES.ORDERS"

    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description] if cur.description else []
    except Exception as exc:
        return f"Snowflake fallback query failed: {exc}"

    if not rows:
        return "No rows returned from fallback SQL."

    lines = ["Fallback SQL result:"]
    for row in rows:
        if cols:
            parts = [f"{cols[i]}={row[i]}" for i in range(len(cols))]
            lines.append("- " + ", ".join(parts))
        else:
            lines.append("- " + ", ".join(str(v) for v in row))
    return "\n".join(lines)


def search_fallback(query: str, top_k: int = 3) -> str:
    if not _has_credentials():
        return "Knowledge fallback unavailable: set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD in .env."

    sql = (
        "SELECT doc_id, title, category, content "
        "FROM SNOWMIND_DB.CORTEX.KNOWLEDGE_BASE"
    )

    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
    except Exception as exc:
        return f"Knowledge fallback query failed: {exc}"

    if not rows:
        return "No relevant documents found in fallback knowledge base."

    tokens = [t.strip(" ,.!?;:\"'()[]{}").lower() for t in query.split()]
    tokens = [t for t in tokens if len(t) >= 4]
    if not tokens:
        tokens = ["policy"]

    scored_rows = []
    for row in rows:
        doc_id, title, category, content = row
        text = f"{title} {category} {content}".lower()
        score = sum(1 for token in tokens if token in text)
        if score > 0:
            scored_rows.append((score, row))

    if not scored_rows:
        return "No relevant documents found in fallback knowledge base."

    scored_rows.sort(key=lambda x: x[0], reverse=True)
    top_rows = [r for _, r in scored_rows[:top_k]]

    lines = ["Fallback knowledge results:"]
    for doc_id, title, category, content in top_rows:
        snippet = (content[:180] + "...") if len(content) > 180 else content
        lines.append(f"- {doc_id} | {title} | {category}: {snippet}")
    return "\n".join(lines)
