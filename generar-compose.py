import yaml
import sys

default_data = {
    "name": "tp0",
    "services": {
        "server": {
            "container_name": "server",
            "image": "server:latest",
            "entrypoint": "python3 /main.py",
            "environment": ["PYTHONUNBUFFERED=1", "LOGGING_LEVEL=DEBUG"],
            "networks": ["testing_net"],
        },
    },
    "networks": {
        "testing_net": {
            "ipam": {
                "driver": "default",
                "config": [{"subnet": "172.25.125.0/24"}],
            }
        }
    }
}

def to_yaml(file_name, compose_data):
    with open(file_name, "w") as f:
        dump = yaml.dump(compose_data, default_flow_style=False, sort_keys=False)
        f.write(dump)


def generar_compose(file_name, clients_amount):
    data = default_data.copy()
    clients = {}
    
    for i in range(clients_amount):
        client_name = f"client{i+1}"
        clients[client_name] = {
            "container_name": client_name,
            "image": "client:latest",
            "entrypoint": "/client",
            "enviroment": ["CLI_ID=" + str(i + 1)],
            "networks": ["testing_net"],
            "depends_on": ["server"],
        }
        
    data["services"].update(clients)
    to_yaml(file_name, data)

      
if __name__ == "__main__":
    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        clients = int(sys.argv[2])
        generar_compose(file_name, clients)
      
   