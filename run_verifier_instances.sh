#!/bin/bash

# Load environment variables
source .env

# Loop through the number of instances
for ((i=0; i<$INSTANCE_COUNT; i++))
do
  # Set the environment variables for the current instance
  service_port=$(($INITIAL_PORT_NUMBER + i))
  export INSTANCE_NUMBER=$i
  export SERVICE_PORT=$service_port

  # Run the service with the current configuration
  echo $SERVICE_PORT
  docker pull gleif/vlei-verifier
  docker run -d -p $SERVICE_PORT:7676 -e VERIFIER_CONFIG_FILE=verifier-config-test.json gleif/vlei-verifier --network host
done