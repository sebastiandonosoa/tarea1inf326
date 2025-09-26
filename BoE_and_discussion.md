# Sobre Back of the Envelope

BoE, es una forma de estimar la carga que se presentará nuestro sistema en condiciones particulares. En nuestro caso, pensaremos en el peor caso, que corresponderá a cuando el sismo registrado es de gran magnitud, y a su vez, es cerca de una ciudad con muchos habitantes, donde nuestra suposición es que en estas ciudades existirán más usuarios esperando obtener información de la API. (No consideramos la publicación por parte del publisher, ya que esta será única siempre, pero los llamados a la API no). 

Una forma para determinar la carga, es determinar la cantidad de bits que la API envía por petición (nuestro caso son 65 carácteres, que si asumimos que 1 carácteres son 1 byte, tenemos 65 bytes). Además, si consideramos una sobre carga del 30% en lo que sería headers y "adornos" del mensaje, llegamos a una cantidad de aproximadamente 85 bytes por solicitud. Para finalizar, en nuestro caso en particular, si consideramos Santiago como la ciudad que más solicitudes hará, podemos estimar que se harán siete millones de solicitudes en el momento peak (población aproximada de Santiago).

# Justificación de la Arquitectura propuesta

Es posible proyectar la carga de notificaciones sobre los subscribers. Por ejemplo, si se conoce que en promedio se registran cierto número de sismos al día, basta con multiplicar esa cantidad por el número de subscribers definidos (cinco en este caso) para obtener una estimación inicial del volumen de notificaciones enviadas.
Posteriormente, se debe considerar la condición de interés de cada subscriber (radio de 500 km respecto del epicentro). Con la distribución geográfica de los sismos, puede estimarse qué proporción de los eventos resultan relevantes para cada ciudad y, en consecuencia, cuántas solicitudes adicionales al servicio HTTP se generarían en busca de información detallada.

De este modo, con parámetros relativamente simples —frecuencia de sismos, número de suscriptores, distancia de interés y tasa estimada de consultas HTTP se puede aproximar la carga promedio del sistema. Este análisis permite, además, justificar la arquitectura propuesta: el patrón publish-subscribe desacopla a los productores de eventos de los consumidores, lo que facilita la escalabilidad ante un incremento en la cantidad de sismos o de suscriptores. Por su parte, el modelo pull empleado mediante HTTP evita transmitir información innecesaria y concentra el procesamiento solo en los casos de interés, optimizando el uso de los recursos del sistema.

A continuación, se detallarán los trade-offs de nuestra propuesta arquitectónica basándonos en los siguientes parámetros:

## Eficiencia

Ventaja de nuestra propuesta: Como el publicador sólo envía mensajes precisos, evitamos que la línea de transmisión se sobrecargue por el tamaño de los mismos.

Desventaja de nuestra propuesta: Si bien la conexión entre publish-suscriber no se sobrecargará, llevaremos este problema eventualmente a la API (debido a la cantidad de peticiones que recibirá).

Este atributo si es de consideración en nuestro caso, ya que necesitamos que cada suscriptor pueda acceder a información rápidamente, evitando tragedias.

## Usabilidad

Ventaja de nuestra propuesta: Nuestra propuesta entrega una forma sencilla de publicar mensajes (se ingresa por consola y estos se comunican con la API para actualizar la "base de datos"), donde nuestro patrón publish-suscriber se hará cargo de informarle a todos los usuarios pendientes.

Desventaja de nuestra propuesta: Si la cantidad de eventos aumenta, el publicador se tendrá que enfrentar un problema de complejidad a la hora de elegir el tipo. (asumiendo que un "ser humano" enviará los mensajes, no un sensor de forma automática.)

Este atributo si es de consideración, ya que el publicador necesita informar a los suscriptores de forma rápida y eficiente.

## Escalabilidad

Ventaja de nuestra propuesta: Al utilizar el patrón publish-suscriber, es muy sencillo incorporar más suscriptores, ya que el publicador será siempre el mismo.

Desventaja de nuestra propuesta: Si la cantidad de suscriptores aumenta, es decir, diversas ciudades a través de Chile se incorporan al publisher, habrán muchos más mensajes que se enviarán que no serán de interés, provocando una sobrecarga de las conexiones (http, por ejemplo).

Este atributo si es de consideración, ya que por el contexto (Chile como país) es muy probable que muchas ciudades no necesiten la información, además, debido al filtro de 500 km, existirá información irrelevante constantemente.

## Consistencia

Ventaja de nuestra propuesta: Nuestra propuesta considera disponibilidad en caida del publisher, o de los suscriptores, asegurando que el mensaje de temblor (que puede ser importante según la magnitud) sea transmitido.

Desventaja de nuestra propuesta: Al almacenar los mensajes, si ocurre una caida catastrófica, y tenemos una gran cantidad de suscriptores, provocaremos que la memoria del publicador se sobre cargue (o bien, se sobrecargaran las lines de transmisión HTTP).

Este atributo si es de consideración, ya que saber la magnitud de un temblor permite a las personas determinar si corren peligro o no, por lo tanto, es necesario considerar este punto.

