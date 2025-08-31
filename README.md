# TP0: Docker + Comunicaciones + Concurrencia

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

En caso que se envie un mensaje tipo apuesta (Type = 0x01), el campo Value contendra los datos de la apuesta serializados siguiendo el siguiente formato:

| Field             | Type           | Length (bytes) | Description                       |
|-------------------|----------------|----------------|-----------------------------------|
| Id de la agencia  | 0x10           | 4              | Identificador unico de la agencia |
| Nombre            | 0x11           | Variable       | Nombre del apostador              |
| Apellido          | 0x12           | Variable       | Apellido del apostador            |
| DNI               | 0x13           | Variable       | Documento Nacional de Identidad   |
| Fecha Nac.        | 0x14           | Variable       | Fecha de nacimiento (YYYY-MM-DD)  |
| Numero            | 0x15           | 4              | Numero apostado                   |

En caso que se envie un mensaje tipo confirmacion (Type = 0x01), el campo Value contendra los siguientes datos:
| Field             | Type           | Length (bytes) | Description                                                   |
|-------------------|----------------|----------------|---------------------------------------------------------------|
| ACK               | 0xFF           | 4              | Se envia mensaje de ack de que el servidor recibio la apuesta. Se envia 0x00 |                                              

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

