docker run -it --rm --name mqtt_broker --net lab4_network -p 1883:1883 -v %cd%\mosquitto\config\:/mosquitto/config/ eclipse-mosquitto
pause