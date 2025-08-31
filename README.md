# TP0: Docker + Comunicaciones + Concurrencia

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

#### Solución:
- En el cliente, se agregó un canal para escuchar la señal SIGTERM y se implementó la función `handleSigtermSignal` para cerrar la conexión del cliente de manera adecuada. 
- En el servidor, se agregó un manejador de señales para SIGTERM que cierra todas las conexiones activas de los clientes y el socket del servidor antes de salir. Se implementó la función `__handle_sigterm_signal` para manejar esta lógica. Se guardan las conexiones activas en una lista `_active_client_connections` para poder cerrarlas todas al recibir la señal SIGTERM.

El flag `-t` en el comando `docker compose down` especifica el tiempo de espera antes de forzar la terminación de los contenedores. Esto permite que las aplicaciones dentro de los contenedores tengan tiempo para cerrar sus recursos de manera adecuada antes de ser terminadas abruptamente.