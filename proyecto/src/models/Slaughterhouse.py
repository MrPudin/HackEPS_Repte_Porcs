from dataclasses import dataclass, field
from typing import Tuple, List
import math

@dataclass
class Slaughterhouse:
    """Representa un escorxador."""
    
    slaughterhouse_id: str
    name: str
    lat: float
    lon: float
    capacity_per_day: int
    price_per_kg: float
    penalty_15_min: float
    penalty_15_max: float 
    penalty_20_min: float
    penalty_20_max: float
    
    pigs_received_today: int = 0
    total_weight_received: float = 0.0
    daily_history: List[dict] = field(default_factory=list)
    
    def get_location(self) -> Tuple[float, float]:
        """Retorna coordenadas GPS."""
        return (self.lat, self.lon)
    
    def get_available_capacity(self) -> int:
        """Retorna capacidad disponible hoy."""
        return max(0, self.capacity_per_day - self.pigs_received_today)
    
    def is_at_capacity(self) -> bool:
        """Comprueba si está al límite de capacidad."""
        return self.pigs_received_today >= self.capacity_per_day
    
    def calculate_penalty(self, avg_weight_kg: float) -> float:
        """
        Calcula la penalización según el peso promedio.
        Retorna el porcentaje de penalización (0.0, 0.15, 0.20).
        """
        if avg_weight_kg < self.penalty_20_min or avg_weight_kg > self.penalty_20_max:
            return 0.20
        
        if avg_weight_kg < self.penalty_15_min or avg_weight_kg > self.penalty_15_max:
            return 0.15
        
        return 0.0
    
    def receive_pigs(self, pigs_count: int, avg_weight_kg: float) -> Tuple[bool, dict]:
        """
        Recibe porcos al escorxador.
        Retorna: (éxito, información_recepción)
        """
        if self.is_at_capacity():
            return False, {"error": "Escorxador a capacidad máxima"}
        
        if pigs_count > self.get_available_capacity():
            pigs_count = self.get_available_capacity()
        
        total_kg_live = pigs_count * avg_weight_kg
        penalty = self.calculate_penalty(avg_weight_kg)
        revenue = total_kg_live * self.price_per_kg * (1 - penalty)
        
        self.pigs_received_today += pigs_count
        self.total_weight_received += total_kg_live
        
        receipt_info = {
            "pigs_count": pigs_count,
            "avg_weight_kg": avg_weight_kg,
            "total_kg_live": total_kg_live,
            "penalty_applied": penalty,
            "revenue": revenue,
            "timestamp": None 
        }
        
        self.daily_history.append(receipt_info)
        return True, receipt_info
    
    def reset_daily_counter(self):
        """Reinicia contadores diarios (fin del día)."""
        self.pigs_received_today = 0
        self.total_weight_received = 0.0
    
    def get_daily_summary(self) -> dict:
        """Retorna resumen del día actual."""
        total_revenue = sum(r["revenue"] for r in self.daily_history)
        total_penalty = sum(r["penalty_applied"] for r in self.daily_history)
        avg_penalty = total_penalty / len(self.daily_history) if self.daily_history else 0
        
        return {
            "slaughterhouse_id": self.slaughterhouse_id,
            "name": self.name,
            "pigs_processed": self.pigs_received_today,
            "total_kg_live": self.total_weight_received,
            "capacity_utilized": f"{(self.pigs_received_today / self.capacity_per_day * 100):.1f}%",
            "total_revenue": total_revenue,
            "avg_penalty_applied": avg_penalty,
            "deliveries_count": len(self.daily_history)
        }
    
    def __repr__(self) -> str:
        return (f"Slaughterhouse(id={self.slaughterhouse_id}, name={self.name}, "
                f"capacity={self.capacity_per_day}, received_today={self.pigs_received_today})")