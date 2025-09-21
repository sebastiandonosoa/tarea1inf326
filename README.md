# Tarea 1 INF326  Arquitectura de Software

## Instalación RabbitMQ en Ubuntu

Para comenzar, es necesario instalar lo necesario para ejecutar RabbitMQ. Para eso, RabbitMQ entrega un script bash que se debe ejecutar en el directorio en donde se ubica (Esta instalación está pensada para hacerla en una máquina con Ubuntu):

````
./rabbitmq.sh
````

Si no quiere ejecutarse, es necesario actualizar los permísos con chmod 755 en la consola.

## Instalación de paquetes de Python

Para evitar modificar los paquetes base, utilicé un entorno Conda (se podría utilizar un entorno python también). Los paquetes (hasta ahora) son los siguientes:

````
pip install pika # Para RabbitMQ
pip install geopy # Para cálculo geodésico de coordenadas
pip install "fastapi[standard]" # Para servidor http
pip install requests # Para poder realizar "consultas" a la base de datos ficticia de temblores
````

## Ejecución

Se recomienda ejecutar main.py, el cuál contiene el servicio de fastAPI. Para eso, debemos ejecutar main.py como:

````
fastapi dev main.py
````

 luego, ejecutamos receiver.py, que se mantiene a la espera de mensajes, y finalmente, ejecutamos publish.py, que se encarga de enviar un "anuncio" de terremoto falso.

 ````
python receiver.py
python publish.py
 ````