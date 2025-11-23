"""
Router
======

Construye rutas diarias:
- selecciona granjas candidatas
- asigna hasta 3 granjas por camión
- respeta capacidad de camión y escorxador
- respeta límite de horas por día y 1 visita/granja/semana
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

import math

from src.models.Farm import Farm
from src.models.Slaughterhouse import Slaughterhouse
from src.models.Transport import Transport


@dataclass
class PlannedStop:
    """Parada planificada de un camión en una granja concreta."""
    farm: Farm
    pigs_to_pick: int


@dataclass
class PlannedRoute:
    """
    Ruta planificada para un camión en un día concreto.
    Un camión puede visitar hasta `max_stops_per_route` granjas.
    """
    day: int
    transport: Transport
    slaughterhouse: Slaughterhouse
    stops: List[PlannedStop]
    distance_km: float
    time_hours: float


class Router:
    """
    Construye un plan de rutas día a día.

    No modifica el estado de granjas / escorxadores / camiones.
    Solo devuelve un plan; la ejecución real la hace `Simulator`.
    """

    def __init__(
        self,
        farms: List[Farm],
        slaughterhouses: List[Slaughterhouse],
        transports: List[Transport],
        speed_kmh: float = 60.0,
        min_market_weight_kg: float = 105.0,
        max_stops_per_route: int = 3,
        max_hours_per_day: float = 8.0,
    ):
        self.farms = farms
        self.slaughterhouses = slaughterhouses
        self.transports = transports
        self.speed_kmh = speed_kmh
        self.min_market_weight_kg = min_market_weight_kg
        self.max_stops_per_route = max_stops_per_route
        self.max_hours_per_day = max_hours_per_day


    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Distancia en km entre dos puntos GPS."""
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(
            dlambda / 2
        ) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    def _route_distance_km(self, slaughterhouse: Slaughterhouse, farms_path: List[Farm]) -> float:
        """
        Distancia total de una ruta:
        escorxador -> granja1 -> ... -> granjaN -> escorxador
        """
        if not farms_path:
            return 0.0

        sh_lat, sh_lon = slaughterhouse.lat, slaughterhouse.lon
        distance = 0.0

        first = farms_path[0]
        distance += self._haversine_km(sh_lat, sh_lon, first.lat, first.lon)

        for f_prev, f_next in zip(farms_path[:-1], farms_path[1:]):
            distance += self._haversine_km(f_prev.lat, f_prev.lon, f_next.lat, f_next.lon)

        last = farms_path[-1]
        distance += self._haversine_km(last.lat, last.lon, sh_lat, sh_lon)

        return distance


    def _select_candidate_farms(self, current_day: int) -> List[Farm]:
        """
        Devuelve las granjas que pueden entregar hoy y cuyo peso está
        razonablemente cerca de peso de sacrificio.
        """
        candidates: List[Farm] = []
        for farm in self.farms:
            if farm.inventory_pigs <= 0:
                continue
            if not farm.can_deliver_today(current_day):
                continue
            if farm.get_current_weight() < self.min_market_weight_kg:
                continue
            candidates.append(farm)

        candidates.sort(key=lambda f: f.get_current_weight(), reverse=True)
        return candidates

    def _nearest_slaughterhouse_with_capacity(
        self,
        farm: Farm,
        remaining_capacity_sh: Dict[str, int],
    ) -> Optional[Slaughterhouse]:
        """Escoge el escorxador más cercano con algo de capacidad disponible."""
        best_sh: Optional[Slaughterhouse] = None
        best_dist = float("inf")

        for sh in self.slaughterhouses:
            cap = remaining_capacity_sh.get(sh.slaughterhouse_id, 0)
            if cap <= 0:
                continue
            dist = self._haversine_km(farm.lat, farm.lon, sh.lat, sh.lon)
            if dist < best_dist:
                best_dist = dist
                best_sh = sh

        return best_sh


    def _has_any_remaining_pigs(self, remaining_pigs: Dict[str, int]) -> bool:
        return any(v > 0 for v in remaining_pigs.values())

    def _build_route_for_transport(
        self,
        transport: Transport,
        current_day: int,
        candidate_farms: List[Farm],
        remaining_pigs: Dict[str, int],
        remaining_capacity_sh: Dict[str, int],
        current_hours_used: float,
    ) -> Optional[PlannedRoute]:
        """
        Construye UNA ruta para un camión concreto en un día dado.
        Devuelve None si no hay ruta factible.
        """

        feasible_farms = [
            f for f in candidate_farms
            if remaining_pigs.get(f.farm_id, 0) > 0 and f.can_deliver_today(current_day)
        ]
        if not feasible_farms:
            return None

        feasible_farms.sort(key=lambda f: f.get_current_weight(), reverse=True)
        seed_farm = feasible_farms[0]

        initial_sh = self._nearest_slaughterhouse_with_capacity(
            seed_farm, remaining_capacity_sh
        )
        if initial_sh is None:
            return None

        sh_id = initial_sh.slaughterhouse_id
        sh_remaining_cap = remaining_capacity_sh.get(sh_id, 0)
        if sh_remaining_cap <= 0:
            return None

        truck_capacity_kg = transport.capacity_tons * 1000
        remaining_capacity_kg = truck_capacity_kg

        selected_stops: List[PlannedStop] = []
        farms_in_route: List[Farm] = []
        distance_km: float = 0.0

        while len(farms_in_route) < self.max_stops_per_route:
            best_candidate: Optional[Farm] = None
            best_incremental_distance: float = float("inf")
            best_new_distance: float = 0.0
            best_pigs_to_pick: int = 0

            for farm in candidate_farms:
                if remaining_pigs.get(farm.farm_id, 0) <= 0:
                    continue
                if farm in farms_in_route:
                    continue
                if not farm.can_deliver_today(current_day):
                    continue

                avg_w = farm.get_current_weight()
                if avg_w <= 0:
                    continue

                max_pigs_by_truck = int(remaining_capacity_kg / avg_w)
                if max_pigs_by_truck <= 0:
                    continue

                pigs_possible = min(
                    max_pigs_by_truck,
                    remaining_pigs[farm.farm_id],
                    sh_remaining_cap,
                )
                if pigs_possible <= 0:
                    continue

                if not farms_in_route:
                    current_dist = 0.0
                    new_dist = self._route_distance_km(initial_sh, [farm])
                else:
                    current_dist = self._route_distance_km(initial_sh, farms_in_route)
                    new_dist = self._route_distance_km(initial_sh, farms_in_route + [farm])

                incremental = new_dist - current_dist
                if incremental < best_incremental_distance:
                    best_incremental_distance = incremental
                    best_candidate = farm
                    best_new_distance = new_dist
                    best_pigs_to_pick = pigs_possible

            if best_candidate is None:
                break

            new_time_hours = best_new_distance / self.speed_kmh if self.speed_kmh > 0 else 0.0
            if current_hours_used + new_time_hours > self.max_hours_per_day:
                if not farms_in_route:
                    return None
                break

            farms_in_route.append(best_candidate)
            distance_km = best_new_distance
            sh_remaining_cap -= best_pigs_to_pick
            remaining_capacity_kg -= best_pigs_to_pick * best_candidate.get_current_weight()
            remaining_pigs[best_candidate.farm_id] -= best_pigs_to_pick
            selected_stops.append(
                PlannedStop(farm=best_candidate, pigs_to_pick=best_pigs_to_pick)
            )

            if remaining_capacity_kg <= 0 or sh_remaining_cap <= 0:
                break

        if not selected_stops:
            return None

        time_hours = distance_km / self.speed_kmh if self.speed_kmh > 0 else 0.0

        remaining_capacity_sh[sh_id] = sh_remaining_cap

        return PlannedRoute(
            day=current_day,
            transport=transport,
            slaughterhouse=initial_sh,
            stops=selected_stops,
            distance_km=distance_km,
            time_hours=time_hours,
        )

    def build_daily_plan(self, current_day: int) -> List[PlannedRoute]:
        """
        Construye un conjunto de rutas para un día concreto.

        Estrategia:
        - Selecciona granjas candidatas (peso >= umbral, 1 visita/semana, inventario > 0).
        - Mantiene capacidades disponibles por escorxador.
        - Para cada camión, construye tantas rutas como quepan en 8h/día.
        - Cada ruta puede visitar hasta 3 granjas.
        """
        planned_routes: List[PlannedRoute] = []

        candidate_farms = self._select_candidate_farms(current_day)
        if not candidate_farms or not self.transports or not self.slaughterhouses:
            return planned_routes

        remaining_pigs = {farm.farm_id: farm.inventory_pigs for farm in candidate_farms}
        remaining_capacity_sh = {
            sh.slaughterhouse_id: sh.get_available_capacity() for sh in self.slaughterhouses
        }
        daily_hours: Dict[str, float] = {
            transport.transport_id: 0.0 for transport in self.transports
        }

        def any_sh_capacity() -> bool:
            return any(cap > 0 for cap in remaining_capacity_sh.values())

        def any_pigs_left() -> bool:
            return self._has_any_remaining_pigs(remaining_pigs)

        for transport in self.transports:
            tid = transport.transport_id

            while daily_hours[tid] < self.max_hours_per_day and any_pigs_left() and any_sh_capacity():
                route = self._build_route_for_transport(
                    transport=transport,
                    current_day=current_day,
                    candidate_farms=candidate_farms,
                    remaining_pigs=remaining_pigs,
                    remaining_capacity_sh=remaining_capacity_sh,
                    current_hours_used=daily_hours[tid],
                )
                if route is None:
                    break

                planned_routes.append(route)
                daily_hours[tid] += route.time_hours

        return planned_routes
