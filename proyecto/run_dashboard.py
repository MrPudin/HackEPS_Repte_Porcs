# run_dashboard.py

from src.utils.data_loader import DataLoader
from src.utils.BiologicalDataManager import BiologicalDataManager
from src.models.Farm import Farm
from src.models.Slaughterhouse import Slaughterhouse
from src.models.Transport import Transport
from src.simulation.Simulator import Simulator

from visualization.dashboard import (
    plot_daily_pigs,
    plot_daily_profit,
    plot_avg_pigs_per_route,
    plot_avg_distance_per_route,
)

import plotly.io as pio
pio.renderers.default = "browser"  # abre las figuras en el navegador


DAYS_TO_SIMULATE = 10  # 2 semanas laborales


def build_domain_objects():
    """Carga datos y construye farms, slaughterhouses y transports."""
    loader = DataLoader("data")
    farms_df, slaughterhouses_df, transports_df = loader.load_all_data()

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

    transports = [
        Transport(
            transport_id=str(row["transport_id"]),
            type=str(row["type"]),
            capacity_tons=float(row["capacity_tons"]),
            cost_per_km=float(row["cost_per_km"]),
            max_hours_per_week=float(row["max_hours_per_week"]),
            fixed_weekly_cost=float(row["fixed_weekly_cost"]),
        )
        for _, row in transports_df.iterrows()
    ]

    loader_consumption = loader.get_consumption_data()
    loader_weight = loader.get_weight_data()

    bio_manager = BiologicalDataManager(
        loader_consumption,
        loader_weight,
    )

    return farms, slaughterhouses, transports, bio_manager


def main():
    print("[run_dashboard] Construyendo objetos de dominio...")
    farms, slaughterhouses, transports, bio_manager = build_domain_objects()

    print(
        f"[run_dashboard] Granjas: {len(farms)}, "
        f"escorxadors: {len(slaughterhouses)}, camiones: {len(transports)}"
    )

    print("[run_dashboard] Creando simulador...")
    simulator = Simulator(
        farms=farms,
        slaughterhouses=slaughterhouses,
        transports=transports,
        biological_manager=bio_manager,
    )

    print(f"[run_dashboard] Ejecutando simulación de {DAYS_TO_SIMULATE} días...")
    events = simulator.run(days=DAYS_TO_SIMULATE)

    if events is None or events.empty:
        print("[run_dashboard] La simulación no ha generado eventos. Nada que mostrar.")
        return

    print("[run_dashboard] Mostrando gráficos...")

    plot_daily_pigs(events)

    plot_daily_profit(events)

    plot_avg_pigs_per_route(events)

    plot_avg_distance_per_route(events)


if __name__ == "__main__":
    main()
