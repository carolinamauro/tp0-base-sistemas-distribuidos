#!/bin/bash

file_name="docker-compose-dev.yaml"
clients_amount="5"

python3 generar-compose.py "$file_name" "$clients_amount"