from dataclasses import dataclass, field
from typing import List, Tuple
from enum import Enum

class TransportStatus(Enum):
    """Estados posibles de un transporte."""
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    LOADING = "loading"
    FULL = "full"
    MAINTENANCE = "maintenance"

@dataclass
class Route:
    """Representa una ruta de un transporte (granjas -> escorxador)."""
    route_id: str
    farms_visited: List[str] = field(default_factory=list)
    total_distance_km: float = 0.0
    total_time_hours: float = 0.0
    pigs_loaded: int = 0
    current_load_kg: float = 0.0
    trip_cost: float = 0.0
    slaughterhouse_id: str = ""
    
    def add_farm(self, farm_id: str, distance_km: float, time_hours: float):
        """Añade una granja a la ruta."""
        if len(self.farms_visited) < 3:
            self.farms_visited.append(farm_id)
            self.total_distance_km += distance_km
            self.total_time_hours += time_hours
            return True
        return False
    
    def is_full_capacity(self) -> bool:
        """Comprueba si alcanzó el máximo de granjas."""
        return len(self.farms_visited) >= 3

@dataclass
class Transport:
    """Representa un vehículo de transporte."""
    
    transport_id: str
    type: str
    capacity_tons: float
    cost_per_km: float
    max_hours_per_week: float
    fixed_weekly_cost: float
    
    current_load_kg: float = 0.0
    pigs_aboard: int = 0
    status: TransportStatus = TransportStatus.AVAILABLE
    current_route: Route = None
    hours_used_this_week: float = 0.0
    routes_completed: List[Route] = field(default_factory=list)
    
    def get_available_capacity_kg(self) -> float:
        """Retorna capacidad disponible en kg."""
        capacity_kg = self.capacity_tons * 1000
        return max(0, capacity_kg - self.current_load_kg)
    
    def get_available_capacity_pigs(self, avg_pig_weight_kg: float) -> int:
        """Retorna cuántos porcos pueden cargarse."""
        if avg_pig_weight_kg <= 0:
            return 0
        available_kg = self.get_available_capacity_kg()
        return int(available_kg / avg_pig_weight_kg)
    
    def is_full(self) -> bool:
        """Comprueba si está a capacidad."""
        capacity_kg = self.capacity_tons * 1000
        return self.current_load_kg >= capacity_kg * 0.95
    
    def can_use_hours(self, hours_needed: float) -> bool:
        """Comprueba si tiene horas disponibles esta semana."""
        return (self.hours_used_this_week + hours_needed) <= self.max_hours_per_week
    
    def load_pigs(self, pigs_count: int, avg_weight_kg: float) -> Tuple[bool, int]:
        """
        Intenta cargar porcos.
        Retorna: (éxito, cantidad_cargada)
        """
        weight_needed_kg = pigs_count * avg_weight_kg
        
        if weight_needed_kg > self.get_available_capacity_kg():
            pigs_count = self.get_available_capacity_pigs(avg_weight_kg)
            weight_needed_kg = pigs_count * avg_weight_kg
        
        if pigs_count == 0:
            return False, 0
        
        self.current_load_kg += weight_needed_kg
        self.pigs_aboard += pigs_count
        
        return True, pigs_count
    
    def start_route(self, route_id: str, slaughterhouse_id: str) -> Route:
        """Inicia una nueva ruta."""
        self.status = TransportStatus.LOADING
        self.current_route = Route(
            route_id=route_id,
            slaughterhouse_id=slaughterhouse_id
        )
        return self.current_route
    
    def complete_route(self, distance_km: float, time_hours: float) -> Tuple[bool, dict]:
        """
        Completa la ruta actual.
        Retorna: (éxito, información_ruta)
        """
        if self.current_route is None:
            return False, {"error": "No hay ruta activa"}
        
        if not self.can_use_hours(time_hours):
            return False, {"error": "Horas insuficientes esta semana"}
        

        trip_cost = distance_km * self.cost_per_km * (self.current_load_kg / (self.capacity_tons * 1000))
        
        self.current_route.total_distance_km = distance_km
        self.current_route.total_time_hours = time_hours
        self.current_route.pigs_loaded = self.pigs_aboard
        self.current_route.current_load_kg = self.current_load_kg
        self.current_route.trip_cost = trip_cost
        
        self.routes_completed.append(self.current_route)
        self.hours_used_this_week += time_hours
        
        route_info = {
            "route_id": self.current_route.route_id,
            "farms_visited": self.current_route.farms_visited,
            "distance_km": distance_km,
            "time_hours": time_hours,
            "pigs_delivered": self.pigs_aboard,
            "load_kg": self.current_load_kg,
            "cost": trip_cost,
            "capacity_utilized": f"{(self.current_load_kg / (self.capacity_tons * 1000) * 100):.1f}%"
        }
        
        self.current_load_kg = 0.0
        self.pigs_aboard = 0
        self.current_route = None
        self.status = TransportStatus.AVAILABLE
        
        return True, route_info
    
    def get_weekly_summary(self) -> dict:
        """Retorna resumen de la semana."""
        total_distance = sum(r.total_distance_km for r in self.routes_completed)
        total_cost = sum(r.trip_cost for r in self.routes_completed) + self.fixed_weekly_cost
        total_pigs = sum(r.pigs_loaded for r in self.routes_completed)
        total_time = sum(r.total_time_hours for r in self.routes_completed)
        
        return {
            "transport_id": self.transport_id,
            "type": self.type,
            "routes_completed": len(self.routes_completed),
            "total_pigs_delivered": total_pigs,
            "total_distance_km": total_distance,
            "total_time_hours": total_time,
            "total_cost": total_cost,
            "hours_available": self.max_hours_per_week,
            "hours_utilization": f"{(total_time / self.max_hours_per_week * 100):.1f}%"
        }
    
    def reset_weekly(self):
        """Reinicia contadores semanales."""
        self.hours_used_this_week = 0.0
        self.routes_completed = []
        self.current_load_kg = 0.0
        self.pigs_aboard = 0
        self.status = TransportStatus.AVAILABLE
    
    def __repr__(self) -> str:
        return (f"Transport(id={self.transport_id}, type={self.type}, "
                f"capacity={self.capacity_tons}T, load={self.current_load_kg:.0f}kg)")