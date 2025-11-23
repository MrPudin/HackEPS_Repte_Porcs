# Simulación Logística de Porcs – HackEPS

Este proyecto implementa una simulación logística para el transporte de cerdos desde granjas hasta escorxadors, siguiendo las restricciones del reto de HackEPS.

## Características Principales

- Planificación diaria durante varias jornadas (por defecto 10 días)
- Una granja solo puede ser visitada una vez por semana logística
- Máximo de 3 granjas por ruta
- Límite de 8 horas de trabajo al día por camión
- Capacidad diaria del escorxador respetada
- Cálculo de costes, penalizaciones por peso y beneficio
- Visualización de infraestructura, rutas y KPIs con Plotly

## 1. Requisitos

- **Python** 3.10+ (desarrollado y probado con Python 3.12)
- `pip` instalado
- Se recomienda usar un entorno virtual (`venv`) para aislar las dependencias del sistema

### Estructura Básica del Proyecto

```text
proyecto/
├─ main.py
├─ run_map.py
├─ run_dashboard.py
├─ requirements.txt
├─ README.md
├─ data/
│   ├─ farms 1.csv
│   ├─ slaughterhouses 1.csv
│   ├─ transports 1.csv
│   ├─ Consumption 1.xlsx
│   └─ weight 1.xlsx
├─ src/
│   ├─ models/
│   │   ├─ Farm.py
│   │   ├─ Slaughterhouse.py
│   │   └─ Transport.py
│   ├─ simulation/
│   │   ├─ Simulator.py
│   │   └─ Router.py
│   ├─ optimization/
│   │   └─ Optimizer.py
│   └─ utils/
│       ├─ data_loader.py
│       ├─ BiologicalDataManager.py
│       └─ metrics.py
└─ visualization/
    ├─ map.py
    └─ dashboard.py
```

## 2. Entorno Virtual (venv) e Instalación

Todos los comandos deben ejecutarse desde la carpeta del proyecto:

```bash
cd ~/Repte_HackEPS/proyecto
```

### 2.1 Crear el Entorno Virtual

Si aparece el error "No module named venv", instala primero:

```bash
sudo apt install python3-venv
```

Luego crea el entorno virtual:

```bash
python3 -m venv venv
```

### 2.2 Activar el Entorno Virtual

**Linux / macOS:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

Cuando está activo, el prompt muestra algo así:

```bash
(venv) usuario@maquina:~/Repte_HackEPS/proyecto$
```

### 2.3 Instalar Dependencias

Con el venv activado:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Esto instala:
- `pandas` y librerías de datos
- Lógica interna del simulador
- `Plotly` para visualización

## 3. Datos de Entrada

El proyecto usa la carpeta `data/` para cargar toda la información.

### 3.1 Ficheros Principales

**`farms 1.csv`**

Columnas clave:
- `farm_id`, `name` (nombre), `lat` (latitud), `lon` (longitud)
- `inventory_pigs` (cerdos en inventario), `avg_weight_kg` (peso promedio), `growth_rate_kg_per_week` (crecimiento por semana), `age_weeks` (edad en semanas)
- `price_per_kg` (precio por kg), `consumption_pigs` (consumo de cerdos), `capacity` (capacidad)

**`slaughterhouses 1.csv`**

Columnas clave:
- `slaughterhouse_id`, `name`, `lat`, `lon`
- `capacity_per_day`, `price_per_kg`
- `penalty_15_min`, `penalty_15_max`
- `penalty_20_min`, `penalty_20_max`

**`transports 1.csv`**

Columnas clave:
- `transport_id`, `type`
- `capacity_tons`, `cost_per_km`
- `max_hours_per_week`, `fixed_weekly_cost`

**`Consumption 1.xlsx` y `weight 1.xlsx`**

Usados por `BiologicalDataManager` para modelar:
- Crecimiento por edad
- Consumo por edad

**Nota:** Si cambias nombres o rutas, actualiza `src/utils/data_loader.py`.

## 4. Estructura del Código

### Archivos Principales

**`main.py`**
- Carga datos
- Construye entidades (`Farm`, `Slaughterhouse`, `Transport`)
- Ejecuta la simulación
- Muestra KPIs por consola

**`run_map.py`**
- Carga datos de granjas y escorxadors
- Muestra un mapa interactivo con Plotly

**`run_dashboard.py`**
- Ejecuta la simulación
- Genera gráficos:
  - Porcos entregados por día
  - Beneficio neto
  - Porcos/ruta
  - Distancia/ruta

### Módulos en `src/`

**`models/`**
- `Farm.py` – Representa una granja
- `Slaughterhouse.py` – Representa un escorxador
- `Transport.py` – Representa un vehículo de transporte

**`simulation/`**
- `Simulator.py` – Motor principal de la simulación
- `Router.py` – Lógica de enrutamiento

**`optimization/`**
- `Optimizer.py` – Optimización de rutas y costes

**`utils/`**
- `data_loader.py` – Carga de datos CSV/XLSX
- `BiologicalDataManager.py` – Gestión de datos biológicos
- `metrics.py` – Funciones auxiliares para cálculos

**`visualization/`**
- `map.py` – Visualización de mapas
- `dashboard.py` – Generación de KPIs y gráficos

## 5. Cómo Ejecutar la Simulación

### Ejecución Principal

```bash
cd ~/Repte_HackEPS/proyecto
source venv/bin/activate
python3 main.py
```

`main.py`:
- Carga los datos
- Crea las entidades
- Ejecuta varios días de simulación
- Muestra por consola:
  - Ingresos
  - Costes
  - Beneficio
  - Distancias
  - Entregas diarias

### Guardar Resultados en CSV

```python
events.to_csv("output/events.csv", index=False)
```

## 6. Visualización de Mapa

```bash
cd ~/Repte_HackEPS/proyecto
source venv/bin/activate
python3 run_map.py
```

Muestra:
- Mapa de granjas
- Mapa de escorxadors
- Información al pasar el ratón

## 7. Visualización de Dashboard (KPIs)

```bash
cd ~/Repte_HackEPS/proyecto
source venv/bin/activate
python3 run_dashboard.py
```

Incluye gráficos:
- Porcos entregados por día
- Beneficio neto
- Porcos medios por ruta
- Distancia media por ruta

## 8. Configuración y Extensiones

### Cambiar Días Simulados

Modifica la variable `DAYS_TO_SIMULATE` en:
- `main.py`
- `run_dashboard.py`

### Posibles Mejoras

- Guardar resultados en carpeta `output/`
- Crear frontend con Streamlit
- Añadir KPIs extra
- Implementar algoritmos de optimización avanzados
- Exportar reportes en PDF

## 9. Resumen Rápido

```bash
# Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar simulación
python3 main.py

# Visualizar mapa
python3 run_map.py

# Ver dashboard de KPIs
python3 run_dashboard.py
```

## 10. Solución de Problemas

**Error: "No module named venv"**
```bash
sudo apt install python3-venv
```

**Error: "No such file or directory: data/"**
Asegúrate de que los archivos CSV y XLSX estén en la carpeta `data/` y que el nombre sea exacto.

**Error: "ModuleNotFoundError"**
Verifica que el venv está activado y todas las dependencias se instalaron correctamente:
```bash
pip install -r requirements.txt
```

---

**Desarrollado para el Reto HackEPS**
**Daranuta Zop, Cristian**
