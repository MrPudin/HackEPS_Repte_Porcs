"""
Optimizer
=========

Espacio para jugar con heurísticas de optimización encima del simulador.

Lo que hay aquí es un esqueleto sencillo que hace una búsqueda de rejilla
sobre el peso mínimo de sacrificio y se queda con el mejor resultado
según beneficio neto.
"""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd

from src.simulation.Simulator import Simulator
from src.utils.metrics import compute_global_kpis


class Optimizer:
    """
    Minimísima envoltura alrededor de `Simulator` para explorar parámetros.
    """

    def __init__(self, base_simulator: Simulator):
        self.base_simulator = base_simulator

    def search_best_min_weight(
        self, candidates_kg: List[float], days: int = 7
    ) -> Tuple[float, pd.DataFrame, dict]:
        """
        Prueba varios valores del peso mínimo de sacrificio y devuelve
        el que da mejor beneficio neto.

        Returns
        -------
        (best_weight, events_df, kpis_dict)
        """
        best_weight = None
        best_profit = float("-inf")
        best_events = pd.DataFrame()
        best_kpis = {}

        for w in candidates_kg:
            sim = Simulator(
                farms=self.base_simulator.farms,
                slaughterhouses=self.base_simulator.slaughterhouses,
                transports=self.base_simulator.transports,
                biological_manager=self.base_simulator.bio,
                speed_kmh=self.base_simulator.router.speed_kmh,
                min_market_weight_kg=w,
            )

            events = sim.run(days=days)
            kpis = compute_global_kpis(events)

            if kpis["net_profit"] > best_profit:
                best_profit = kpis["net_profit"]
                best_weight = w
                best_events = events
                best_kpis = kpis

        return best_weight, best_events, best_kpis
