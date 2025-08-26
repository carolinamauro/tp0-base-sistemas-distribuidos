#!/bin/bash

CONFIG_FILE="server/config.ini"
SERVER_IP=$(grep SERVER_IP $CONFIG_FILE | cut -d ' '  -f3)
SERVER_PORT=$(grep SERVER_PORT $CONFIG_FILE | cut -d ' ' -f3)

message="Hola, Mundo!"

server_response=$(docker run --rm --network tp0_testing_net busybox sh -c "echo $message | nc $SERVER_IP $SERVER_PORT")

if [ "$server_serponse" = "$message" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi

