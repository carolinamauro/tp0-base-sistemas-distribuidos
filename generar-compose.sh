#!/bin/bash

file_name=$1
clients_amount=$2

if [ -z "$file_name" ]; then
    file_name="docker-compose-dev.yml"
fi

if [ -z "$clients_amount" ]; then
    clients_amount=5
fi

python3 generar-compose.py "$file_name" "$clients_amount"