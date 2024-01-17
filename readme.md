```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto.service
sudo systemctl start mosquitto.service
sudo systemctl status mosquitto.service

sudo apt-get update
sudo apt-get install nmap
```

```bash
#subscribe
mosquitto_sub -h $host -t $channel

#publish
mosquitto_pub -h $host -t $channel -m $message
```

```bash
pip install paho-mqtt
```

```txt
allow_anonymous true
listener 1883 0.0.0.0
```

```txt
https://www.chirpstack.io/docs/guides/mosquitto-tls-configuration.html
http://www.steves-internet-guide.com/mosquitto-tls/
```

