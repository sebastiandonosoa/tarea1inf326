import pika
import json
from typing import Optional
from datetime import datetime

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
    
    def publish_earthquake_data(self, latitud: float, longitud: float):
        """
        Acá el profe en clases mostró una forma diferente. Decidí utilizar el formato JSON ya que es lo típico según google... (además de ser facil de usar).
        """
        
        if not self.channel:
            raise RuntimeError("No te encuentras conectado. Utiliza connect()")

        dato_terremoto = {
            "event_type": "terremoto",
            "coordenadas": {
                "latitud": latitud,
                "longitud": longitud
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        message = json.dumps(dato_terremoto)
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key="", # Cambiar a futuro ? ...
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

    publisher = Publisher(exchange_name="Servicio_Temblores")
    publisher.connect()

    latitud = float(input("Ingrese la latitud en que ocurrio el terremoto"))
    longitud = float(input("Ingrese la longitud en que ocurrio el terremoto"))

    publisher.publish_earthquake_data(  ## Coordenadas latitud =-33.15, longitud = -71.40, corresponden al Estadio Nacional, Santiago de Chile.
        latitud,
        longitud,
    )
    publisher.close()


