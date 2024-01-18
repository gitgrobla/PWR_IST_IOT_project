#!/bin/bash

mkdir /home/pi/tests/certs
mkdir /home/pi/tests/certs/ca
cp ./certs_and_keys/{client_1.crt,client_1.key} /home/pi/tests/certs
cp ./certs_and_keys/ca.crt /home/pi/tests/certs/ca
chmod o+r /home/pi/tests/certs/*
chmod o+r /home/pi/tests/certs/ca/*

echo "Configuration completed"