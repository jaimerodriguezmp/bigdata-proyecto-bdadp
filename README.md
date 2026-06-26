# Proyecto BDaDP - Big Data y Procesamiento Distribuido

## Autores
Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino

## Descripcion
Proyecto completo para la asignatura de Big Data y Procesamiento Distribuido.
Consta de dos partes principales:

### 1. Sistema Distribuido para Reserva de Cine
Base de datos distribuida **Apache Cassandra** (3 nodos en Docker) con aplicacion de consola para gestionar reservas de cine.

**Funcionalidades:**
- Hacer reserva (insertar)
- Actualizar reserva (modificar asiento)
- Ver reservas activas por cliente
- Ver todas las reservas
- Cancelar reserva individual
- Cancelar multiples reservas a la vez

**Pruebas de Stress (5):**
1. Mismo cliente, misma peticion rapida (20 intentos simultaneos)
2. Clientes aleatorios con operaciones simultaneas
3. Ocupacion total de butacas por 2 clientes al mismo tiempo
4. Cancelaciones constantes y ocupacion de butacas
5. Cancelacion masiva de 1000 reservas

### 2. Analisis de Datos con Apache Hadoop
Dataset de 5000+ coches con analisis MapReduce (6 puntos):

1. **Precio promedio por marca**
2. **Precio promedio por tipo de combustible**
3. **Kilometraje promedio por marca**
4. **Numero de puertas por marca**
5. **Propietarios anteriores vs precio**
6. **Comparativa coches electricos vs gasolina por año**

---

## Requisitos

- **Docker** y **Docker Compose** (para Cassandra)
- **Python 3.8+**
- Paquetes Python: `pip install cassandra-driver`
- **Apache Hadoop** (opcional, para Hadoop Streaming)

## Estructura del proyecto

```
proyecto_final_bigdata/
├── cinema-reservation/
│   ├── docker-compose.yml        # 3 nodos Cassandra
│   ├── app.py                    # Aplicacion principal (CLI)
│   ├── db.py                     # Conexion y esquema Cassandra
│   ├── reservation.py            # Operaciones CRUD
│   ├── stress_tests.py           # Pruebas de stress (1-5)
│   ├── requirements.txt
│   ├── start_nodes.bat           # Levantar nodos Cassandra
│   ├── run_app.bat               # Ejecutar app de reservas
│   └── run_stress_tests.bat      # Ejecutar stress tests
├── hadoop-analysis/
│   ├── generate_data.py          # Generador de dataset de coches
│   ├── car_sales.csv             # Dataset generado (5000+ filas)
│   ├── analysis.py               # Analisis de datos (Python puro)
│   ├── mapper.py                 # Mapper para Hadoop Streaming
│   ├── reducer.py                # Reducer para Hadoop Streaming
│   ├── hadoop_runner.py          # Lanzador Hadoop desde Python
│   ├── run_analysis.bat          # Menu de analisis
│   ├── run_hadoop.bat            # Ejecutar con Hadoop
│   └── run_hadoop.sh             # Script alternativo para Hadoop
├── Projekt BDaDP.pdf             # Memoria del proyecto
└── README.md
```

## Como ejecutar

### 1. Levantar Cassandra (3 nodos)
```cmd
cd cinema-reservation
start_nodes.bat
```
Esperar ~60s hasta que los nodos esten listos.

### 2. Inicializar base de datos
```cmd
cd cinema-reservation
python app.py
```
Seleccionar opcion **8** para crear keyspace y tablas.

### 3. Aplicacion de reservas
```cmd
cd cinema-reservation
python app.py
```
Opciones del menu:
- **1** - Ver proyecciones disponibles
- **2** - Hacer una reserva
- **3** - Ver mis reservas (solo activas)
- **4** - Ver todas las reservas
- **5** - Actualizar una reserva
- **6** - Cancelar una reserva
- **7** - Cancelar multiples reservas
- **8** - Inicializar / resetear BD

### 4. Pruebas de stress
```cmd
cd cinema-reservation
run_stress_tests.bat
```

### 5. Analisis Hadoop (sin Hadoop)
```cmd
cd hadoop-analysis
python analysis.py           # Todos los analisis
python analysis.py --interactive  # Modo interactivo
```

### 6. Analisis Hadoop (con Hadoop Streaming)
```cmd
cd hadoop-analysis
run_hadoop.bat
```

## Esquema de base de datos

### Keyspace: `cinema_reservations`
```sql
CREATE TABLE screenings (
    movie_name text,
    show_time timestamp,
    screen_number int,
    total_seats int,
    screening_id UUID,
    PRIMARY KEY ((movie_name), show_time, screen_number)
);

CREATE TABLE reservations (
    movie_name text,
    show_time timestamp,
    screen_number int,
    seat_number int,
    customer_name text,
    status text,
    reservation_id UUID,
    created_at timestamp,
    PRIMARY KEY ((movie_name, show_time), screen_number, seat_number)
);
```

## Problemas encontrados
- Cassandra no soporta `SELECT DISTINCT` con columnas que no sean de la partition key (solucionado eliminando DISTINCT)
- Las queries que usan `ALLOW FILTERING` con columnas no indexadas pueden ser lentas en produccion
- La consistencia eventual de Cassandra requiere LWT para evitar condiciones de carrera
- Los stress tests demostraron que LWT (INSERT IF NOT EXISTS / UPDATE IF) resuelve correctamente la concurrencia
- Hadoop en Windows requiere configuracion adicional (WSL o Cygwin recomendado)
