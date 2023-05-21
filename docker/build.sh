#!/bin/bash

# Copy app folder to this folder, since docker can't access parent directories.
cp -r ../app .

docker build -t raccoon_conn_monitor:latest .

# Remove local app folder
rm -rf app