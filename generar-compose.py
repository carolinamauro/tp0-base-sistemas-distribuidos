import sys

COMPOSE_TEMPLATE = """\
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
    volumes: 
      - ./server/config.ini:/config.ini
    networks: 
      - testing_net
{clients}
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

CLIENT_TEMPLATE = """\
  {name}:
    container_name: {name}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={id}
    networks: 
      - testing_net
    depends_on:
      - server
    volumes:
      - ./client/config.yaml:/config.yaml
"""

def generate_compose(file_name, clients_amount):
    compose = COMPOSE_TEMPLATE
    clients_str = ""
    for i in range(1, clients_amount + 1):
        clients_str += CLIENT_TEMPLATE.format(name=f"client{i}", id=i)
    compose = compose.format(clients=clients_str)
    
    with open(file_name, "w") as f:
        f.write(compose)
            
if __name__ == "__main__":
    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        clients = int(sys.argv[2])
        generate_compose(file_name, clients)
    else:
        print("Usage: python3 generar-compose.py <output_file> <number_of_clients>")
 