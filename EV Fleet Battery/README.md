# EV Fleet Battery Health Analytics — Databricks Lakehouse Project

A portfolio project modeling how a connected-vehicle company (Rivian-style) would use
Databricks end-to-end: medallion pipeline → ML → dashboard, all inside one lakehouse.

## Why this shape (how companies like Rivian actually use Databricks)

- **Ingestion & pipelines**: connected vehicles stream telemetry continuously; it lands in a
  Bronze Delta table via Auto Loader / Kafka + structured streaming in production. Here it's
  simulated as a batch load (notebook 00) so you can run the whole thing without a streaming
  source, but the Bronze → Silver → Gold shape is exactly what a real Lakeflow Declarative
  Pipeline (formerly Delta Live Tables) would do.
- **Unity Catalog**: one governed catalog/schema (`main.ev_fleet`) instead of ad-hoc tables —
  this is how a real fleet-data platform enforces access control (e.g. "regional ops teams see
  only their region") and lineage across ingestion → ML → BI.
- **ML on the lakehouse, not a separate ML stack**: the model trains directly off Gold Delta
  tables, tracks with MLflow, and registers into the Unity Catalog Model Registry — no export
  to a separate feature store or notebook-only experiment.
- **Batch inference as a scheduled Job**: notebook 04 is what you'd point a Databricks Job
  schedule at nightly, separate from training, which normally reruns weekly/monthly at most.
- **Dashboards read Gold tables directly**: Databricks SQL / Lakeview dashboards query the same
  governed tables the ML pipeline writes to — one platform, not a BI tool bolted onto an export.

## Project structure

```
00_generate_synthetic_data.py   # Bronze: synthetic fleet telemetry (stand-in for real ingestion)
01_bronze_to_silver.py          # Silver: cleaning, dedup, data-quality flags
02_silver_to_gold.py            # Gold: fleet KPIs + vehicle-level ML features
03_ml_battery_health.py         # Train + register the degradation model (run once / on retrain)
04_batch_inference_job.py       # Score the fleet with the registered model (run on a schedule)
dashboard_queries.sql           # Queries to wire into a Lakeview dashboard
```

## How to run (Databricks Free Edition — no cost, no credit card)

1. **Sign up**: go to the Databricks Free Edition signup page (search "Databricks Free Edition"
   or go to databricks.com/learn/free-edition) and create a workspace with a personal email.
   Free Edition replaced the old Community Edition and is serverless-only — no cluster config
   needed, which is actually simpler for this project.

2. **Import the notebooks**: in the workspace sidebar, **Workspace → your folder → Import**,
   choose **File**, and upload each `.py` file. Databricks auto-detects the `# Databricks
   notebook source` header and renders them as notebooks with proper cells (the `# COMMAND
   ----------` markers become cell breaks, `# MAGIC %md` becomes markdown cells).

3. **Run in order**, top to bottom, using the notebook's own "Run All":
   - `00_generate_synthetic_data.py` — creates the catalog/schema and Bronze table (~1-2 min)
   - `01_bronze_to_silver.py`
   - `02_silver_to_gold.py`
   - `03_ml_battery_health.py` — installs xgboost/mlflow, trains, registers the model
     (first run takes longer due to the `%pip install` + Python restart)
   - `04_batch_inference_job.py` — optional to run manually now; this is the one you'd
     actually schedule

   Free Edition is serverless, so there's no cluster to start — each notebook just attaches to
   serverless compute automatically. If you hit a daily usage quota, your compute pauses until
   it resets; your tables and model aren't affected.

4. **Check your catalog** if `main` doesn't already exist in your workspace: run `SHOW CATALOGS`
   in a SQL cell first, and swap the `CATALOG` variable at the top of each notebook to match.

5. **Build the dashboard**:
   - Go to **SQL Editor**, paste each query block from `dashboard_queries.sql` one at a time to
     confirm it returns rows.
   - Go to **Dashboards → Create Dashboard**, add each query as a dataset, and add a matching
     visual (line chart for Tiles 1–2, counters for Tile 3, scatter for Tile 4, table for Tile 5,
     bar chart for Tile 6).
   - Optional: Free Edition includes **Genie**, which lets you ask the dashboard questions in
     natural language against these same Gold tables instead of only prebuilt tiles — worth
     demoing if you want to show you know the newer Databricks AI/BI surface, not just classic
     dashboards.

6. **(Optional) Schedule it**: **Workflows → Jobs → Create Job**, add `04_batch_inference_job.py`
   as a task, set a nightly schedule. This is the piece that makes it "production," not a
   one-off notebook run — worth mentioning explicitly if you talk about this project in an
   interview.

## The story to tell about this project

The interesting part isn't "I built a pipeline" — it's the ML framing in notebook 03: instead of
training directly on a "defective battery" label (which wouldn't exist yet in a real fleet), the
model predicts *expected* degradation from usage alone, and flags vehicles whose actual
degradation is anomalously higher than expected. That's a residual/anomaly-detection approach,
not a straight classifier — the same instinct behind your incident-detection project's move from
a fixed threshold to a 95th-percentile adaptive cutoff.
