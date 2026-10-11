# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Scheduled Batch Inference
# MAGIC
# MAGIC This is the notebook you'd actually put on a Databricks **Job** schedule (e.g. nightly)
# MAGIC once new telemetry lands in `gold_vehicle_features`. It loads the registered model instead
# MAGIC of retraining, scores the current fleet, and refreshes the table the dashboard reads from.
# MAGIC In a real deployment, notebook 00 (data generation) wouldn't exist — this would run right
# MAGIC after your real ingestion pipeline updates `gold_vehicle_features`.

# COMMAND ----------

# MAGIC %pip install mlflow xgboost --quiet
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

CATALOG = "main"
SCHEMA = "ev_fleet"
MODEL_NAME = f"{CATALOG}.{SCHEMA}.battery_soh_expected_degradation"

import mlflow

mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------

# MAGIC %md ### Load latest registered model version (Unity Catalog Model Registry)

# COMMAND ----------

client = mlflow.MlflowClient()
latest_version = max(
    int(v.version) for v in client.search_model_versions(f"name='{MODEL_NAME}'")
)
model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{latest_version}")
print(f"Loaded {MODEL_NAME} version {latest_version}")

# COMMAND ----------

feature_cols = [
    "days_in_service",
    "avg_battery_temp_c",
    "max_battery_temp_c",
    "avg_depth_of_discharge",
    "fast_charge_rate",
    "odometer_miles",
]

features_df = spark.table(f"{CATALOG}.{SCHEMA}.gold_vehicle_features").toPandas()
features_df["expected_degradation_pct"] = model.predict(features_df[feature_cols])
features_df["residual"] = features_df["soh_degradation_pct"] - features_df["expected_degradation_pct"]

# Recompute the adaptive threshold against the current fleet, not a value baked in at training time
threshold = features_df["residual"].quantile(0.95)
features_df["anomaly_flag"] = features_df["residual"] > threshold

print(f"Scored {len(features_df)} vehicles | {features_df['anomaly_flag'].sum()} flagged "
      f"at current 95th-pct threshold of {threshold:.4f}")

# COMMAND ----------

scored_spark = spark.createDataFrame(
    features_df[
        [
            "vehicle_id", "model", "region", "current_soh_pct", "soh_degradation_pct",
            "expected_degradation_pct", "residual", "anomaly_flag", "is_known_bad_batch",
        ]
    ]
)
scored_spark.write.mode("overwrite").format("delta").saveAsTable(
    f"{CATALOG}.{SCHEMA}.gold_battery_health_scored"
)
print("gold_battery_health_scored refreshed.")
