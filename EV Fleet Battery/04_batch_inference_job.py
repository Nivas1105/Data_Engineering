CATALOG = "main"
SCHEMA = "ev_fleet"
MODEL_NAME = f"{CATALOG}.{SCHEMA}.battery_soh_expected_degradation"

import mlflow

mlflow.set_registry_uri("databricks-uc")


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
