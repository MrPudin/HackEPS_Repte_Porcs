"""
Simulator
=========

Motor de simulación día a día.

Se apoya en:
- `Router` para decidir qué rutas se hacen
- Clases `Farm`, `Slaughterhouse`, `Transport` para actualizar estados
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

import pandas as pd

from src.models.Farm import Farm
from src.models.Slaughterhouse import Slaughterhouse
from src.models.Transport import Transport
from src.simulation.Router import Router, PlannedRoute, PlannedStop
from src.utils.BiologicalDataManager import BiologicalDataManager


class Simulator:
    """
    Orquesta la simulación de varios días.

    Uso típico:
    ----------
    simulator = Simulator(farms, slaughterhouses, transports, bio_manager)
    events_df = simulator.run(days=10)
    """

    def __init__(
        self,
        farms: List[Farm],
        slaughterhouses: List[Slaughterhouse],
        transports: List[Transport],
        biological_manager: Optional[BiologicalDataManager] = None,
        speed_kmh: float = 60.0,
        min_market_weight_kg: float = 105.0,
        max_stops_per_route: int = 3,
        max_hours_per_day: float = 8.0,
    ):
        self.farms = farms
        self.slaughterhouses = slaughterhouses
        self.transports = transports
        self.bio = biological_manager

        self.router = Router(
            farms=self.farms,
            slaughterhouses=self.slaughterhouses,
            transports=self.transports,
            speed_kmh=speed_kmh,
            min_market_weight_kg=min_market_weight_kg,
            max_stops_per_route=max_stops_per_route,
            max_hours_per_day=max_hours_per_day,
        )

        # Eventos detallados de la simulación
        self._events: List[Dict[str, Any]] = []

    # ---------- API pública ----------

    def run(self, days: int = 7) -> pd.DataFrame:
        """
        Ejecuta la simulación un número de días.

        Returns
        -------
        pd.DataFrame
            Un registro fila-a-fila de cada ruta ejecutada.
        """
        self._events.clear()

        for day in range(days):
            self._simulate_single_day(day)

        if not self._events:
            return pd.DataFrame()

        return pd.DataFrame(self._events)

    # ---------- lógica interna ----------

    def _simulate_single_day(self, day: int) -> None:
        """Simula un único día:
        - Se actualiza el crecimiento de los animales
        - Se planifican rutas
        - Se ejecutan las rutas
        """
        # 1) Actualizar peso y edad de los animales
        for farm in self.farms:
            farm.update_growth(days_passed=1)

        # 2) Pedir plan de rutas al Router
        planned_routes: List[PlannedRoute] = self.router.build_daily_plan(day)

        if not planned_routes:
            # No hay rutas este día
            return

        # 3) Ejecutar cada ruta
        for route_idx, planned in enumerate(planned_routes):
            self._execute_route(day, route_idx, planned)

        # 4) Reset diario de escorxadores (capacidad / acumulados)
        for sh in self.slaughterhouses:
            sh.reset_daily_counter()

    def _execute_route(self, day: int, route_index: int, planned: PlannedRoute) -> None:
        """
        Ejecuta físicamente una PlannedRoute:
        - Carga animales en el camión
        - Registra ruta en el propio transporte
        - Entrega en el escorxador
        """
        transport = planned.transport
        slaughterhouse = planned.slaughterhouse
        stops = planned.stops

        if not stops:
            return

        route_identifier = f"day{day}_r{route_index}"

        # Crear ruta en el transporte
        route_obj = transport.start_route(
            route_id=route_identifier,
            slaughterhouse_id=slaughterhouse.slaughterhouse_id,
        )

        total_pigs_loaded = 0
        total_weight_kg = 0.0
        farms_visited_ids: List[str] = []

        for stop in stops:
            isinstance(stop, PlannedStop)  # para IDEs

            farm = stop.farm
            pigs_requested = stop.pigs_to_pick

            current_weight = farm.get_current_weight()
            success = farm.deliver_pigs(pigs_requested, current_day=day)
            if not success:
                continue

            load_ok, pigs_loaded = transport.load_pigs(pigs_requested, current_weight)
            if not load_ok or pigs_loaded <= 0:
                # En teoría no debería pasar porque Router ya mira capacidad
                continue

            farms_visited_ids.append(farm.farm_id)
            total_pigs_loaded += pigs_loaded
            total_weight_kg += pigs_loaded * current_weight

        if total_pigs_loaded <= 0:
            # Nada se cargó realmente, limpiamos ruta
            transport.current_load_kg = 0.0
            transport.pigs_aboard = 0
            transport.current_route = None
            return

        avg_weight = total_weight_kg / total_pigs_loaded

        # Entregar en escorxador
        sh_ok, receipt_info = slaughterhouse.receive_pigs(
            pigs_count=total_pigs_loaded,
            avg_weight_kg=avg_weight,
        )
        if not sh_ok:
            return

        # Completar ruta en el camión (coste, tiempos, etc.)
        tr_ok, route_info = transport.complete_route(
            distance_km=planned.distance_km,
            time_hours=planned.time_hours,
        )
        if not tr_ok:
            return

        # Enriquecer receipt_info con info de contexto
        event: Dict[str, Any] = {
            "day": day,
            "route_index": route_index,
            "route_id": route_identifier,
            "transport_id": transport.transport_id,
            "transport_type": transport.type,
            "slaughterhouse_id": slaughterhouse.slaughterhouse_id,
            "slaughterhouse_name": slaughterhouse.name,
            "farms_visited": farms_visited_ids,
            "pigs_delivered": total_pigs_loaded,
            "avg_weight_kg": avg_weight,
            "distance_km": planned.distance_km,
            "time_hours": planned.time_hours,
            "transport_cost": route_info.get("cost", 0.0),
            "capacity_utilized_pct": route_info.get("capacity_utilized"),
            "revenue": receipt_info.get("revenue", 0.0),
            "penalty_applied": receipt_info.get("penalty_applied", 0.0),
        }

        self._events.append(event)

    # ---------- helpers ----------

    def get_events(self) -> pd.DataFrame:
        """Devuelve una copia del registro de eventos actual."""
        if not self._events:
            return pd.DataFrame()
        return pd.DataFrame(self._events)
