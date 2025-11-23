"""
dashboard.py
============

Funciones de visualización rápida usando Plotly.

Incluye:
- Porcos entregados por día
- Beneficio por día
- Coste medio por ruta
- Pigs por ruta
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px


def plot_daily_pigs(events: pd.DataFrame):
    """Bar chart de porcos entregados por día."""
    if events is None or events.empty:
        print("No hay eventos para mostrar.")
        return

    daily = (
        events.groupby("day")["pigs_delivered"]
        .sum()
        .reset_index()
        .rename(columns={"pigs_delivered": "pigs"})
    )

    fig = px.bar(
        daily,
        x="day",
        y="pigs",
        title="Porcos entregados por día",
        labels={"day": "Día", "pigs": "Porcos entregados"},
    )
    fig.show()


def plot_daily_profit(events: pd.DataFrame):
    """Beneficio neto por día."""
    if events is None or events.empty:
        print("No hay eventos para mostrar.")
        return

    if "revenue" not in events.columns or "transport_cost" not in events.columns:
        print("Faltan columnas 'revenue' o 'transport_cost' en los eventos.")
        return

    daily = (
        events.groupby("day")
        .agg(revenue=("revenue", "sum"), transport_cost=("transport_cost", "sum"))
        .reset_index()
    )
    daily["net_profit"] = daily["revenue"] - daily["transport_cost"]

    fig = px.bar(
        daily,
        x="day",
        y="net_profit",
        title="Beneficio neto por día",
        labels={"day": "Día", "net_profit": "Beneficio neto (€)"},
    )
    fig.show()


def plot_avg_pigs_per_route(events: pd.DataFrame):
    """Pigs medios por ruta, por día."""
    if events is None or events.empty:
        print("No hay eventos para mostrar.")
        return

    daily = (
        events.groupby("day")
        .agg(
            pigs_delivered=("pigs_delivered", "sum"),
            routes=("route_id", "nunique"),
        )
        .reset_index()
    )
    daily["avg_pigs_per_route"] = daily["pigs_delivered"] / daily["routes"].replace(0, pd.NA)

    fig = px.line(
        daily,
        x="day",
        y="avg_pigs_per_route",
        markers=True,
        title="Porcos medios por ruta y día",
        labels={"day": "Día", "avg_pigs_per_route": "Porcos / ruta"},
    )
    fig.show()


def plot_avg_distance_per_route(events: pd.DataFrame):
    """Distancia media por ruta y día."""
    if events is None or events.empty:
        print("No hay eventos para mostrar.")
        return

    daily = (
        events.groupby("day")
        .agg(
            distance_km=("distance_km", "sum"),
            routes=("route_id", "nunique"),
        )
        .reset_index()
    )
    daily["avg_distance_per_route_km"] = daily["distance_km"] / daily["routes"].replace(0, pd.NA)

    fig = px.line(
        daily,
        x="day",
        y="avg_distance_per_route_km",
        markers=True,
        title="Distancia media por ruta y día",
        labels={"day": "Día", "avg_distance_per_route_km": "km / ruta"},
    )
    fig.show()
