# TP0: Docker + Comunicaciones + Concurrencia

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.


### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

#### Solución

Se modificó el cliente para que envíe las apuestas en lotes (_chunks_) según la configuración establecida en `config.yaml` bajo la clave `batch: maxAmount`. La cantidad máxima de apuestas por lote se ajustó para no exceder los 8kB. El clienta intenta conectarse al servidor y enviar los lotes de apuestas. 
- En caso de error de conexión, el cliente reintenta la conexión hasta 3 veces antes de abortar. 
- Si logra conectarse exitosamente, realiza el envio de los lotes de apuestas. Lee la maxima cantidad que puede enviar por lote respetando el limite de 8kB y envia el chunk. Espera la respuesta del servidor (ack) antes de enviar el siguiente chunk. Una vez enviado el ultimo chunk, envia un mensaje MESSAGE_TYPE_END_OF_CHUNKS para indicar que no hay mas chunks a enviar. Una vez enviado el ultimo chunk, cierra la conexion.

Desde el laso del servidor, se implementó la funcionalidad para recibir y procesar múltiples apuestas en un solo lote. El servidor sabe responder correctamente a los mensajes de tipo `MESSAGE_TYPE_BATCH` y `MESSAGE_TYPE_LAST_CHUNK`. Los procesa de la siguiente manera:
- Cuando recibe un mensaje de tipo `MESSAGE_TYPE_BATCH`, procesa todas las apuestas del chunk, guardandolas con la funcion `store_bet`. 
  --> Si todas las apuestas son procesadas correctamente, le envia al cliente el mensaje `ACK_OK` y sigue esperando mas mensajes del cliente.
  --> Si alguna apuesta falla, le envia al cliente el mensaje `PROCESS_CHUNK_ERROR`, loguea el error y cierra la conexion del cliente. Esto se decidio para evitar que el cliente siga enviando mas chunks si ya hubo un error en el procesamiento de sus apuestas es porque no las envio correctamente.

- Cuando recibe un mensaje de tipo `MESSAGE_TYPE_LAST_CHUNK`, significa que ya recibió todos los chunks del cliente. Por lo que loguea eun mensaje indicando que el cliente ya envio todos sus chunks, cierra la conexion y sigue esperando nuevos clientes.

El servidor responde con éxito solamente si todas las apuestas del lote fueron procesadas correctamente. En caso de detectar un error con alguna de las apuestas, responde con un código de error y cierra la conexión del cliente.