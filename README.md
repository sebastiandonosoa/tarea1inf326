# Tarea 1 INF326  Arquitectura de Software

## Integrantes

- Pablo Arellano, ROL: **202073**
- Sebastian Donoso, ROL: **202073**
- Cristóbal Pérez: ROL: **202073105-5**

## Instalación RabbitMQ en Ubuntu

Para comenzar, es necesario instalar lo necesario para ejecutar RabbitMQ. Para eso, RabbitMQ entrega un script bash que se debe ejecutar en el directorio en donde se ubica (Esta instalación está pensada para hacerla en una máquina con Ubuntu):

````
./rabbitmq.sh
````

Si no quiere ejecutarse, es necesario actualizar los permísos con chmod 755 en la consola.

## Instalación de paquetes de Python

Para evitar modificar los paquetes base, se utilizo un entorno Conda (se podría utilizar un entorno python también). Los paquetes (hasta ahora) son los siguientes y estan incluidos en el código (*receiver.py*):

````
pip install pika # Para RabbitMQ
pip install geopy # Para cálculo geodésico de coordenadas
pip install "fastapi[standard]" # Para servidor http
pip install requests # Para poder realizar "consultas" a la base de datos ficticia de temblores
pip install tabulate # Para crear la tabla en la línea de comandos
````

**Importante**: Si se presentan problemas con *fastapi*, puede ser debido a que se debe ingresar el root del script en el PATH de las variables de entorno, esto ocurre a veces si no se está ejecutando en entornos, como el de Conda.

## Ejecución

Se recomienda ejecutar main.py, el cuál contiene el servicio de fastAPI. Para eso, debemos ejecutar main.py como:

````
fastapi dev main.py
````

Después, se debe ejecutar el código de *receiver.py*, una vez por cada suscriptor que se quiera tener, en este caso serían 5. Cada vez que se ejecute el código de Pyhton, se preguntará lo siguiente:

1- **Latitud**: Se debe entregar la coordenada de latitud de la ciudad, se usará para calcular la distancia con respecto al terremoto que se publicará.

2- **Longitud**: Se debe entregar la coordenada de longitud de la ciudad, se usará para calcular la distancia con respecto al terremoto que se publicará.

3- **Nombre ciudad**: Se debe entregar el nombre de la ciudad que se está considerando en las coordenadas, esto solo afecta al nombre de la cola que tendrá asignado el suscriptor en *RabbitMQ*
 luego, ejecutamos receiver.py, que se mantiene a la espera de mensajes, y finalmente, ejecutamos publish.py, que se encarga de enviar un "anuncio" de terremoto falso.

En este caso, se ha probado con los siguientes datos: **Arica (coordenadas lat=-18.4746, long=-70.29792), Coquimbo (coordenadas lat=-29.95332, long=-71.33947), Valparaiso (coordenadas lat=-33.036, long=-71.62963), Concepción (coordenadas lat=-36.82699, long=-73.04977) y Punta Arenas (coordenadas lat=-53.16282, long=-70.90922)**.

Luego de dejar esperando cada instancia, se debe ejecutar el código de *publisher.py*, el cual también preguntará la latitud y longitud del terremoto que se quiere publicar y recibiran los suscriptores en el **exchange** "Servicio_Temblores".

Se prefirio utilizar 5 ejecuciones del mismo código de suscriptor, antes de 5 códigos distintos para cada ciudad que contengan la latitud y longitud que ya estan guardados antes de la ejecución, pues da más libertad para probar distintas ciudades, de igual forma que en el publisher, pese a que sea más trabajo el ingresar por cada uno los datos anteriormente mencionados.

 ````
python receiver.py
python publish.py
 ````
