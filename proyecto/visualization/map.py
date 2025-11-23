"""
map.py
======

Mapa sencillo de granjas y escorxadors usando Plotly.

- plot_infrastructure_map: solo puntos.
- plot_routes_for_day: puntos + líneas de rutas para un día concreto.
"""

from __future__ import annotations

from typing import List
import ast

import pandas as pd
import plotly.express as px

from src.models.Farm import Farm
from src.models.Slaughterhouse import Slaughterhouse


def plot_infrastructure_map(farms: List[Farm], slaughterhouses: List[Slaughterhouse]):
    """
    Dibuja la localización de granjas y escorxadors en un mapa.

    En el contexto de los datos del reto, debería dibujar Cataluña.
    """
    if not farms and not slaughterhouses:
        print("No hay granjas ni escorxadors para mostrar.")
        return

    rows = []

    for f in farms:
        rows.append(
            {
                "name": f.name,
                "lat": f.lat,
                "lon": f.lon,
                "type": "Granja",
            }
        )

    for s in slaughterhouses:
        rows.append(
            {
                "name": s.name,
                "lat": s.lat,
                "lon": s.lon,
                "type": "Escorxador",
            }
        )

    df = pd.DataFrame(rows)

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="type",
        hover_name="name",
        title="Mapa de granjas y escorxadors",
    )
    fig.update_layout(legend_title_text="Tipo")
    fig.show()


def _parse_farms_visited(value):
    """Convierte el campo farms_visited de cada evento a lista de IDs."""
    if isinstance(value, list):
        return value
    if value is None:
        return []
    s = str(value)
    try:
        # Intentar parsear como lista Python: "['F1', 'F2']"
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    # Fallback: separar por coma
    return [x.strip() for x in s.split(",") if x.strip()]


def plot_routes_for_day(
    events: pd.DataFrame,
    farms: List[Farm],
    slaughterhouses: List[Slaughterhouse],
    day: int,
):
    """
    Dibuja las rutas ejecutadas en un día concreto.

    - Cada ruta se dibuja como una polilínea:
      escorxador -> granja1 -> granja2 -> ... -> escorxador
    - Colorea por route_id.
    """
    if events is None or events.empty:
        print("No hay eventos para mostrar.")
        return

    day_events = events[events["day"] == day]
    if day_events.empty:
        print(f"No hay rutas para el día {day}.")
        return

    farm_dict = {f.farm_id: f for f in farms}
    sh_dict = {s.slaughterhouse_id: s for s in slaughterhouses}

    rows = []

    for _, row in day_events.iterrows():
        route_id = row.get("route_id", f"day{day}_r{row.get('route_index', 0)}")
        sh_id = row["slaughterhouse_id"]
        sh = sh_dict.get(sh_id)
        if sh is None:
            continue

        farms_visited = _parse_farms_visited(row.get("farms_visited"))

        points = [("Escorxador", sh.lat, sh.lon, sh.name)]

        for farm_id in farms_visited:
            farm = farm_dict.get(farm_id)
            if farm is not None:
                points.append(("Granja", farm.lat, farm.lon, farm.name))

        points.append(("Escorxador", sh.lat, sh.lon, sh.name))

        for idx, (ptype, lat, lon, name) in enumerate(points):
            rows.append(
                {
                    "route_id": route_id,
                    "step": idx,
                    "type": ptype,
                    "lat": lat,
                    "lon": lon,
                    "name": name,
                }
            )

    if not rows:
        print(f"No se pudieron construir segmentos de ruta para el día {day}.")
        return

    df = pd.DataFrame(rows)

    fig = px.line_geo(
        df,
        lat="lat",
        lon="lon",
        color="route_id",
        line_group="route_id",
        hover_name="name",
        markers=True,
        title=f"Rutas ejecutadas - Día {day}",
    )
    fig.update_layout(legend_title_text="Ruta")
    fig.show()
