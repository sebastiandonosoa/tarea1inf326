import pika
import json
import requests

from typing import Callable, Optional
from geopy.distance import geodesic

# Pip install pika
# pip install geopy
# pip install "fastapi[standard]"
# pip install requests


class Suscribers:
    def __init__(self, host: str = "localhost", exchange_name: str = "message_ex", latitud: Optional[float] = None, longitud: Optional[float] = None):
        self.host = host
        self.exchange_name = exchange_name
        self.latitud = latitud
        self.longitud = longitud
        self.connection = None
        self.channel = None
        self.queue_name = None
    
    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type = "fanout")

        result = self.channel.queue_declare(queue="", exclusive = True)
        self.queue_name = result.method.queue

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
        #print(body.decode())
        #distance = self.calculate_geodesic_distance(40.7128,-74.0060,34.0522,-118.2437)
        try:
            dato_terremoto = json.loads(body.decode())

            json_lat = dato_terremoto["coordenadas"]["latitud"]
            json_lon = dato_terremoto["coordenadas"]["longitud"]

            # Para facilitar las pruebas, evitaré hacer comprobaciones de seguridad (i.e. ver que tenga valores los atributos de latitud y longitud de la clase.)
            distance = self.calculate_geodesic_distance(self.latitud, self.longitud, json_lat, json_lon)
            if distance <= 500:
                print(f"La distancia entre yo (suscriptor) y la ubicación del terremoto es de {distance:.2f} KM")
                print("soy válido\n")
                self.consultar_datos()
            else:
                print(f"La distancia entre yo (suscriptor) y la ubicación del terremoto es de {distance:.2f} KM")
                print("No soy válido")

            
        
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error {e}")

        
    
    def calculate_geodesic_distance(self, lat1, lon1, lat2, lon2):
        point1 = (lat1, lon1)
        point2= (lat2, lon2)
        distance = geodesic(point1, point2).kilometers
        return distance
    
    # La siguiente función tiene como propósito consultar los datos de fastAPI para una posterior implementación utilizando los criterios de la tarea.
    def consultar_datos(self, api_url: str = "http://localhost:8000/api/terremotos"):
        try:
            response = requests.get(api_url)
            response.raise_for_status()

            data = response.json()
            terremotos = data.get("terremotos", [])

            for terremoto in terremotos:
                print(f"- {terremoto['location']}: Magnitud {terremoto['magnitude']}")

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
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_consuming()
        self.close()

if __name__ == "__main__":
    with  Suscribers(latitud=-33.04927422413275, longitud=-71.58683350800092) as suscriber:
        suscriber.subscribe()

