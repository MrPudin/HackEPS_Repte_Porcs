"""
metrics.py
==========

Pequeña librería de KPIs para analizar los resultados de la simulación.

Todos los métodos funcionan con un `pd.DataFrame` de eventos
como el que devuelve `Simulator.run()`.
"""

from __future__ import annotations

from typing import Dict, Any

import pandas as pd


def _parse_capacity_pct(series: pd.Series) -> float:
    """
    Convierte una serie de strings tipo '83.2%' a un promedio float (0-100).
    Si la columna no existe o está vacía, devuelve 0.0.
    """
    if series is None or series.empty:
        return 0.0

    def to_float(x):
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        s = str(x).strip()
        if s.endswith("%"):
            s = s[:-1]
        try:
            return float(s)
        except ValueError:
            return None

    vals = series.map(to_float)
    vals = vals.dropna()
    if vals.empty:
        return 0.0
    return float(vals.mean())


def compute_global_kpis(events: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula algunos indicadores básicos a partir del log de rutas.

    Parameters
    ----------
    events : pd.DataFrame
        Debe contener al menos las columnas:
        - pigs_delivered
        - distance_km
        - transport_cost
        - revenue
        - penalty_applied
        - time_hours

    Returns
    -------
    dict
    """
    if events is None or events.empty:
        return {
            "total_pigs_delivered": 0,
            "total_distance_km": 0.0,
            "total_time_hours": 0.0,
            "total_transport_cost": 0.0,
            "total_revenue": 0.0,
            "total_penalty": 0.0,
            "net_profit": 0.0,
            "avg_weight_kg": 0.0,
            "num_routes": 0,
            "avg_pigs_per_route": 0.0,
            "avg_distance_per_route_km": 0.0,
            "avg_time_per_route_h": 0.0,
            "cost_per_kg": 0.0,
            "avg_capacity_utilization_pct": 0.0,
        }

    total_pigs = float(events["pigs_delivered"].sum())
    total_distance = float(events["distance_km"].sum())
    total_time = float(events["time_hours"].sum())
    total_cost = float(events.get("transport_cost", 0.0).sum())
    total_revenue = float(events.get("revenue", 0.0).sum())
    total_penalty = float(events.get("penalty_applied", 0.0).sum())
    num_routes = int(len(events))

    if "avg_weight_kg" in events.columns and total_pigs > 0:
        weighted_weight = (events["avg_weight_kg"] * events["pigs_delivered"]).sum()
        avg_weight = float(weighted_weight / total_pigs)
        total_kg = float((events["avg_weight_kg"] * events["pigs_delivered"]).sum())
    else:
        avg_weight = 0.0
        total_kg = 0.0

    net_profit = total_revenue - total_cost

    avg_pigs_per_route = float(total_pigs / num_routes) if num_routes > 0 else 0.0
    avg_distance_per_route = float(total_distance / num_routes) if num_routes > 0 else 0.0
    avg_time_per_route = float(total_time / num_routes) if num_routes > 0 else 0.0
    cost_per_kg = float(total_cost / total_kg) if total_kg > 0 else 0.0

    avg_capacity_utilization = 0.0
    if "capacity_utilized_pct" in events.columns:
        avg_capacity_utilization = _parse_capacity_pct(events["capacity_utilized_pct"])

    return {
        "total_pigs_delivered": total_pigs,
        "total_distance_km": total_distance,
        "total_time_hours": total_time,
        "total_transport_cost": total_cost,
        "total_revenue": total_revenue,
        "total_penalty": total_penalty,
        "net_profit": net_profit,
        "avg_weight_kg": avg_weight,
        "num_routes": num_routes,
        "avg_pigs_per_route": avg_pigs_per_route,
        "avg_distance_per_route_km": avg_distance_per_route,
        "avg_time_per_route_h": avg_time_per_route,
        "cost_per_kg": cost_per_kg,
        "avg_capacity_utilization_pct": avg_capacity_utilization,
    }


def compute_daily_kpis(events: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve KPIs agregados por día.
    """
    if events is None or events.empty:
        return pd.DataFrame()

    grouped = (
        events.groupby("day")
        .agg(
            pigs_delivered=("pigs_delivered", "sum"),
            distance_km=("distance_km", "sum"),
            time_hours=("time_hours", "sum"),
            transport_cost=("transport_cost", "sum"),
            revenue=("revenue", "sum"),
            penalty_applied=("penalty_applied", "sum"),
            routes=("route_id", "nunique"),
        )
        .reset_index()
    )

    grouped["net_profit"] = grouped["revenue"] - grouped["transport_cost"]
    grouped["avg_pigs_per_route"] = grouped["pigs_delivered"] / grouped["routes"].replace(0, pd.NA)
    grouped["avg_distance_per_route_km"] = grouped["distance_km"] / grouped["routes"].replace(0, pd.NA)
    grouped["avg_time_per_route_h"] = grouped["time_hours"] / grouped["routes"].replace(0, pd.NA)

    return grouped
