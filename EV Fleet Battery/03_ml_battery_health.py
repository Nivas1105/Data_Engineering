
CATALOG = "main"
SCHEMA = "ev_fleet"

import mlflow
import mlflow.xgboost
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

mlflow.set_registry_uri("databricks-uc")

features_df = spark.table(f"{CATALOG}.{SCHEMA}.gold_vehicle_features").toPandas()
print(f"Vehicles: {len(features_df)} | Known bad-batch: {features_df['is_known_bad_batch'].sum()}")
features_df.head()
feature_cols = [
    "days_in_service",
    "avg_battery_temp_c",
    "max_battery_temp_c",
    "avg_depth_of_discharge",
    "fast_charge_rate",
    "odometer_miles",
]
target_col = "soh_degradation_pct"

X = features_df[feature_cols]
y = features_df[target_col]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

mlflow.xgboost.autolog()

with mlflow.start_run(run_name="battery_soh_expected_degradation") as run:
    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    mlflow.log_metric("test_mae", mae)
    mlflow.log_metric("test_rmse", rmse)
    print(f"Test MAE: {mae:.4f} pct-points | Test RMSE: {rmse:.4f} pct-points")

    run_id = run.info.run_id


features_df["expected_degradation_pct"] = model.predict(X)
features_df["residual"] = features_df["soh_degradation_pct"] - features_df["expected_degradation_pct"]

threshold = features_df["residual"].quantile(0.95)
features_df["anomaly_flag"] = features_df["residual"] > threshold

flagged = features_df[features_df["anomaly_flag"]]
true_positives = flagged["is_known_bad_batch"].sum()
precision = true_positives / len(flagged) if len(flagged) else 0
recall = true_positives / features_df["is_known_bad_batch"].sum()

print(f"Residual threshold (95th pct): {threshold:.4f}")
print(f"Vehicles flagged: {len(flagged)} | Precision: {precision:.2%} | Recall: {recall:.2%}")

with mlflow.start_run(run_id=run_id):
    mlflow.log_metric("anomaly_threshold", threshold)
    mlflow.log_metric("flagged_count", len(flagged))
    mlflow.log_metric("validation_precision", precision)
    mlflow.log_metric("validation_recall", recall)


model_name = f"{CATALOG}.{SCHEMA}.battery_soh_expected_degradation"
model_uri = f"runs:/{run_id}/model"
registered = mlflow.register_model(model_uri=model_uri, name=model_name)
print(f"Registered {model_name} version {registered.version}")


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
display(scored_spark.orderBy(scored_spark.residual.desc()).limit(15))
