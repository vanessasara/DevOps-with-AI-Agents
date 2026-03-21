# Level 3 — Multi-Source Integration

**Folder:** `03-multi-source/`
**Status:** Coming later
**Builds on:** Level 2 (Next.js + FastAPI)

---

## What This Level Will Add

Level 3 connects the agent to real, live log sources instead of local files.

- **Elasticsearch** — application logs
- **Kubernetes** — container and pod logs
- **CloudWatch** — AWS system metrics and logs
- **RDS** — database logs

The agent gains the ability to query multiple sources in a single run and correlate events across them. Instead of "service crashed", it produces "service crashed after DB connection pool exhausted, caused by a deploy that changed timeout from 30s to 5s."

---

## New Tools That Will Be Added

- `query_elasticsearch(index, query, time_range)`
- `query_cloudwatch(log_group, filter_pattern, start_time, end_time)`
- `get_kubernetes_logs(namespace, pod_name, tail_lines)`
- `query_rds_logs(instance_id, time_range)`

Each tool is a `@function_tool` decorated function — same pattern as Level 0. The agent decides which ones to call based on the question.

---

## What Changes vs Level 2

- New tools in `src/tools/` for each log source
- New environment variables for API credentials
- FastAPI gains a `/analyse` endpoint that returns structured JSON (severity, affected service, recommended action) in addition to `/chat`
- Frontend gains an incident card component that renders structured analysis results differently from plain chat messages

The `src/agents/log_analyzer.py` and `main.py` require minimal changes — just new tools added to the list.

---

## Why Runs Get Longer Here

A single question like "Why did the payment service fail last night?" might trigger:

1. Query Elasticsearch for app errors in the time window
2. Query CloudWatch for system metrics around the same time
3. Query RDS logs for database errors
4. Correlate findings across all three sources
5. Save a structured summary

This can take 30–60 seconds. This is where background task handling becomes relevant — the frontend needs to handle long-running requests gracefully.

---

## This Folder Will Contain

```
03-multi-source/
├── backend/
│   ├── src/
│   │   ├── config.py          ← updated with new credentials
│   │   └── tools/
│   │       ├── log_tools.py   ← existing local tools
│   │       ├── elastic.py     ← new
│   │       ├── cloudwatch.py  ← new
│   │       ├── kubernetes.py  ← new
│   │       └── rds.py         ← new
│   └── main.py                ← gains /analyse endpoint
└── frontend/
    └── components/
        └── chat/
            └── incident-card.tsx  ← new structured result component
```

---

## Prerequisites Before Starting Level 3

- Level 2 must be fully working and tested
- Access to at least one real log source (Elasticsearch or CloudWatch)
- API credentials for that source
- Understanding of the query syntax for your chosen source
