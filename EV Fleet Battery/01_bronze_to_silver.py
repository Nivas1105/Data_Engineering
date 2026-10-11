# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze -> Silver: Clean & Standardize Vehicle Telemetry
# MAGIC
# MAGIC Typical silver-layer responsibilities: dedupe, enforce types/ranges, flag bad readings,
# MAGIC and add derived columns downstream consumers shouldn't have to recompute themselves.

# COMMAND ----------

CATALOG = "main"
SCHEMA = "ev_fleet"
spark.sql(f"USE {CATALOG}.{SCHEMA}")

from pyspark.sql import functions as F

bronze = spark.table(f"{CATALOG}.{SCHEMA}.bronze_vehicle_telemetry")

# COMMAND ----------

# MAGIC %md ### Data quality checks — log what silver rejects instead of silently dropping it

# COMMAND ----------

before_count = bronze.count()

silver = (
    bronze.dropDuplicates(["vehicle_id", "date"])
    .filter(F.col("state_of_health_pct").between(0, 100))
    .filter(F.col("soc_end_pct").between(0, 100))
    .filter(F.col("odometer_miles") >= 0)
    .withColumn(
        "battery_stress_flag",
        F.when(F.col("battery_temp_c") > 45, "HIGH_TEMP")
        .when(F.col("depth_of_discharge") > 0.85, "DEEP_DISCHARGE")
        .when(F.col("fault_code").isNotNull(), "FAULT_LOGGED")
        .otherwise("NORMAL"),
    )
    .withColumn("year_month", F.date_format("date", "yyyy-MM"))
)

after_count = silver.count()
print(f"Bronze rows: {before_count:,} | Silver rows: {after_count:,} | "
      f"Rejected: {before_count - after_count:,}")

# COMMAND ----------

silver.write.mode("overwrite").format("delta").saveAsTable(
    f"{CATALOG}.{SCHEMA}.silver_vehicle_telemetry"
)

display(spark.table(f"{CATALOG}.{SCHEMA}.silver_vehicle_telemetry").limit(10))
