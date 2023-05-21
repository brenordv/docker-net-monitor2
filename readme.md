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

## How internet check works?
The script pings one of the sites in the list. Every request has a timeout of 5 seconds. If the request times out, the
script assumes that the internet is down. If the request is successful, then the internet is working, regardless of the
status code. The reason behind it is simple: If the site rejected our request, it means that the internet is working.
I also set the script to ignore SSL problems because I don't want a certificate error to trigger a false positive.

When the internet is down, we're catching the `requests.exceptions.RequestException` because it is the base class for 
all exceptions raised by the `requests` library when making HTTP requests. It is a broad exception that encompasses 
various types of errors that can occur during the request process. Whenever an error occurs during an HTTP request 
using the `requests` library, a subclass of `RequestException` is raised.

Here are some common scenarios in which `requests.exceptions.RequestException` can be raised:

1. Connection-related errors: This includes `requests.exceptions.ConnectionError` when there is a problem establishing 
a connection, such as DNS resolution failure, network connectivity issues, or timeouts.

2. Timeout errors: If the request exceeds the specified timeout duration, `requests.exceptions.Timeout` can be raised.

3. Invalid URL or URL-related errors: If the provided URL is malformed or does not follow the expected format, 
`requests.exceptions.InvalidURL` or `requests.exceptions.MissingSchema` can be raised.

4. Redirect errors: If the request encounters too many redirects or encounters a redirect loop, 
`requests.exceptions.TooManyRedirects` can be raised.

5. SSL/TLS certificate verification errors: If there are issues with SSL/TLS certificate verification, such as an 
expired or invalid certificate, `requests.exceptions.SSLError` can be raised.

6. Authentication errors: If there are problems with authentication, such as incorrect credentials or lack of 
authorization, `requests.exceptions.HTTPError` can be raised.

7. Server-side errors: When the server returns an HTTP status code indicating an error, such as 4xx or 5xx status 
codes, `requests.exceptions.HTTPError` can be raised.

These are just a few examples, and there are other exceptions that can be derived from `RequestException` to handle 
specific types of errors. When handling exceptions in your code, it's generally recommended to catch `RequestException`
or its specific subclasses to handle different types of errors gracefully.


# What is needed for this to work
1. A running MQTT server
2. A running Node-RED instance (or any other way to receive the MQTT messages)
3. A Telegram bot (optional, but recommended)
4. Docker to run everything in a container

If you have a Raspberry Pi (or something similar) I recommend using [IoTStack](https://sensorsiot.github.io/IOTstack/), 
it's super easy to install and configure. It comes with a pre-configured MQTT server and Node-RED instance.


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