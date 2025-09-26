import pika
import json
from typing import Optional
from datetime import datetime
from tabulate import tabulate
import requests

class Publisher:

    def __init__(self, host: str = "localhost", exchange_name: Optional[str] = "message_ex", exchange_type: str = "fanout"):
        self.host = host
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
    
    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type = self.exchange_type)
    
    def publish_message(self, message: str, routing_key: str = ""):
        if not self.channel:
            raise RuntimeError("No te encuentras conectado. Utiliza connect().")
        
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,
            body=message
        )
        print(f"Mensaje enviado!")
    
    def publish_earthquake_data(self, latitud: float, longitud: float, timestamp: None):
        """
        Método encargado de enviar el mensaje de terremoto detectado.
        """
        if not self.channel:
            raise RuntimeError("No te encuentras conectado. Utiliza connect()")

        dato_terremoto = {
            "event_type": "terremoto.detectado",
            "coordenadas": {
                "latitud": latitud,
                "longitud": longitud,
            },
            "timestamp": timestamp
        }

        message = json.dumps(dato_terremoto)
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key="", 
            body=message
        )
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":

    earthquakes = [
    ["23 km al SE de Valparaíso", 7.8, "2024-03-15 18:29:13", "135 km", -33.15, -71.40],
    ["129 km al NE de Santiago", 6.2, "2024-02-28 18:02:59", "12 km", -32.50, -69.80],
    ["81 km al NO de Antofagasta", 8.1, "2024-01-10 16:34:34", "45 km", -23.20, -70.80],
    ["20 km al N de Concepción", 5.9, "2024-01-05 14:37:37", "49 km", -36.60, -72.95],
    ["68 km al S de Iquique", 7.3, "2023-12-20 14:31:27", "28 km", -20.80, -70.20],
    ["54 km al E de La Serena", 6.7, "2023-11-18 13:50:44", "40 km", -29.90, -70.20]
]

    print("\nPara fines de simulación, a continuación se entregará una base de datos ficticia ubicada en la API, para que puedas guiarte.")
    print(tabulate(earthquakes, headers=["Locación", "Magnitud", "Fecha", "Profundidad","Latitud","Longitud",], tablefmt="fancy_grid"))

    publisher = Publisher(exchange_name="Servicio_Temblores")
    publisher.connect()

    # while
    latitud = float(input("Ingrese la latitud en que ocurrio el terremoto: "))
    longitud = float(input("Ingrese la longitud en que ocurrio el terremoto: "))
    localidad = str(input("Ingrese la locación ocurrida del sismo: "))
    magnitud = float(input("Ingrese magnitud del sismo: "))
    profundidad_sismo = float(input("Ingrese la profundidad registrada del sismo (en KM): "))
    timestamp = datetime.utcnow().isoformat()
    terremoto_data = {
        "magnitude": magnitud,
        "location": localidad,
        "date": timestamp,
        "depth": f"{profundidad_sismo} km",
        "latitud": latitud,
        "longitud": longitud
    }

    try:
        api_url = "http://localhost:8000/api/terremotos"
        response = requests.post(api_url, json=terremoto_data)
        print(f"API respuesta: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error conectando a la API: {e}")

    publisher.publish_earthquake_data(  
        latitud,
        longitud,
        timestamp
    )
    publisher.close()


