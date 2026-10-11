

CATALOG = "main"
SCHEMA = "ev_fleet"
spark.sql(f"USE {CATALOG}.{SCHEMA}")

from pyspark.sql import functions as F

silver = spark.table(f"{CATALOG}.{SCHEMA}.silver_vehicle_telemetry")


fleet_daily_kpi = (
    silver.groupBy("date", "model", "region")
    .agg(
        F.countDistinct("vehicle_id").alias("active_vehicles"),
        F.avg("state_of_health_pct").alias("avg_soh_pct"),
        F.avg("battery_temp_c").alias("avg_battery_temp_c"),
        F.sum(F.col("fast_charge_event").cast("int")).alias("fast_charge_events"),
        F.sum(F.when(F.col("fault_code").isNotNull(), 1).otherwise(0)).alias("fault_count"),
        F.avg("miles_driven").alias("avg_miles_driven"),
    )
    .withColumn("fault_rate_pct", F.round(100 * F.col("fault_count") / F.col("active_vehicles"), 2))
)

fleet_daily_kpi.write.mode("overwrite").format("delta").saveAsTable(
    f"{CATALOG}.{SCHEMA}.gold_fleet_daily_kpi"
)
display(fleet_daily_kpi.orderBy(F.desc("date")).limit(10))

vehicle_features = (
    silver.groupBy("vehicle_id", "model", "region")
    .agg(
        F.count("*").alias("days_in_service"),
        F.avg("battery_temp_c").alias("avg_battery_temp_c"),
        F.max("battery_temp_c").alias("max_battery_temp_c"),
        F.avg("depth_of_discharge").alias("avg_depth_of_discharge"),
        (F.sum(F.col("fast_charge_event").cast("int")) / F.count("*")).alias("fast_charge_rate"),
        F.sum(F.when(F.col("fault_code").isNotNull(), 1).otherwise(0)).alias("total_fault_events"),
        F.max("odometer_miles").alias("odometer_miles"),
        F.min("state_of_health_pct").alias("current_soh_pct"),  # SoH only decreases -> min = latest
        F.max("is_known_bad_batch").alias("is_known_bad_batch"),  # ground truth for evaluation only
    )
    .withColumn("soh_degradation_pct", F.round(100 - F.col("current_soh_pct"), 3))
    .withColumn("degradation_per_1k_miles",
                F.round(F.col("soh_degradation_pct") / (F.col("odometer_miles") / 1000 + 0.01), 4))
)

vehicle_features.write.mode("overwrite").format("delta").saveAsTable(
    f"{CATALOG}.{SCHEMA}.gold_vehicle_features"
)
display(vehicle_features.orderBy(F.desc("soh_degradation_pct")).limit(15))