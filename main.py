'''
Teoria de colas, utilizado para analizar sistemas con demanda y recursos limitados.

1. Proceso de Poisson: Los clientes llegan de manera aleatoria a una tasa constante promedio.
2. Distribucion exponencial: Describe el tiempo entre eventos en un proceso de Poisson. 
   En este ejercicio, el tiempo entre llegadas y el tiempo de servicio siguen esta distribucion.
3. Seleccion de caja: El cliente elige la caja con menos personas. Si hay empate, elige al azar.
4. Metricas:
   - Tiempo promedio en la cola: Tiempo que un cliente pasa esperando antes de ser atendido.
   - Numero promedio de clientes en la cola: Promedio de clientes esperando en cualquier momento.
   - Factor de utilizacion: Fraccion del tiempo que un cajero esta ocupado atendiendo clientes.

Si el numero promedio de clientes en la cola es 0.00, significa que, en promedio, no hay clientes esperando, 
posiblemente porque los cajeros atienden rapidamente en comparacion con la tasa de llegada.

El grado o factor de utilizacion de una caja (o de cualquier recurso en teoría de colas) representa la 
proporcion del tiempo que esa caja estuvo ocupada atendiendo a clientes, en relacion con el tiempo total 
de la simulacion. No es necesario que sumen 100%. Cada caja es un recurso independiente y su factor 
de utilizacion refleja cuanto estuvo ocupada en relacion con el tiempo total de la simulacion.
'''
import simpy
import random

# Parametros de la simulacion
CLIENTES_HORA = 20  # Tasa de llegada de clientes por hora
CAJAS_HORA = 5  # Tasa de servicio en cajas por hora
NUM_CAJAS = 5  # Numero de cajas en la sucursal
SIMULATION_TIME = 480  # Duracion de la simulacion en minutos

# Variables para recopilar estadisticas
tiempos_en_cola = []  # Tiempos que cada cliente paso en la cola
# Tiempos en que se liberaran las cajas
tiempos_liberacion_cajas = [0 for _ in range(NUM_CAJAS)]
# Tiempos totales de servicio por caja
tiempos_servicio = [0 for _ in range(NUM_CAJAS)]
longitud_cola = []  # Longitud de la cola en cada intervalo de tiempo


def cliente(env, caja, cliente_id, tiempo_llegada, indice_caja):
    """Funcion para simular el proceso de atencion al cliente por un cajero."""
    with caja.request() as req:
        yield req  # Esperar hasta que el cajero este disponible
        # Tiempo que tomara atender al cliente
        servicio_time = random.expovariate(1/CAJAS_HORA)
        # Actualizar el tiempo total de servicio del cajero
        tiempos_servicio[indice_caja] += servicio_time
        yield env.timeout(servicio_time)  # Simular el tiempo de servicio
        salida = env.now
        # Actualizar el tiempo de liberacion de la caja
        tiempos_liberacion_cajas[indice_caja] = salida
        print(
            f"Cliente {cliente_id} termino en la caja {caja.name} en {salida - tiempo_llegada:.2f} minutos")
        # Guardar el tiempo que el cliente paso en la cola
        tiempos_en_cola.append(salida - tiempo_llegada)


def llegada_clientes(env, cajas):
    """Funcion para simular la llegada de clientes al supermercado."""
    cliente_id = 0
    while True:
        # Tiempo hasta la llegada del siguiente cliente
        yield env.timeout(random.expovariate(1/CLIENTES_HORA))
        cliente_id += 1

        # Estimacion del tiempo de espera en cada caja
        tiempos_espera = []
        for i, caja in enumerate(cajas):
            tiempo_espera = tiempos_liberacion_cajas[i] + \
                (len(caja.queue) + 1) / CAJAS_HORA
            tiempos_espera.append(tiempo_espera)

        # Registrar la longitud de la cola en cada intervalo de tiempo
        total_clientes_cola = sum([len(caja.queue) for caja in cajas])
        longitud_cola.append(total_clientes_cola)

        # El cliente elige la caja con el tiempo de espera mas corto
        indice_caja_disponible = tiempos_espera.index(min(tiempos_espera))
        caja_disponible = cajas[indice_caja_disponible]
        print(
            f"Cliente {cliente_id} llego a la cola de caja {caja_disponible.name}")
        env.process(cliente(env, caja_disponible, cliente_id,
                    env.now, indice_caja_disponible))


# Inicializacion de la simulacion
env = simpy.Environment()
cajas = [simpy.Resource(env) for i in range(NUM_CAJAS)]  # Crear las cajas

for i, caja in enumerate(cajas):
    caja.name = f"Caja {i + 1}"  # Nombrar cada caja

env.process(llegada_clientes(env, cajas))
env.run(until=SIMULATION_TIME)  # Ejecutar la simulacion

# Calcular el tiempo promedio de un cliente en la cola
tiempo_promedio_en_cola = sum(tiempos_en_cola) / len(tiempos_en_cola)
print(f"Tiempo promedio en la cola: {tiempo_promedio_en_cola:.2f} minutos")

# Calcular y mostrar el numero de clientes en la cola en promedio
clientes_promedio_cola = sum(longitud_cola) / len(longitud_cola)
print(
    f"Numero de clientes en la cola en promedio: {clientes_promedio_cola:.2f}")

# Calcular y mostrar el grado o factor de utilizacion de cada cajero
for i, tiempo in enumerate(tiempos_servicio, 1):
    factor_utilizacion = tiempo / SIMULATION_TIME
    print(
        f"Grado o Factor de Utilizacion de la Caja {i}: {factor_utilizacion:.2f}")
