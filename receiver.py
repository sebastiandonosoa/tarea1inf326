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
        #self.queue_name = result.method.queue

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

            # Para facilitar las pruebas, evitaré hacer comprobaciones de seguridad (i.e. ver que tenga valores los atributos de latitud y longitud de la clase.)
            distance = self.calculate_geodesic_distance(self.latitud, self.longitud, json_lat, json_lon)
            if distance <= 500:
                print(f"La distancia entre yo (suscriptor) y la ubicación del terremoto es de {distance:.2f} KM")
                print("soy válido\n")
                self.consultar_datos(latitud=json_lat, longitud = json_lon, timestamp = json_tim )
            else:
                print(f"La distancia entre yo (suscriptor) y la ubicación del terremoto es de {distance:.2f} KM")
                print("No estoy a menos 500 kilometros.")

            
        
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error {e}")

        
    
    def calculate_geodesic_distance(self, lat1, lon1, lat2, lon2):
        point1 = (lat1, lon1)
        point2= (lat2, lon2)
        distance = geodesic(point1, point2).kilometers
        return distance
    
    # La siguiente función tiene como propósito consultar los datos de fastAPI para una posterior implementación utilizando los criterios de la tarea.
    def consultar_datos(self, api_url: str = "http://localhost:8000/api/terremotos", latitud = None, longitud = None, timestamp = None):
        try:
            params = {}
            if latitud is not None:
                params['latitud'] = latitud
            if longitud is not None:
                params['longitud'] = longitud
            
            # Falta ver tema timestamp

            response = requests.get(api_url, params=params)
            response.raise_for_status()

            data = response.json()
            terremotos = data.get("terremotos", [])

            
            tabla = []
            for terremoto in terremotos:
                #percibido = True

                #if latitud is not None and terremoto.get("latitud") != latitud:
                    #percibido = False
                #if longitud is not None and terremoto.get("longitud") != longitud:
                    #percibido = False

                #if percibido or (latitud is None and longitud is None):
                fila = [
                    terremoto.get("location", "N/A"),
                    terremoto.get("magnitude", "N/A"),
                    terremoto.get("depth", "N/A"),
                    terremoto.get("date", "N/A"),
                    terremoto.get("latitud", "N/A"),
                    terremoto.get("longitud", "N/A")
                ]

                    #fila = [f"*** {campo} ***" for campo in fila]

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
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_consuming()
        self.close()

if __name__ == "__main__":
    latitud = float(input("Ingrese la latitud de su ubicacion: "))
    longitud = float(input("Ingrese la longitud de su ubicacion: "))
    queue_name = input("Ingrese la ciudad de su ubicación, que será el nombre de la cola: ")

    with  Suscribers(latitud=latitud, longitud=longitud, exchange_name="Servicio_Temblores", queue_name=queue_name) as suscriber:
        suscriber.subscribe()


