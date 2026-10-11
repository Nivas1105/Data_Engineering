# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Generate Synthetic EV Fleet Telemetry
# MAGIC
# MAGIC Simulates the kind of daily-rollup telemetry an EV manufacturer's connected-vehicle
# MAGIC platform would land in a lakehouse: one row per vehicle per day, covering battery
# MAGIC state of charge, charging behavior, thermal exposure, and odometer.
# MAGIC
# MAGIC A small subset of vehicles (~4%) are seeded with a "bad battery batch" — accelerated
# MAGIC State-of-Health (SoH) degradation — so the ML notebook later has a real anomaly to find,
# MAGIC not just noise.
# MAGIC
# MAGIC Output: `main.ev_fleet.bronze_vehicle_telemetry` (Delta table, Unity Catalog)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Config — adjust catalog/schema if yours differ.
# MAGIC Free Edition workspaces come with a default catalog; run `SHOW CATALOGS` if `main` doesn't exist.

# COMMAND ----------

CATALOG = "main"
SCHEMA = "ev_fleet"

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE {CATALOG}.{SCHEMA}")

# COMMAND ----------

import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(7)

N_VEHICLES = 500
N_DAYS = 365
START_DATE = date(2025, 1, 1)

models = rng.choice(["R1T", "R1S", "R2"], N_VEHICLES, p=[0.45, 0.40, 0.15])
vehicle_ids = [f"RVN-{10000+i}" for i in range(N_VEHICLES)]
regions = rng.choice(
    ["Southwest", "Pacific NW", "Northeast", "Midwest", "Southeast"], N_VEHICLES
)
# ~4% of the fleet has a manufacturing-defect battery batch -> accelerated degradation
bad_batch = rng.random(N_VEHICLES) < 0.04
delivery_offset_days = rng.integers(0, 120, N_VEHICLES)  # staggered fleet delivery

# COMMAND ----------

# MAGIC %md ### Simulate daily telemetry per vehicle
# MAGIC State of Health (SoH) decays daily as a function of: fast-charge frequency,
# MAGIC thermal exposure (ambient + battery temp), and depth-of-discharge (DoD).
# MAGIC Bad-batch vehicles degrade 3-6x faster — the pattern the ML model should learn to flag.

# COMMAND ----------

records = []
soh = np.full(N_VEHICLES, 100.0)
odometer = np.zeros(N_VEHICLES)

for day_offset in range(N_DAYS):
    current_date = START_DATE + timedelta(days=day_offset)
    for v in range(N_VEHICLES):
        if day_offset < delivery_offset_days[v]:
            continue  # not yet delivered to customer

        ambient_temp_c = rng.normal(22, 12) + (5 if regions[v] == "Southwest" else 0)
        miles_today = max(0, rng.normal(35, 20))
        odometer[v] += miles_today

        fast_charge_today = rng.random() < (0.35 if miles_today > 60 else 0.12)
        dod = np.clip(rng.normal(0.5, 0.18), 0.05, 0.98)
        battery_temp_c = ambient_temp_c + rng.normal(8 if fast_charge_today else 3, 4)
        pack_voltage = rng.normal(400, 6)
        soc_end_pct = np.clip(rng.normal(55, 20), 3, 100)

        base_degrade = (
            0.0025
            + 0.006 * fast_charge_today
            + max(0, battery_temp_c - 35) * 0.0009
            + max(0, dod - 0.7) * 0.01
        )
        if bad_batch[v]:
            base_degrade *= rng.uniform(3.0, 6.0)
        soh[v] = max(60.0, soh[v] - base_degrade)

        # occasional fault code, more likely as SoH drops or on bad-batch vehicles
        fault_prob = 0.01 + (0.15 if soh[v] < 85 else 0) + (0.05 if bad_batch[v] else 0)
        fault_code = None
        if rng.random() < fault_prob:
            fault_code = rng.choice(
                ["THERMAL_WARN", "CELL_IMBALANCE", "CHARGE_FAULT", "BMS_COMM_ERR"]
            )

        records.append(
            {
                "vehicle_id": vehicle_ids[v],
                "model": models[v],
                "region": regions[v],
                "date": current_date,
                "miles_driven": round(miles_today, 1),
                "odometer_miles": round(odometer[v], 1),
                "ambient_temp_c": round(ambient_temp_c, 1),
                "battery_temp_c": round(battery_temp_c, 1),
                "pack_voltage_v": round(pack_voltage, 1),
                "soc_end_pct": round(soc_end_pct, 1),
                "depth_of_discharge": round(dod, 3),
                "fast_charge_event": bool(fast_charge_today),
                "state_of_health_pct": round(soh[v], 3),
                "fault_code": fault_code,
                "is_known_bad_batch": bool(bad_batch[v]),  # ground truth, drop before training
            }
        )

pdf = pd.DataFrame(records)
print(f"Generated {len(pdf):,} rows across {N_VEHICLES} vehicles")
pdf.head()

# COMMAND ----------

# MAGIC %md ### Write to Bronze Delta table

# COMMAND ----------

df = spark.createDataFrame(pdf)
df.write.mode("overwrite").format("delta").saveAsTable(
    f"{CATALOG}.{SCHEMA}.bronze_vehicle_telemetry"
)

display(spark.table(f"{CATALOG}.{SCHEMA}.bronze_vehicle_telemetry").limit(10))