# TP0: Docker + Comunicaciones + Concurrencia

## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).


#### Solución:

El servidor fue modificado para que pueda manejar múltiples conexiones en paralelo.
Para esto, se utilizó la librería `threading` de Python, que permite crear un nuevo hilo para cada conexión entrante. De esta manera, cada cliente puede ser atendido de forma independiente y simultánea. Se eligio implementar el servidor en Python utilizando _multithreading_ ya que para este caso de uso, donde las operaciones son principalmente de I/O (entrada/salida) y no de cálculo intensivo, el uso de hilos es adecuado y eficiente. Por lo que el Global Interpreter Lock (GIL) no representa una limitación significativa en este contexto.

Cada vez que llega una nueva conexión, se crea un nuevo hilo que maneja la comunicación con ese cliente específico. Una vez se procesan todos los mensajes del cliente, se chequea si el se comenzo el sorteo. 
- En caso de que no se haya comenzado se verifica si la cantidad de agencias finalizadas es igual a la cantidad de agencias conectadas. Si es así, se procede a iniciar el sorteo y enviar los resultados a todas las agencias. Para esto, el hilo que detecta que todas las agencias han finalizado, lanza otro hilo que se encarga de iniciar el sorteo y enviar los resultados a todas las agencias. 
- En caso de que el sorteo no haya comenzado y no se hayan finalizado todas las agencias, el hilo queda esparando en `_lottery_done` a que se inicie el sorteo. Una vez se lance el evento, el hilo continúa su ejecución, envia los resultados al cliente y finaliza la conexión

Una vez todos los clientes han finalizado y se han enviado los resultados, el servidor pasa a realizar el join de todos los hilos que se crearon para manejar las conexiones. Esto se hace mediante el timeout del socket, donde se chequea si el sorteo ya se realizó y si todos los hilos han finalizado. En caso afirmativo, el servidor procede a realizar el join de los hilos y "limpiar" los recursos utilizados. Queda a la espera de nuevas conexiones.