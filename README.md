# TP0: Docker + Comunicaciones + Concurrencia

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). 

#### Solución
Se creo el script `validar-echo-server.sh` el cual obtiene del archivo `config.ini` las varibles SERVER_IP y SERVER_PORT. Luego se ejecuta el siguiente comando:
`server_response=$(docker run --rm --network tp0_testing_net busybox sh -c "echo $message | nc $SERVER_IP $SERVER_PORT")`
donde
1. Se corre la imagen de docker busybox (una distribucion de linux liviana que incluye el comando de netcat) en la red tp0_testing_net, la misma en la que se encontrará el servidor corriendo. De esta manera, ambos contenedores pueden comunicarse  sin la necesidad de exponer un puerto.
2. Con `sh -c` se abre una terminal dentro del contenedor y se ejecuta el comando `echo $message`, que imprime el mensaje "Hola,Mundo!". Ese mensaje se redirige mediante el pipe (|) al comando netcat (nc), que lo envía al servidor en la IP y el puerto especificados.
3. La espuesta se guarda en la variable  `server_response` y luego se lo compara con el mensaje original a ver si el servidor esta respondiendo correctammente.

                   