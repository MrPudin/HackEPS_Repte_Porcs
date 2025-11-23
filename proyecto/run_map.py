# run_map.py

from src.utils.data_loader import DataLoader
from src.models.Farm import Farm
from src.models.Slaughterhouse import Slaughterhouse
from visualization.map import plot_infrastructure_map

import plotly.io as pio
pio.renderers.default = "browser"  # para que abra el navegador por defecto


def main():
    print("[run_map] Cargando datos...")
    loader = DataLoader("data")
    farms_df, slaughterhouses_df, transports_df = loader.load_all_data()

    print("[run_map] Creando objetos Farm y Slaughterhouse...")
    farms = [
        Farm(
            farm_id=str(row["farm_id"]),
            name=str(row["name"]),
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            inventory_pigs=int(row["inventory_pigs"]),
            avg_weight_kg=float(row["avg_weight_kg"]),
            growth_rate_kg_per_week=float(row["growth_rate_kg_per_week"]),
            age_weeks=int(row["age_weeks"]),
            price_per_kg=float(row["price_per_kg"]),
            consumption_pigs=float(row["consumption_pigs"]),
            capacity=int(row["capacity"]),
        )
        for _, row in farms_df.iterrows()
    ]

    slaughterhouses = [
        Slaughterhouse(
            slaughterhouse_id=str(row["slaughterhouse_id"]),
            name=str(row["name"]),
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            capacity_per_day=int(row["capacity_per_day"]),
            price_per_kg=float(row["price_per_kg"]),
            penalty_15_min=float(row["penalty_15_min"]),
            penalty_15_max=float(row["penalty_15_max"]),
            penalty_20_min=float(row["penalty_20_min"]),
            penalty_20_max=float(row["penalty_20_max"]),
        )
        for _, row in slaughterhouses_df.iterrows()
    ]

    print(f"[run_map] Granjas cargadas: {len(farms)}")
    print(f"[run_map] Escorxadors cargados: {len(slaughterhouses)}")
    print("[run_map] Mostrando mapa...")
    plot_infrastructure_map(farms, slaughterhouses)


if __name__ == "__main__":
    main()
