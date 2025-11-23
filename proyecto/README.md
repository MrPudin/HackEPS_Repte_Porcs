# Simulación logística de porcs – Catalunya

Este proyecto implementa un sistema de **planificación y simulación logística** para el transporte de cerdos desde granjas hasta escorxadors (mataderos) en Catalunya.

Incluye:

- Modelo de **granjas**, **escorxadors** y **camiones** con capacidades, costes y restricciones.
- Planificación de rutas **quinzenal** (10 días laborables), con:
  - Granjas visitadas como máximo **1 vez por semana**.
  - Rutas con **hasta 3 granjas por camión**.
  - Límite de **8 horas de trabajo por camión y día**.
- Cálculo de **costes, penalizaciones y beneficio** según rangos de peso.
- **KPIs** globales y por día.
- Módulos de **visualización** (mapas y dashboards) con Plotly.

---

## 1. Requisitos

- Python **3.9+** (recomendado 3.10 o superior).
- Entorno virtual (opcional pero recomendable).

Dependencias principales de Python:

- `pandas`
- `numpy`
- `plotly`
- `openpyxl`

Si el proyecto incluye un `requirements.txt`, basta con instalar a partir de ahí.

---

## 2. Estructura del proyecto

Dentro del ZIP `Repte_HackEPS`:

```text
Repte_HackEPS/
├─ Repte Hackathon_FV.pdf      # Enunciado original del reto
├─ Dades/                      # Datos originales (no estrictamente necesarios para ejecutar)
│   └─ ...                     
└─ proyecto/
    ├─ main.py                 # Punto de entrada principal
    ├─ README.md               # (este documento)
    ├─ data/
    │   ├─ farms 1.csv
    │   ├─ slaughterhouses 1.csv
    │   ├─ transports 1.csv
    │   ├─ Consumption 1.xlsx
    │   └─ weight 1.xlsx
    │
    ├─ src/
    │   ├─ __init__.py
    │   ├─ models/
    │   │   ├─ __init__.py
    │   │   ├─ Farm.py
    │   │   ├─ Slaughterhouse.py
    │   │   └─ Transport.py
    │   │
    │   ├─ utils/
    │   │   ├─ __init__.py
    │   │   ├─ data_loader.py
    │   │   ├─ BiologicalDataManager.py
    │   │   └─ metrics.py
    │   │
    │   ├─ simulation/
    │   │   ├─ __init__.py
    │   │   ├─ Simulator.py
    │   │   └─ Router.py
    │   │
    │   └─ optimization/
    │       ├─ __init__.py
    │       └─ Optimizer.py    # módulo opcional para jugar con parámetros
    │
    └─ visualization/
        ├─ __init__.py
        ├─ dashboard.py
        └─ map.py
