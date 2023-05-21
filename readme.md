# Network connection monitor
This is a simple application that monitors the internet connection, logs downtime, and performs internet speed tests. 
I have a running MQTT server alongside a Node-RED instance that receives the messages, logs them in a database, and 
sends me a notification when the internet is restored.

The data sent to the MQTT server is also utilized to generate a daily report, which is sent to my Telegram. The report 
includes the average response time of the requests (used to check if the internet is functioning), average download and 
upload speeds, and average ping.

Although I hastily put together this script in a few minutes, I acknowledge that there may be more elegant ways to 
accomplish the same task. Nonetheless, it serves its purpose adequately.

Feel free to use or modify it as needed.


# Installation
First of all, you need to install Docker on your machine, in a raspberry or in some machine that will be connected to
the internet.
Then you have to build and run the docker image.
(From the root directory of this project)
```shell
cd docker
./build.sh
./run.sh
```

Note that the `run.sh` script will prompt you for the MQTT_SERVER address. It was easier than setting up an env file and
then making sure it was not committed to the repo. Lazy, I know, but it's ok...