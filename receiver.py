import pika
import json
import requests

from typing import Callable, Optional
from geopy.distance import geodesic
from tabulate import tabulate

# Pip install pika
# pip install geopy
# pip install "fastapi[standard]"
# pip install requests
# pip install tabulate


class Suscribers:
    def __init__(self, host: str = "localhost", exchange_name: Optional[str] = "message_ex", queue_name: Optional[str] = None, latitud: Optional[float] = None, longitud: Optional[float] = None):
        self.host = host
        self.exchange_name = exchange_name
        self.latitud = latitud
        self.longitud = longitud
        self.connection = None
        self.channel = None
        self.queue_name = queue_name
    
    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type = "fanout")

        result = self.channel.queue_declare(queue= self.queue_name, exclusive = True)

        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name)
    
    def subscribe(self, callback: Optional[Callable] = None):
        if not self.channel or not self.queue_name:
            raise Exception("Antes de suscribirte debes llamar a connect()")
        
        if callback is None:
            callback = self._default_callback

        print("Esperando mensajes...")
        self.channel.basic_consume(
            queue = self.queue_name,
            on_message_callback=callback,
            auto_ack=True
        )

        self.channel.start_consuming()
    
    def _default_callback(self, ch, method, properties, body):
        try:
            dato_terremoto = json.loads(body.decode())

            json_lat = dato_terremoto["coordenadas"]["latitud"]
            json_lon = dato_terremoto["coordenadas"]["longitud"]
            json_tim = dato_terremoto["timestamp"]

            distance = self.calculate_geodesic_distance(self.latitud, self.longitud, json_lat, json_lon)
            if distance <= 500:
                print(f"\nLa distancia entre yo {queue_name} y la ubicación del terremoto es de {distance:.2f} KM. Consultando datos...")
                self.consultar_datos(latitud=json_lat, longitud = json_lon, timestamp = json_tim )
            else:
                print(f"\nLa distancia entre {queue_name} y la ubicación del terremoto es de {distance:.2f} KM. No es necesario consultar datos.")
                

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error {e}")

        
    
    def calculate_geodesic_distance(self, lat1, lon1, lat2, lon2):
        point1 = (lat1, lon1)
        point2= (lat2, lon2)
        distance = geodesic(point1, point2).kilometers
        return distance
    
    
    def consultar_datos(self, api_url: str = "http://localhost:8000/api/terremotos", latitud = None, longitud = None, timestamp = None):
        try:
            params = {}
            if latitud is not None:
                params['latitud'] = latitud
            if longitud is not None:
                params['longitud'] = longitud
            if timestamp is not None:
                params['timestamp'] = timestamp
            
            response = requests.get(api_url, params=params)
            response.raise_for_status()

            data = response.json()
            terremotos = data.get("terremotos", [])

            tabla = []
            for terremoto in terremotos:
                fila = [
                    terremoto.get("location", "N/A"),
                    terremoto.get("magnitude", "N/A"),
                    terremoto.get("depth", "N/A"),
                    terremoto.get("date", "N/A"),
                    terremoto.get("latitud", "N/A"),
                    terremoto.get("longitud", "N/A")
                ]
                tabla.append(fila) 

            print(tabulate(tabla, headers=["Ubicación", "Magnitud", "Profundidad", "Fecha","Latitud","Longitud",], tablefmt="fancy_grid"))

            return terremotos

        except requests.exceptions.RequestException as e:
            print(f"Error al consultar la api {e}")
            return None
        except Exception as e:
            print(f"Error {e}")
            return None

    
    def stop_consuming(self):
        if self.channel:
            self.channel.stop_consuming()
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
    
    # Los siguientes dos métodos, cumplen la función de facilitar la ejecución de los suscriptores usando "with Suscribers(...)"
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_consuming()
        self.close()
    
    ##################################

if __name__ == "__main__":

    print("\nA continuación, se presenta una serie de coordenadas de ciudades Chilenas importantes. Úsalas para facilitar la prueba.")
    coordenadas_tentativas = [
    ["Valparaíso", -33.0458, -71.6197],
    ["La Serena", -29.9045, -71.2489],
    ["Santiago de Chile", -33.4489, -70.6693],
    ["Concepción", -36.8201, -73.0443],
    ["Antofagasta", -23.6524, -70.3954],
    ["Iquique", -20.2133, -70.1503],
    ["Temuco", -38.7359, -72.5904],
    ["Puerto Montt", -41.4657, -72.9429],
    ["Viña del Mar", -33.0246, -71.5518],
    ["Arica", -18.4746, -70.2979]
    ]
    print(tabulate(coordenadas_tentativas, headers=["Ubicación", "Latitud", "Longitud"], tablefmt="fancy_grid"))

    latitud = float(input("Ingrese la latitud de su ubicacion: "))
    longitud = float(input("Ingrese la longitud de su ubicacion: "))
    queue_name = input("Ingrese la ciudad de su ubicación, que será el nombre de la cola: ")

    with  Suscribers(latitud=latitud, longitud=longitud, exchange_name="Servicio_Temblores", queue_name=queue_name) as suscriber:
        suscriber.subscribe()


