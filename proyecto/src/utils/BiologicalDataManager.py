"""
Gestiona datos biológicos: distribuciones de peso y consumo según edad.
Estos datos provienen de los archivos Excel de consumo y peso.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
from scipy.stats import norm

class BiologicalDataManager:
    """Gestiona distribuciones de peso y consumo de porcos por edad."""
    
    def __init__(self, consumption_df: pd.DataFrame, weight_df: pd.DataFrame):
        """
        Inicializa con datos de consumo y peso.
        
        Args:
            consumption_df: DataFrame con columnas [age_weeks, intake_kg, mean, sd]
            weight_df: DataFrame con columnas [age_weeks, weight_kg, mean, sd]
        """
        self.consumption_df = consumption_df
        self.weight_df = weight_df
        self._normalize_columns()
    
    def _normalize_columns(self):
        """Normaliza nombres de columnas para consistencia."""
        # Consumo
        if not self.consumption_df.empty:
            cols = self.consumption_df.columns.str.strip().str.lower()
            self.consumption_df.columns = cols
        
        # Peso
        if not self.weight_df.empty:
            cols = self.weight_df.columns.str.strip().str.lower()
            self.weight_df.columns = cols
    
    def get_weight_by_age(self, age_weeks: float) -> Tuple[float, float]:
        """
        Obtiene peso medio y desviación estándar para una edad.
        
        Returns:
            (weight_mean_kg, weight_sd_kg)
        """
        if self.weight_df.empty:
            # Fallback: estimación lineal simple
            return self._estimate_weight(age_weeks), 5.0
        
        # Buscar por edad exacta o interpolar
        return self._interpolate_value(
            self.weight_df, 
            'age of pigs in week', 
            age_weeks, 
            'mean', 
            'sd'
        )
    
    def get_consumption_by_age(self, age_weeks: float) -> Tuple[float, float]:
        """
        Obtiene consumo medio y desviación estándar para una edad.
        
        Returns:
            (consumption_mean_kg, consumption_sd_kg)
        """
        if self.consumption_df.empty:
            # Fallback: estimación simple
            return self._estimate_consumption(age_weeks), 2.0
        
        return self._interpolate_value(
            self.consumption_df, 
            'age of pigs in week', 
            age_weeks, 
            'mean', 
            'sd'
        )
    
    def _interpolate_value(self, df: pd.DataFrame, age_col: str, 
                          age: float, mean_col: str, sd_col: str) -> Tuple[float, float]:
        """
        Interpola valores para una edad entre datos discretos.
        """
        # Buscar columnas con nombres similares
        age_cols = [c for c in df.columns if 'age' in c.lower() and 'week' in c.lower()]
        mean_cols = [c for c in df.columns if 'mean' in c.lower()]
        sd_cols = [c for c in df.columns if 'sd' in c.lower()]
        
        if not age_cols or not mean_cols or not sd_cols:
            return 0.0, 0.0
        
        age_col = age_cols[0]
        mean_col = mean_cols[0]
        sd_col = sd_cols[0]
        
        # Encontrar índices para interpolación
        df_sorted = df.sort_values(age_col)
        ages = df_sorted[age_col].values
        means = df_sorted[mean_col].values
        sds = df_sorted[sd_col].values
        
        # Si la edad es menor que el mínimo
        if age <= ages[0]:
            return float(means[0]), float(sds[0])
        
        # Si la edad es mayor que el máximo
        if age >= ages[-1]:
            return float(means[-1]), float(sds[-1])
        
        # Interpolación lineal
        idx = np.searchsorted(ages, age)
        age1, age2 = ages[idx-1], ages[idx]
        mean1, mean2 = means[idx-1], means[idx]
        sd1, sd2 = sds[idx-1], sds[idx]
        
        factor = (age - age1) / (age2 - age1)
        mean = mean1 + factor * (mean2 - mean1)
        sd = sd1 + factor * (sd2 - sd1)
        
        return float(mean), float(sd)
    
    def _estimate_weight(self, age_weeks: float) -> float:
        """Estimación simple de peso si no hay datos."""
        # Aproximación: crecimiento no-lineal
        # Porcos típicamente van de ~10kg a ~120kg entre 5 y 25 semanas
        return 10 + (age_weeks - 5) * 5.5
    
    def _estimate_consumption(self, age_weeks: float) -> float:
        """Estimación simple de consumo si no hay datos."""
        # Aproximación: consumo crece con edad
        return 1.5 + age_weeks * 0.3
    
    def generate_weight_distribution(self, age_weeks: float, 
                                    num_pigs: int = 1000) -> np.ndarray:
        """
        Genera una distribución de pesos para un lote de porcos.
        Usa distribución normal basada en datos reales.
        
        Returns:
            Array de pesos en kg para num_pigs porcos
        """
        mean, sd = self.get_weight_by_age(age_weeks)
        
        # Generar distribución normal
        weights = np.random.normal(mean, sd, num_pigs)
        
        # Limitar a rangos realistas (evitar valores negativos o extremos)
        weights = np.clip(weights, 5, 150)
        
        return weights
    
    def get_weight_range_percentage(self, age_weeks: float, 
                                   min_kg: float = 105, 
                                   max_kg: float = 115) -> float:
        """
        Calcula qué porcentaje de porcos caen en rango ideal.
        
        Args:
            age_weeks: Edad de los porcos
            min_kg: Peso mínimo ideal
            max_kg: Peso máximo ideal
        
        Returns:
            Porcentaje (0-100) de porcos en rango
        """
        mean, sd = self.get_weight_by_age(age_weeks)
        
        # Usar distribución normal acumulada
        p_min = norm.cdf(min_kg, mean, sd)
        p_max = norm.cdf(max_kg, mean, sd)
        
        return (p_max - p_min) * 100
    
    def get_statistics_by_age(self, age_weeks: float) -> dict:
        """Retorna estadísticas completas para una edad."""
        weight_mean, weight_sd = self.get_weight_by_age(age_weeks)
        consumption_mean, consumption_sd = self.get_consumption_by_age(age_weeks)
        ideal_range_pct = self.get_weight_range_percentage(age_weeks)
        
        return {
            "age_weeks": age_weeks,
            "weight_mean_kg": weight_mean,
            "weight_sd_kg": weight_sd,
            "consumption_mean_kg": consumption_mean,
            "consumption_sd_kg": consumption_sd,
            "ideal_range_percentage": ideal_range_pct
        }
    
    def __repr__(self) -> str:
        return (f"BiologicalDataManager("
                f"consumption_records={len(self.consumption_df)}, "
                f"weight_records={len(self.weight_df)})")