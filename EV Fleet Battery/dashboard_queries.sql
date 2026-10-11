-- Databricks SQL / Lakeview dashboard queries
-- Build each of these as a separate dataset in the dashboard, then add matching visuals.
-- Run these in the SQL Editor first to confirm they return rows, then wire each into a
-- Lakeview dashboard tile (Dashboards -> Create Dashboard -> Add data -> paste query).

USE main.ev_fleet;

-- ============================================================
-- Tile 1: Fleet-wide average State of Health over time (line chart)
-- X: date, Y: avg_soh_pct, Series: model
-- ============================================================
SELECT
    date,
    model,
    ROUND(AVG(avg_soh_pct), 2) AS avg_soh_pct
FROM gold_fleet_daily_kpi
GROUP BY date, model
ORDER BY date;

-- ============================================================
-- Tile 2: Fault rate trend (line/area chart)
-- X: date, Y: fault_rate_pct, Series: region
-- ============================================================
SELECT
    date,
    region,
    SUM(fault_count) AS fault_count,
    SUM(active_vehicles) AS active_vehicles,
    ROUND(100.0 * SUM(fault_count) / SUM(active_vehicles), 2) AS fault_rate_pct
FROM gold_fleet_daily_kpi
GROUP BY date, region
ORDER BY date;

-- ============================================================
-- Tile 3: Current fleet KPI summary (counter/scorecard tiles)
-- ============================================================
SELECT
    COUNT(*) AS total_vehicles,
    ROUND(AVG(current_soh_pct), 2) AS fleet_avg_soh_pct,
    SUM(CASE WHEN anomaly_flag THEN 1 ELSE 0 END) AS flagged_vehicles,
    ROUND(100.0 * SUM(CASE WHEN anomaly_flag THEN 1 ELSE 0 END) / COUNT(*), 2) AS flagged_pct
FROM gold_battery_health_scored;

-- ============================================================
-- Tile 4: Anomaly detection scatter (residual vs. mileage)
-- X: odometer via join back to gold_vehicle_features, Y: residual, Color: anomaly_flag
-- ============================================================
SELECT
    s.vehicle_id,
    s.model,
    s.region,
    f.odometer_miles,
    s.soh_degradation_pct,
    s.expected_degradation_pct,
    s.residual,
    s.anomaly_flag
FROM gold_battery_health_scored s
JOIN gold_vehicle_features f USING (vehicle_id)
ORDER BY s.residual DESC;

-- ============================================================
-- Tile 5: Top flagged vehicles table (for a fleet ops action list)
-- ============================================================
SELECT
    vehicle_id,
    model,
    region,
    ROUND(current_soh_pct, 1) AS current_soh_pct,
    ROUND(residual, 3) AS residual_pct_pts,
    is_known_bad_batch  -- keep visible while validating; drop this column once trusted in prod
FROM gold_battery_health_scored
WHERE anomaly_flag = true
ORDER BY residual DESC
LIMIT 25;

-- ============================================================
-- Tile 6: SoH by region (bar chart) — spot geographic/climate effects
-- ============================================================
SELECT
    region,
    ROUND(AVG(current_soh_pct), 2) AS avg_soh_pct,
    COUNT(*) AS vehicle_count
FROM gold_battery_health_scored
GROUP BY region
ORDER BY avg_soh_pct;
