#!/bin/bash

# Prompt user for MQTT server value
read -p "Enter MQTT server value: " mqtt_server

# Check if MQTT server value is empty
if [ -z "$mqtt_server" ]; then
  echo "Error: MQTT server value cannot be empty. Exiting script."
  exit 1
fi

# Build the docker command with the environment variable
docker_command="docker run -d --restart=unless-stopped --name conn_monitor -e MQTT_SERVER=${mqtt_server} -it raccoon_conn_monitor:latest"

# Run the docker command
eval $docker_command
