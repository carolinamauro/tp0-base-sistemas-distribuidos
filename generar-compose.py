import sys

CLIENT_NAMES = ["Carolina", "Facuando", "Lucia", "Franco", "Diego"]
CLIENT_SURNAMES = ["Gonzalez", "Perez", "Lopez", "Garcia", "Rodriguez"]
CLIENT_DNIS = ["34098765", "43456789", "34567890", "45678901", "56789012"]
CLIENT_BIRTH_DATES = ["1990-01-01", "2001-05-15", "1996-07-20", "2004-12-30", "2007-03-10"]

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
      - NOMBRE={client_name}
      - APELLIDO={client_surname}
      - DNI={client_dni}
      - FECHA_NACIMIENTO={birth_date}
      - NUMERO={client_bet_number}
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
        clients_str += CLIENT_TEMPLATE.format(name=f"client{i}", id=i, 
                                              client_name=CLIENT_NAMES[i-1],
                                              client_surname=CLIENT_SURNAMES[i-1],
                                              client_dni=CLIENT_DNIS[i-1],
                                              client_bet_number=1000 + i,
                                              birth_date=CLIENT_BIRTH_DATES[i-1])
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
 