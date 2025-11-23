from dataclasses import dataclass, field
from typing import List, Tuple
import math

@dataclass
class Farm:
    """Representa una granja de porcos."""
    
    farm_id: str
    name: str
    lat: float
    lon: float
    inventory_pigs: int  # Número actual de porcos
    avg_weight_kg: float  # Peso promedio actual
    growth_rate_kg_per_week: float  # Crecimiento semanal
    age_weeks: int  # Edad actual en semanas
    price_per_kg: float  # Precio por kg canal
    consumption_pigs: float  # Consumo por cerdo por día (kg)
    capacity: int  # Capacidad máxima de la granja
    
    # Atributos de control simulación
    pigs_delivered_week: int = 0  # Porcos enviados esta "semana logística"
    last_delivery_day: int = -5  # Último día que se visitó (semana de 5 días)
    weekly_inventory_history: List[int] = field(default_factory=list)
    
    def get_location(self) -> Tuple[float, float]:
        """Retorna coordenadas GPS."""
        return (self.lat, self.lon)
    
    def get_current_weight(self) -> float:
        """Retorna el peso actual promedio de los porcos."""
        return self.avg_weight_kg
    
    def update_growth(self, days_passed: int = 1):
        """Actualiza el peso según días transcurridos."""
        weekly_growth = self.growth_rate_kg_per_week
        daily_growth = weekly_growth / 7
        self.avg_weight_kg += daily_growth * days_passed
        self.age_weeks += days_passed / 7
    
    def get_revenue(self, pigs_count: int, avg_weight: float) -> Tuple[float, float]:
        """
        Calcula ingresos y aplica penalización por peso desde el punto de vista
        de la granja. Esta función es opcional porque el cálculo "oficial"
        se hace en Slaughterhouse, pero la dejamos por compatibilidad.
        Retorna: (ingresos_totales, penalización_aplicada)
        """
        total_kg = pigs_count * avg_weight
        penalty = 0.0
        
        # Penalización 15% para 100–105 o 115–120 kg (fuera del rango ideal)
        if (avg_weight < 105 or avg_weight > 115) and (100 <= avg_weight <= 120):
            penalty = 0.15
        # Penalización 20% para <100 o >120 kg
        elif avg_weight < 100 or avg_weight > 120:
            penalty = 0.20
        
        revenue = total_kg * self.price_per_kg * (1 - penalty)
        return revenue, penalty
    
    def can_deliver_today(self, current_day: int) -> bool:
        """
        Comprueba si puede entregar hoy.
        
        Regla: máximo 1 vez por semana logística.
        Definimos semana logística como bloques de 5 días:
        - días 0–4: semana 0
        - días 5–9: semana 1
        etc.
        """
        if self.inventory_pigs <= 0:
            return False
        
        if self.last_delivery_day < 0:
            # Nunca se ha entregado, puede entregar
            return True
        
        current_week = current_day // 5
        last_week = self.last_delivery_day // 5
        return current_week != last_week
    
    def deliver_pigs(self, pigs_count: int, current_day: int) -> bool:
        """
        Entrega porcos si es posible.
        Retorna True si se completó la entrega.
        """
        if pigs_count <= 0:
            return False
        
        if pigs_count > self.inventory_pigs:
            return False
        
        if not self.can_deliver_today(current_day):
            return False
        
        self.inventory_pigs -= pigs_count
        self.pigs_delivered_week += pigs_count
        self.last_delivery_day = current_day
        self.weekly_inventory_history.append(self.inventory_pigs)
        
        return True
    
    def reset_weekly_counter(self):
        """Reinicia contador semanal (se llama al fin de semana logística)."""
        self.pigs_delivered_week = 0
    
    def __repr__(self) -> str:
        return (f"Farm(id={self.farm_id}, name={self.name}, "
                f"pigs={self.inventory_pigs}, weight={self.avg_weight_kg:.1f}kg)")
