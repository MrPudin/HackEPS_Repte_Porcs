import pandas as pd
import os
from typing import Dict, List, Tuple
import sqlite3

class DataLoader:
    """Carga y valida datos desde CSV para la simulación logística."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.farms = None
        self.slaughterhouses = None
        self.transports = None
        self.consumption_data = None
        self.weight_data = None
    
    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Carga todos los CSV necesarios."""
        try:
            self.farms = self._load_farms()
            self.slaughterhouses = self._load_slaughterhouses()
            self.transports = self._load_transports()
            self.consumption_data = self._load_consumption()
            self.weight_data = self._load_weight()
            
            print("✓ Datos cargados exitosamente")
            print(f"  - {len(self.farms)} granjas")
            print(f"  - {len(self.slaughterhouses)} escorxadores")
            print(f"  - {len(self.transports)} tipos de transporte")
            print(f"  - Datos de consumo: {len(self.consumption_data)} semanas")
            print(f"  - Datos de peso: {len(self.weight_data)} semanas")
            
            return self.farms, self.slaughterhouses, self.transports
        
        except FileNotFoundError as e:
            print(f"✗ Error: Archivo no encontrado - {e}")
            raise
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
            raise
    
    def _load_farms(self) -> pd.DataFrame:
        """Carga y valida el CSV de granjas."""
        file_path = os.path.join(self.data_dir, "farms 1.csv")
        df = pd.read_csv(file_path)
        
        # Validar columnas requeridas
        required_cols = [
            'farm_id', 'name', 'lat', 'lon', 'inventory_pigs',
            'avg_weight_kg', 'growth_rate_kg_per_week', 'age_weeks',
            'price_per_kg', 'consumption_pigs', 'capacity'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columnas faltantes en farms: {missing_cols}")
        
        # Convertir tipos de datos
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df['inventory_pigs'] = pd.to_numeric(df['inventory_pigs'], errors='coerce')
        df['avg_weight_kg'] = pd.to_numeric(df['avg_weight_kg'], errors='coerce')
        df['growth_rate_kg_per_week'] = pd.to_numeric(df['growth_rate_kg_per_week'], errors='coerce')
        df['age_weeks'] = pd.to_numeric(df['age_weeks'], errors='coerce')
        df['price_per_kg'] = pd.to_numeric(df['price_per_kg'], errors='coerce')
        df['consumption_pigs'] = pd.to_numeric(df['consumption_pigs'], errors='coerce')
        df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
        
        # Validar datos no nulos
        if df[required_cols].isnull().any().any():
            print("⚠ Advertencia: Hay valores nulos en las granjas")
            df = df.dropna(subset=required_cols)
        
        return df
    
    def _load_slaughterhouses(self) -> pd.DataFrame:
        """Carga y valida el CSV de escorxadores."""
        file_path = os.path.join(self.data_dir, "slaughterhouses 1.csv")
        df = pd.read_csv(file_path)
        
        required_cols = [
            'slaughterhouse_id', 'name', 'lat', 'lon', 'capacity_per_day',
            'price_per_kg', 'penalty_15_min', 'penalty_15_max',
            'penalty_20_min', 'penalty_20_max'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columnas faltantes en escorxadores: {missing_cols}")
        
        # Convertir tipos de datos
        numeric_cols = [col for col in required_cols if col != 'slaughterhouse_id' and col != 'name']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if df[required_cols].isnull().any().any():
            print("⚠ Advertencia: Hay valores nulos en los escorxadores")
            df = df.dropna(subset=required_cols)
        
        return df
    
    def _load_transports(self) -> pd.DataFrame:
        """Carga y valida el CSV de transportes."""
        file_path = os.path.join(self.data_dir, "transports 1.csv")
        df = pd.read_csv(file_path)
        
        required_cols = [
            'transport_id', 'type', 'capacity_tons', 'cost_per_km',
            'max_hours_per_week', 'fixed_weekly_cost'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columnas faltantes en transportes: {missing_cols}")
        
        numeric_cols = ['capacity_tons', 'cost_per_km', 'max_hours_per_week', 'fixed_weekly_cost']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if df[required_cols].isnull().any().any():
            print("⚠ Advertencia: Hay valores nulos en los transportes")
            df = df.dropna(subset=required_cols)
        
        return df
    
    def _load_consumption(self) -> pd.DataFrame:
        """
        Carga y prepara los datos de consumo por edad desde el Excel
        'Consumption 1.xlsx'.

        El Excel tiene estructura:
        - Fila 0: ["Age of pigs in week", "mean", "sd"]
        - Filas siguientes: valores
        """
        file_path = os.path.join(self.data_dir, "Consumption 1.xlsx")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encontró el fichero de consumo: {file_path}")

        # Leemos sin usar la primera fila como cabecera
        raw = pd.read_excel(file_path, header=None)

        # Fila 0 son los nombres "lógicos"
        header = raw.iloc[0].tolist()
        # Esperamos algo como: ["Age of pigs in week", "mean", "sd"]
        data = raw.iloc[1:].copy()
        data.columns = [
            "age of pigs in week",
            "mean",
            "sd",
        ]

        # Aseguramos tipos numéricos
        data["age of pigs in week"] = pd.to_numeric(
            data["age of pigs in week"], errors="coerce"
        )
        data["mean"] = pd.to_numeric(data["mean"], errors="coerce")
        data["sd"] = pd.to_numeric(data["sd"], errors="coerce")

        data = data.dropna(subset=["age of pigs in week", "mean", "sd"])

        return data

    def _load_weight(self) -> pd.DataFrame:
        """
        Carga y prepara los datos de peso por edad desde el Excel
        'weight 1.xlsx'.

        Misma estructura que el de consumo.
        """
        file_path = os.path.join(self.data_dir, "weight 1.xlsx")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encontró el fichero de peso: {file_path}")

        raw = pd.read_excel(file_path, header=None)

        header = raw.iloc[0].tolist()
        data = raw.iloc[1:].copy()
        data.columns = [
            "age of pigs in week",
            "mean",
            "sd",
        ]

        data["age of pigs in week"] = pd.to_numeric(
            data["age of pigs in week"], errors="coerce"
        )
        data["mean"] = pd.to_numeric(data["mean"], errors="coerce")
        data["sd"] = pd.to_numeric(data["sd"], errors="coerce")

        data = data.dropna(subset=["age of pigs in week", "mean", "sd"])

        return data

    def get_consumption_data(self) -> pd.DataFrame:
        """Retorna el DataFrame de consumo biológico."""
        if self.consumption_data is None:
            raise ValueError("Datos de consumo no cargados. Llama a load_all_data() primero.")
        return self.consumption_data

    def get_weight_data(self) -> pd.DataFrame:
        """Retorna el DataFrame de peso biológico."""
        if self.weight_data is None:
            raise ValueError("Datos de peso no cargados. Llama a load_all_data() primero.")
        return self.weight_data

    
    def get_farms(self) -> pd.DataFrame:
        """Retorna el DataFrame de granjas."""
        if self.farms is None:
            raise ValueError("Datos no cargados. Llama a load_all_data() primero.")
        return self.farms
    
    def get_slaughterhouses(self) -> pd.DataFrame:
        """Retorna el DataFrame de escorxadores."""
        if self.slaughterhouses is None:
            raise ValueError("Datos no cargados. Llama a load_all_data() primero.")
        return self.slaughterhouses
    
    def get_transports(self) -> pd.DataFrame:
        """Retorna el DataFrame de transportes."""
        if self.transports is None:
            raise ValueError("Datos no cargados. Llama a load_all_data() primero.")
        return self.transports