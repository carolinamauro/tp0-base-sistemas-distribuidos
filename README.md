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
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

#### Solución:
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