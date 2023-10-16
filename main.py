import simpy
import random

# Parámetros de la simulación
CLIENTES_HORA = 20  # Tasa de llegada de clientes por hora
CAJAS_HORA = 5  # Tasa de servicio en cajas por hora
NUM_CAJAS = 5  # Número de cajas en la sucursal
SIMULATION_TIME = 480  # Duración de la simulación en minutos 

# Variables para recopilar estadísticas
tiempos_en_cola = []
tiempos_liberacion_cajas = [0 for _ in range(NUM_CAJAS)]  # Tiempos en que se liberarán las cajas
tiempos_servicio = [0 for _ in range(NUM_CAJAS)]  # Tiempos totales de servicio por caja

def cliente(env, caja, cliente_id, tiempo_llegada, indice_caja):
    with caja.request() as req:
        yield req
        servicio_time = random.expovariate(1/CAJAS_HORA)
        tiempos_servicio[indice_caja] += servicio_time  # Actualizar el tiempo total de servicio del cajero
        yield env.timeout(servicio_time)
        salida = env.now
        tiempos_liberacion_cajas[indice_caja] = salida  # Actualizar el tiempo de liberación de la caja
        print(f"Cliente {cliente_id} terminó en la caja {caja.name} en {salida - tiempo_llegada:.2f} minutos")
        tiempos_en_cola.append(salida - tiempo_llegada)

def llegada_clientes(env, cajas):
    cliente_id = 0
    while True:
        yield env.timeout(random.expovariate(1/CLIENTES_HORA))
        cliente_id += 1

        # Estimación del tiempo de espera en cada caja
        tiempos_espera = []
        for i, caja in enumerate(cajas):
            tiempo_espera = tiempos_liberacion_cajas[i] + (len(caja.queue) + 1) / CAJAS_HORA
            tiempos_espera.append(tiempo_espera)

        # El cliente elige la caja con el tiempo de espera más corto
        indice_caja_disponible = tiempos_espera.index(min(tiempos_espera))
        caja_disponible = cajas[indice_caja_disponible]

        print(f"Cliente {cliente_id} llegó a la cola de caja {caja_disponible.name}")
        env.process(cliente(env, caja_disponible, cliente_id, env.now, indice_caja_disponible))

# Inicialización de la simulación
env = simpy.Environment()
cajas = [simpy.Resource(env) for i in range(NUM_CAJAS)]

for i, caja in enumerate(cajas):
    caja.name = f"Caja {i + 1}"

env.process(llegada_clientes(env, cajas))
env.run(until=SIMULATION_TIME)

# Calcular el tiempo promedio de un cliente en la cola
tiempo_promedio_en_cola = sum(tiempos_en_cola) / len(tiempos_en_cola)
print(f"Tiempo promedio en la cola: {tiempo_promedio_en_cola:.2f} minutos")

# Calcular y mostrar el grado o factor de utilización de cada cajero
for i, tiempo in enumerate(tiempos_servicio, 1):
    factor_utilizacion = tiempo / SIMULATION_TIME
    print(f"Grado o Factor de Utilización de la Caja {i}: {factor_utilizacion:.2f}")
