#!/bin/bash

file_name=$1
clients_amount=$2

if [ -z "$file_name" ] || [ -z "$clients_amount" ]; then
    echo "Uso: $0 <nombre_archivo> <cantidad_clientes>"
    exit 1
fi

pip install -r requirements.txt

python3 generar-compose.py "$file_name" "$clients_amount"