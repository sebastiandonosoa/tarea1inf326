# Tarea 1 INF326  Arquitectura de Software

## Integrantes

- Pablo Arellano, ROL: **202073034-2**
- Sebastian Donoso, ROL: **201921090-4**
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

Se recomienda ejecutar primero "main.py", el cuál contiene el servicio de fastAPI. Para eso, debemos ejecutar main.py como:

````
fastapi dev main.py
````

Después, se debe ejecutar el código de *receiver.py*, una vez por cada suscriptor que se quiera tener, en este caso serían 5. Cada vez que se ejecute el código de Python, se preguntará lo siguiente:

1- **Latitud**: Se debe entregar la coordenada de latitud de la ciudad, se usará para calcular la distancia con respecto al terremoto que se publicará.

2- **Longitud**: Se debe entregar la coordenada de longitud de la ciudad, se usará para calcular la distancia con respecto al terremoto que se publicará.

3- **Nombre ciudad**: Se debe entregar el nombre de la ciudad que se está considerando en las coordenadas, esto solo afecta al nombre de la cola que tendrá asignado el suscriptor en *RabbitMQ*.

En este caso, se ha probado con los siguientes datos: **Arica (coordenadas lat=-18.4746, long=-70.29792), Coquimbo (coordenadas lat=-29.95332, long=-71.33947), Valparaiso (coordenadas lat=-33.036, long=-71.62963), Concepción (coordenadas lat=-36.82699, long=-73.04977) y Punta Arenas (coordenadas lat=-53.16282, long=-70.90922)**.

Luego de dejar esperando cada instancia, se debe ejecutar el código de *publisher.py*, el cual preguntará:

1. **Latitud**: Coordenada de la latitud en donde se ha producido el sismo.

2. **Longitud**: Coordenada de la longitud en donde se ha producido el sismo.

3. **Localidad**: Ubicación (aproximada) de donde se ha producido el sismo.

4. **Magnitud**: Magnitud en escala de Ritcher del sismo.

5. **Profundidad_Sismo**: Profundidad (ya en kilómetros) del sismo. NO INGRESAR UNIDAD.

Al publicar un nuevo sismo, la información detallada se incorporará a la lista de sismos existentes en la API, y se enviará un aviso a los suscriptores que sólo incorporará la latitud, longitud y timestamp, para realizar el filtrado correspondiente. Posteriormente, los suscriptores si están interesados por el sismo, podrán consultar a la API. Se recibirán los suscriptores en el **exchange** "Servicio_Temblores".


````
python receiver.py
python publish.py
 ````

## Consideraciones

1. Se prefirio utilizar 5 ejecuciones del mismo código de suscriptor, antes de 5 códigos distintos para cada ciudad que contengan la latitud y longitud que ya estan guardados antes de la ejecución, pues da más libertad para probar distintas ciudades, de igual forma que en el publisher, pese a que sea más trabajo el ingresar por cada uno los datos anteriormente mencionados.

2. Se debe considerar que en la API, solo están guardados los siguientes temblores en formato JSON:

 ````
earthquakes = [
    {"magnitude": 7.8, "location": "23 km al SE de Valparaíso", "date": "2024-03-15 18:29:13", "depth": "135 km", "latitud": -33.15, "longitud": -71.40},
    {"magnitude": 6.2, "location": "129 km al NE de Santiago", "date": "2024-02-28 18:02:59", "depth": "12 km", "latitud": -32.50, "longitud": -69.80},
    {"magnitude": 8.1, "location": "81 km al NO de Antofagasta", "date": "2024-01-10 16:34:34", "depth": "45 km", "latitud": -23.20, "longitud": -70.80},
    {"magnitude": 5.9, "location": "20 km al N de Concepción", "date": "2024-01-05 14:37:37", "depth": "49 km", "latitud": -36.60, "longitud": -72.95},
    {"magnitude": 7.3, "location": "68 km al S de Iquique", "date": "2023-12-20 14:31:27", "depth": "28 km", "latitud": -20.80, "longitud": -70.20},
    {"magnitude": 6.7, "location": "54 km al E de La Serena", "date": "2023-11-18 13:50:44", "depth": "40 km", "latitud": -29.90, "longitud": -70.20},
]
 ````
 Estos son la base, pero al publicar nuevos sismos la lista se irá actualizando.

3. Se considero que en vez de mensajes sólo en formato *String* como se mostró en la clase, era mejor que los mensajes fueran en formato *JSON*, que se utiliza varias veces en estos contextos y es más eficiente al querer obtener ciertos datos.

4. Cada vez que se ejecuta el publisher y se le dan los datos de un terremoto, se guarda como fecha el momento actual, esta quedara con un formato de tiempo universal, es decir, en **UTC=0**
