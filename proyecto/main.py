#!/usr/bin/env python3
"""
Punto de entrada principal para la simulación de logística de porcos.
"""

from src.utils.data_loader import DataLoader
from src.models.Farm import Farm
from src.models.Slaughterhouse import Slaughterhouse
from src.models.Transport import Transport
from src.utils.BiologicalDataManager import BiologicalDataManager
from src.simulation.Simulator import Simulator
from src.utils.metrics import compute_global_kpis, compute_daily_kpis


def main():
    """Función principal."""
    print("=" * 60)
    print("  SIMULACIÓN LOGÍSTICA DE Cerdos - CATALUNYA")
    print("=" * 60)
    print()
    
    print("1. Cargando datos...")
    loader = DataLoader(data_dir="data")
    
    try:
        farms_df, slaughterhouses_df, transports_df = loader.load_all_data()
        print("✓ Datos cargados exitosamente")
        print(f"  - {len(farms_df)} granjas")
        print(f"  - {len(slaughterhouses_df)} mataderos")
        print(f"  - {len(transports_df)} tipos de transporte")
        print(f"  - Datos de consumo: {len(loader.get_consumption_data())} semanas")
        print(f"  - Datos de peso: {len(loader.get_weight_data())} semanas")
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return
    
    print()
    
    print("2. Inicializando granjas...")
    farms = []
    for _, row in farms_df.iterrows():
        farm = Farm(
            farm_id=str(row['farm_id']),
            name=str(row['name']),
            lat=float(row['lat']),
            lon=float(row['lon']),
            inventory_pigs=int(row['inventory_pigs']),
            avg_weight_kg=float(row['avg_weight_kg']),
            growth_rate_kg_per_week=float(row['growth_rate_kg_per_week']),
            age_weeks=int(row['age_weeks']),
            price_per_kg=float(row['price_per_kg']),
            consumption_pigs=float(row['consumption_pigs']),
            capacity=int(row['capacity'])
        )
        farms.append(farm)
    
    print(f"✓ {len(farms)} granjas creadas")
    for farm in farms[:3]:
        print(f"  - {farm}")
    if len(farms) > 3:
        print(f"  ... y {len(farms) - 3} más")
    
    print()
    
    print("3. Inicializando mataderos...")
    slaughterhouses = []
    for _, row in slaughterhouses_df.iterrows():
        slaughterhouse = Slaughterhouse(
            slaughterhouse_id=str(row['slaughterhouse_id']),
            name=str(row['name']),
            lat=float(row['lat']),
            lon=float(row['lon']),
            capacity_per_day=int(row['capacity_per_day']),
            price_per_kg=float(row['price_per_kg']),
            penalty_15_min=float(row['penalty_15_min']),
            penalty_15_max=float(row['penalty_15_max']),
            penalty_20_min=float(row['penalty_20_min']),
            penalty_20_max=float(row['penalty_20_max'])
        )
        slaughterhouses.append(slaughterhouse)
    
    print(f"✓ {len(slaughterhouses)} mataderos creados")
    for sh in slaughterhouses:
        print(f"  - {sh}")
    
    print()
    
    print("4. Inicializando transportes...")
    transports = []
    for _, row in transports_df.iterrows():
        transport = Transport(
            transport_id=str(row['transport_id']),
            type=str(row['type']),
            capacity_tons=float(row['capacity_tons']),
            cost_per_km=float(row['cost_per_km']),
            max_hours_per_week=float(row['max_hours_per_week']),
            fixed_weekly_cost=float(row['fixed_weekly_cost'])
        )
        transports.append(transport)
    
    print(f"✓ {len(transports)} tipos de transporte disponibles")
    for t in transports:
        print(f"  - {t}")
    
    print()
    print("=" * 60)
    print("✓ Inicialización completada exitosamente")
    print("=" * 60)
    
    print("\n5. Cargando datos biológicos...")
    bio_manager = BiologicalDataManager(
        loader.get_consumption_data(),
        loader.get_weight_data()
    )
    print(f"✓ {bio_manager}")
    
    print("\nESTADÍSTICAS DE EJEMPLO (edad 16 semanas):")
    stats = bio_manager.get_statistics_by_age(16)
    print(f"  Peso medio: {stats['weight_mean_kg']:.1f} kg (±{stats['weight_sd_kg']:.1f} kg)")
    print(f"  Consumo: {stats['consumption_mean_kg']:.1f} kg/día")
    print(f"  % en rango ideal (105-115kg): {stats['ideal_range_percentage']:.1f}%")
    
    print()
    
    print("\nRESUMEN DE DATOS:")
    print(f"  Granjas: {len(farms)}")
    print(f"  Escorxadores: {len(slaughterhouses)}")
    print(f"  Transportes: {len(transports)}")
    print(f"  Total de porcos en sistema: {sum(f.inventory_pigs for f in farms)}")
    print()
    
    print("=" * 60)
    print("6. Lanzando simulación (plan quinzenal, 10 días laborables)...")
    print("=" * 60)

    if not farms or not slaughterhouses or not transports:
        print("No hay suficientes entidades (granjas/mataderos/transportes) para simular.")
        return

    simulator = Simulator(
        farms=farms,
        slaughterhouses=slaughterhouses,
        transports=transports,
        biological_manager=bio_manager,
        speed_kmh=60.0,
        min_market_weight_kg=105.0,
        max_stops_per_route=3,
        max_hours_per_day=8.0,
    )

    DAYS_TO_SIMULATE = 10
    events = simulator.run(days=DAYS_TO_SIMULATE)

    if events is None or events.empty:
        print("La simulación no ha generado eventos. Revisa que los CSV tengan datos y que los parámetros tengan sentido.")
        return

    print(f"Simulación completada, rutas ejecutadas: {len(events)}")

    print("\nKPIs GLOBALES (plan quinzenal):")
    kpis = compute_global_kpis(events)
    for k, v in kpis.items():
        print(f"  {k}: {v}")

    print("\nKPIs POR DÍA:")
    daily = compute_daily_kpis(events)
    print(daily.to_string(index=False))


if __name__ == "__main__":
    main()
