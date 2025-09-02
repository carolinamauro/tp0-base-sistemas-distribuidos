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
- Se modificó el cliente para que envíe las apuestas en lotes (_batches_) según la configuración establecida en `config.yaml` bajo la clave `batch: maxAmount`. La cantidad máxima de apuestas por lote se ajustó para no exceder los 8kB. 
- Se agregó la funcionalidad en el servidor para procesar múltiples apuestas recibidas en un solo lote.
- Se implementó la lógica para validar todas las apuestas en el lote y responder con éxito

Se sumaron los mensajes MESSAGE_TYPE_BATCH y MESSAGE_TYPE_LAST_CHUNK. EL servidor recibe el batch y procesa todas las apuestas. EN caso de exito, responde con un ACK. EN caso de error, logea el error. Cuando el cliente envia el ultimo batch, envia el mensaje MESSAGE_TYPE_LAST_CHUNK y el servidor responde con un ACK y cierra la conexion.