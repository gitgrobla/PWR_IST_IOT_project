#!/bin/bash

cp ./certs_and_keys/{server.key,server.crt} /etc/mosquitto/certs
chmod o+r /etc/mosquitto/certs/server.*

cp ./certs_and_keys/ca.crt /etc/mosquitto/ca_certificates
chmod o+r /etc/mosquitto/ca_certificates/ca.crt

cp ./certs_and_keys/{mosquitto.conf,passwd_file} /etc/mosquitto

mkdir /home/pi/tests/certs
mkdir /home/pi/tests/certs/ca
cp ./certs_and_keys/{hub.crt,hub.key} /home/pi/tests/certs
cp ./certs_and_keys/ca.crt /home/pi/tests/certs/ca
chmod o+r /home/pi/tests/certs/*
chmod o+r /home/pi/tests/certs/ca/*

systemctl restart mosquitto.service

echo "Configuration completed"
