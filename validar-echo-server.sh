#!/bin/bash

message="Hola, Mundo!"

server_response=$(docker run --rm --network tp0_testing_net busybox sh -c "echo $message | nc server 12345")

if [ "$server_serponse" == "$message" ]; then
    echo "action: test_echo_server | result: success"
    exit 0
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi

