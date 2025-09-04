# TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un esqueleto básico de cliente/servidor, en donde todas las dependencias del mismo se encuentran encapsuladas en containers. Los alumnos deberán resolver una guía de ejercicios incrementales, teniendo en cuenta las condiciones de entrega descritas al final de este enunciado.

 El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers, en este caso utilizando [Docker Compose](https://docs.docker.com/compose/).

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que incluye distintos comandos en forma de targets. Los targets se ejecutan mediante la invocación de:  **make \<target\>**. Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de depuración.

Los targets disponibles son:

| target  | accion  |
|---|---|
|  `docker-compose-up`  | Inicializa el ambiente de desarrollo. Construye las imágenes del cliente y el servidor, inicializa los recursos a utilizar (volúmenes, redes, etc) e inicia los propios containers. |
| `docker-compose-down`  | Ejecuta `docker-compose stop` para detener los containers asociados al compose y luego  `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene de versiones de desarrollo y recursos sin liberar. |
|  `docker-compose-logs` | Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose. |
| `docker-image`  | Construye las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para probar nuevos cambios en las imágenes antes de arrancar el proyecto. |
| `build` | Compila la aplicación cliente para ejecución en el _host_ en lugar de en Docker. De este modo la compilación es mucho más veloz, pero requiere contar con todo el entorno de Golang y Python instalados en la máquina _host_. |

### Servidor

Se trata de un "echo server", en donde los mensajes recibidos por el cliente se responden inmediatamente y sin alterar. 

Se ejecutan en bucle las siguientes etapas:

1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor retorna al paso 1.


### Cliente
 se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma:
 
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
4. Servidor responde al mensaje.
5. Servidor desconecta al cliente.
6. Cliente verifica si aún debe enviar un mensaje y si es así, vuelve al paso 2.

### Ejemplo

Al ejecutar el comando `make docker-compose-up`  y luego  `make docker-compose-logs`, se observan los siguientes logs:

```
client1  | 2024-08-21 22:11:15 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: DEBUG
client1  | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:14 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2024-08-21 22:11:14 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
client1  | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°5
client1  | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°5
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:40 INFO     action: loop_finished | result: success | client_id: 1
client1 exited with code 0
```

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:

Para generar un archivo de Docker Compose, se creó el script `generar-compose.sh` en la raíz del proyecto. El mismo recibe dos parámetros: el nombre del archivo de salida y la cantidad de clientes a generar. 

Ejemplo de uso:

`./generar-compose.sh docker-compose-dev.yaml 5`

El archivo `generar-compose.sh` chequea que se envien los dos parametros esperados y en caso contrario muestra un mensaje de ayuda. Utiliza un subscript de Python llamado `generar-compose.py` para generar el archivo de Docker Compose. El script utiliza templetes para definir las secciones comunes del compose y luego itera para agregar la cantidad de clientes solicitada. 

### Ejercicio N°2:

Partiendo del ejercicio anterior, se modificó el script `generar-compose.sh` para incluir volúmenes en las definiciones de cliente y servidor.

Se modifico el archivo docker-compose.py agregando los siguientes volúmenes:
Server
```yaml
    volumes:
      - ./server/config.yaml:/config.yaml
```
Client
```yaml
    volumes:
      - ./client/config.yaml:/config.yaml
```
Al sumar los volumes para los archivos de configuración del cliente y del servidor los mismos pueden ser editados en el host y reflejarse en los containers sin necesidad de reconstruir las imágenes. Los archivos `config.yaml` y `config.ini` son inyectados en los containers en la ruta `/config.yaml` y `/config.ini` respectivamente.

### Ejercicio N°3:

Se creo el script `validar-echo-server.sh` el cual obtiene del archivo `config.ini` las varibles `SERVER_IP` y `SERVER_PORT`. Luego se ejecuta el siguiente comando:
`server_response=$(docker run --rm --network tp0_testing_net busybox sh -c "echo $message | nc $SERVER_IP $SERVER_PORT")`
donde
1. Se corre la imagen de docker busybox (una distribucion de linux liviana que incluye el comando de netcat) en la red tp0_testing_net, la misma en la que se encontrará el servidor corriendo. De esta manera, ambos contenedores pueden comunicarse  sin la necesidad de exponer un puerto.
2. Con `sh -c` se abre una terminal dentro del contenedor y se ejecuta el comando `echo $message`, que imprime el mensaje "Hola,Mundo!". Ese mensaje se redirige mediante el pipe (|) al comando netcat (nc), que lo envía al servidor en la IP y el puerto especificados.
3. La espuesta se guarda en la variable  `server_response` y luego se lo compara con el mensaje original a ver si el servidor esta respondiendo correctammente.
  
  - En caso de que la validación sea exitosa se imprime: `action: test_echo_server | result: success`, de lo contrario se imprime:`action: test_echo_server | result: fail`.

### Ejercicio N°4:

- En el cliente, se agregó un canal para escuchar la señal SIGTERM y se implementó la función `handleSigtermSignal` para cerrar la conexión del cliente de manera adecuada.
```
	signalChannel := make(chan os.Signal, 2)
    signal.Notify(signalChannel, syscall.SIGTERM)
    go func() {
        <-signalChannel
        c.handleSigtermSignal()
    }()
```
Además, se implementó un mecanismo de reintentos para la conexión al servidor en caso de que falle. Se intenta reconectar hasta 3 veces con un intervalo definido por la variable de entorno `LoopPeriod` entre cada intento. Si no se puede establecer la conexión después de los reintentos, se loguea un error y se cierra el cliente.
- En el servidor, se agregó un manejador de señales para SIGTERM que cierra todas las conexiones activas de los clientes y el socket del servidor antes de salir. Se implementó la función `__handle_sigterm_signal` para manejar esta lógica. Se guardan las conexiones activas en una lista `_active_client_connections` para poder cerrarlas todas al recibir la señal SIGTERM. Este manejo se agrego en la función `run` antes de emepzar a escuchar conexiones:
```
  signal.signal(signal.SIGTERM, self.__handle_sigterm_signal)
```
Además, se agrego la varibale `_is_listening` para que el servidor pueda dejar de aceptar nuevas conexiones cuando se recibe la señal SIGTERM.


El flag `-t` en el comando `docker compose down` especifica el tiempo de espera antes de forzar la terminación de los contenedores. Esto permite que las aplicaciones dentro de los contenedores tengan tiempo para cerrar sus recursos de manera adecuada antes de ser terminadas abruptamente.

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.


#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).

#### Solución:

Para el protocolo definido de comunicación entre cliente y servidor, se utilizara el formato TLV (Type-Length-Value) para el envío de los datos. Existira al inicio un campo que indicara el tipo del mensaje (apuesta, confirmacion, etc). Para esto se reservara 1 byte. Luego se indicara la longitud del mensaje en bytes, para lo cual se reservara 2 bytes. Por ultimo se enviara el mensaje serializado en bytes.

Se seralizara en big-endian.

En caso que se envie un mensaje tipo MESSAGE_TYPE_BET (Type = 0x01), el campo Value contendra los datos de la apuesta serializados siguiendo el siguiente formato:

| Field             | Type           | Length (bytes) | Description                       |
|-------------------|----------------|----------------|-----------------------------------|
| Id de la agencia  | 0x10           | 2              | Identificador unico de la agencia |
| Nombre            | 0x11           | Variable       | Nombre del apostador              |
| Apellido          | 0x12           | Variable       | Apellido del apostador            |
| DNI               | 0x13           | Variable       | Documento Nacional de Identidad   |
| Fecha Nac.        | 0x14           | Variable       | Fecha de nacimiento (YYYY-MM-DD)  |
| Numero            | 0x15           | 2              | Numero apostado                   |

En caso que se envie un mensaje tipo ACK_MESSAGE_TYPE (Type = 0xFF), el campo Value contendra los siguientes datos:
| Field             | Type           | Length (bytes) | Description                                                   |
|-------------------|----------------|----------------|---------------------------------------------------------------|
| ACK               | 0x00           | 4              | Mensaje recicibido correctamente (0x00000000)                 |

Por ejemplo, para enviar una apuesta del apostador "Carolina Gonzalez", con DNI 34098765, nacimiento 1990-01-01 y numero 1001, desde la agencia con ID 1, se enviaria el siguiente mensaje:

01 → MessageType = BET.

00 36 → longitud del payload = 54 bytes.

| Hexadecimal                           | Significado                         | Valor interpretado      |
| ------------------------------------- | ----------------------------------- | ----------------------- |
| `10 04 00 00 00 01`                   | AGENCY\_ID (Type=16, Len=4)         | `0x00000001` = **1**    |
| `11 08 43 61 72 6F 6C 69 6E 61`       | CLIENT\_NAME (Type=17, Len=8)       | `"Carolina"`            |
| `12 08 47 6F 6E 7A 61 6C 65 7A`       | CLIENT\_SURNAME (Type=18, Len=8)    | `"Gonzalez"`            |
| `13 08 33 34 30 39 38 37 36 35`       | CLIENT\_DNI (Type=19, Len=8)        | `"34098765"`            |
| `20 0A 31 39 39 30 2D 30 31 2D 30 31` | CLIENT\_BIRTHDATE (Type=20, Len=10) | `"1990-01-01"`          |
| `15 04 00 00 03 E9`                   | BET\_NUMBER (Type=21, Len=4)        | `0x000003E9` = **1001** |

Una vez que el servidor reciba la apuesta y la almacena, debera enviar una confirmacion al cliente (ack). Finalmente, cierra la conexion.

#### **Agencia**: 

Se creo la clase bet.go en el cliente para representar la apuesta. En la misma se encuentran los metodos para serializar la apuesta:
```go
type Bet struct {
	agencyId			 			uint16
	number        			uint16    
	clientName    			string 
	clientSurname 			string 
	clientDNI    			  string 
	clientBirthDate     string 
}
```
Se creo la clase protocol.go para manejar la comunicación con el servidor:
```go
type Protocol struct {
  conn net.Conn
}
```
En la misma se encuentran los metodos para enviar y recibir mensajes evitando los fenomenos de short read y short write. En el protoclo de comunicacion definido, se envia 1 byte para el tipo de mensaje, 2 bytes para la longitud del mensaje y luego el mensaje serializado en bytes. Por ende, en el metodo `ReceiveAll` se lee primero el tipo de mensaje, luego la longitud del mensaje y por ultimo se lee la cantidad de bytes indicada por la longitud del mensaje, evitando asi el short read.

Dicha función es utilizada para recibir el mensaje de confirmación del servidor:
```go
func (a *Agency) recvAck(bet *Bet) error {
	ackMessage := make([]byte, SIZE_ACK_MESSAGE)
	err := a.protocol.ReceiveAll(ackMessage)
	if err != nil {
		return err
	}
	if len(ackMessage) > 0 && ackMessage[0] == MESSAGE_TYPE_ACK && ackMessage[3] == ACK_OK { 
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			bet.clientDNI,
			bet.number,
		)
	}
	return nil
}
```


El metodo `SendAll` envia los datos en el mismo orden, evitando el short write. Chequea que los bytes enviados sean la misma cantidad que los bytes a enviar y en caso contrario intenta enviar los bytes restantes. 

Dicha función es utilizada para enviar la apuesta al servidor:
```go
func (a *Agency) sendBet(bet *Bet) error {
	serializedBet := bet.Serialize()
	err := a.protocol.SendAll(serializedBet)
	if err != nil {
		return err
	}
	return nil
}
```

#### **Servidor**:
Se creo la clase protocol.py en el servidor para manejar la comunicación con el cliente:
```python 
  def __init__(self, agencySocket: socket):
    self._agency_socket = agencySocket
```

La misma se encarga de enviar y recibir mensajes evitando los fenomenos de short read y short write de la misma manera que en el cliente.

El metodo `receive_all` es utilizado para recibir la apuesta del cliente:
```python
  def receive_menssage(self):
    """
    Receives a message from the agency socket
    
    Returns a Bet object in case of success when the message type is
    MESSAGE_TYPE_BET. Otherwise, it returns None.
    """
    message_type = self._agency_socket.recv(MESSAGE_TYPE_SIZE)
    data = self.__receive_all()
    
    if message_type and message_type[0] == MESSAGE_TYPE_BET:
      return Bet.deserialize(data)
    else:
      pass
```

Una vez el servidor recibe la apuesta, la almacena mediante la funcion `store_bet(...)` y luego envia una confirmacion al cliente:
```python
  def send_ack(self):
    """
    Sends an ACK message to the agency socket
    """
    ack_message = bytearray()
    ack_message.append(ACK_MESSAGE_TYPE)
    ack_message.extend((0).to_bytes(LENGTH_SIZE, byteorder='big'))
    ack_message.extend((ACK_OK).to_bytes(ACK_SIZE, byteorder='big'))
    
    self.__send_all(ack_message)
```

Finalmente, se cierra la conexion con el cliente.

