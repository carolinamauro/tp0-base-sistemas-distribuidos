# TP0: Docker + Comunicaciones + Concurrencia

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.


### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

#### Solución

Se mantuvo la estructura de comunicación entre el servidor y las agencias (clientes) igual que en el ejercicio anterior.

Se agrega la variable de entorno `CLIENTS_AMOUNT` en el archivo `docker-compose-dev.yaml` para que el servidor sepa cuantas agencias (clientes) se van a conectar.

Para que el servidor realice el sorteo, se agrego el campo `finised_agencies` donde el servidor aumenta su valor cada vez que una agencia le notifica que finalizó el envío de apuestas. Cuando este campo es igual a la cantidad de agencias (clients_amount) se realiza el sorteo y se envia a cada agencia la lista de ganadores correspondiente.

Flujo de comunicación:
1. El servidor recibe una nueva conexión y la handlea en la funcion `__handle_agency_connection`. 
2. El servidor pasa a recibir todas las apuestas de la agencia en la función `__receive_bets`.
3. Cuando la agencia finaliza el envío de apuestas, envía el mensaje al servidor MESSAGE_TYPE_END_OF_CHUNKS
4. El servidor aumenta en 1 el campo `finised_agencies`. Una vez se termina el loop para el handleo de la agencia, se fija si todas las agencias finalizaron el envío de apuestas (finised_agencies == clients_amount). Si es así, realiza el sorteo y envía a cada agencia la lista de ganadores correspondiente.
5. La agencia recibe la lista de ganadores y la imprime por log.