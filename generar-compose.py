import yaml
import sys

class DockerComposeYamlGenerator:
    
    def __init__(self, clients_amount, file_name):
        self.file_name = file_name
        self.compose = {
            "name": "tp0",
            "services": {
                "server": {
                    "container_name": "server",
                    "image": "server:latest",
                    "entrypoint": "python3 /main.py",
                    "environment": ["PYTHONUNBUFFERED=1"],
                    "networks": ["testing_net"],
                    "volumes": ["./server/config.yaml:/config.yaml"],
                },  
            },
            "networks": {
                "testing_net": {
                    "ipam": {
                        "driver": "default",
                        "config": [{"subnet": "172.25.125.0/24"}],
                    },
                },
            },
        }
        self.add_clients(clients_amount)
        
        
    def add_clients(self, clients_amount):
    
        for i in range(clients_amount):
            client_name = f"client{i+1}"
            self.compose["services"][client_name] = {
                "container_name": client_name,
                "image": "client:latest",
                "entrypoint": "/client",
                "environment": ["CLI_ID=" + str(i + 1)],
                "networks": ["testing_net"],
                "depends_on": ["server"],
                "volumes": ["./client/config.yaml:/config.yaml"],
        }
            
    def generate_yaml(self):
        text = yaml.safe_dump(self.compose, sort_keys=False, default_flow_style=False)
        with open(self.file_name, "w", encoding="utf-8") as f:
            f.write(text)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        clients = int(sys.argv[2])
        composeGenerator = DockerComposeYamlGenerator(clients, file_name)
        composeGenerator.generate_yaml()
      
   