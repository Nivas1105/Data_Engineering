
CATALOG = "main"
SCHEMA = "ev_fleet"

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE {CATALOG}.{SCHEMA}")


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

bad_batch = rng.random(N_VEHICLES) < 0.04
delivery_offset_days = rng.integers(0, 120, N_VEHICLES) 


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
                "is_known_bad_batch": bool(bad_batch[v]), 
            }
        )

pdf = pd.DataFrame(records)
print(f"Generated {len(pdf):,} rows across {N_VEHICLES} vehicles")
pdf.head()


df = spark.createDataFrame(pdf)
df.write.mode("overwrite").format("delta").saveAsTable(
    f"{CATALOG}.{SCHEMA}.bronze_vehicle_telemetry"
)

display(spark.table(f"{CATALOG}.{SCHEMA}.bronze_vehicle_telemetry").limit(10))