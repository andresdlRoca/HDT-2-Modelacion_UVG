import simpy
import random

# Parámetros de la simulación
CLIENTES_HORA = 20  # Tasa de llegada de clientes por hora
CAJAS_HORA = 5  # Tasa de servicio en cajas por hora
NUM_CAJAS = 5  # Número de cajas en la sucursal
SIMULATION_TIME = 480  # Duración de la simulación en minutos 

# Variables para recopilar estadísticas
tiempos_en_cola = []

def cliente(env, caja, cliente_id, tiempo_llegada):
    with caja.request() as req:
        yield req
        servicio_time = random.expovariate(1/CAJAS_HORA)
        yield env.timeout(servicio_time)
        salida = env.now
        print(f"Cliente {cliente_id} terminó en la caja {caja.name} en {salida - tiempo_llegada:.2f} minutos")
        tiempos_en_cola.append(salida - tiempo_llegada)

def llegada_clientes(env, cajas):
    cliente_id = 0
    while True:
        yield env.timeout(random.expovariate(1/CLIENTES_HORA))
        cliente_id += 1
        caja_disponible = min(cajas, key=lambda c: len(c.queue))
        print(f"Cliente {cliente_id} llegó a la cola de caja {caja_disponible.name}")
        env.process(cliente(env, caja_disponible, cliente_id, env.now))

# Inicialización de la simulación
env = simpy.Environment()
cajas = [simpy.Resource(env) for i in range(NUM_CAJAS)]

for i, caja in enumerate(cajas):
    caja.name = f"Caja {i + 1}"

env.process(llegada_clientes(env, cajas))
env.run(until=SIMULATION_TIME)

# Calcular el tiempo promedio de un cliente en la cola
# print(tiempos_en_cola)
tiempo_promedio_en_cola = sum(tiempos_en_cola) / len(tiempos_en_cola)
print(f"Tiempo promedio en la cola: {tiempo_promedio_en_cola:.2f} minutos")
