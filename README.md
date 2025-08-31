# TP0: Docker + Comunicaciones + Concurrencia

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).

#### Solución:
Se crearon volúmenes (bind mountS) para los archivos de configuración del cliente y del servidor, de modo que los mismos puedan ser editados en el host y reflejarse en los containers sin necesidad de reconstruir las imágenes.

Se modifico el archivo docker-compose.py agregando los siguientes volúmenes:
Servver
```yaml
    volumes:
      - ./server/config.yaml:/config.yaml
```
Client
```yaml
    volumes:
      - ./client/config.yaml:/config.yaml
```

De esta forma, los archivos `config.yaml` y `config.ini` son montados (inyectados) en los containers en la ruta `/config.yaml` y `/config.ini` respectivamente, y los cambios realizados en los archivos en el host se reflejan inmediatamente en los containers.