#!/bin/bash

message="Hola, Mundo!"

rta=$(docker run --rm --network tp0_testing_net busybox sh -c "echo $message | nc server 12345")
echo $rta