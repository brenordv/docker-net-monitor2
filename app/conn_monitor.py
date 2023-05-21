# -*- coding: utf-8 -*-
import itertools
import json
import os
import time
from datetime import datetime
from typing import Union
import requests
import speedtest
import paho.mqtt.client as mqtt

from raccoon_simple_stopwatch.stopwatch import StopWatch
from simple_log_factory.log_factory import log_factory


internet_outage = False
internet_outage_sw = StopWatch()
pending_messages = []
logger = log_factory("net_monitor")
site_list = itertools.cycle([
    "https://www.google.com",
    "https://www.duckduckgo.com",
    "https://www.cloudflare.com/",
    "https://www.bing.com"
])
mqtt_server = os.environ.get("MQTT_SERVER")

if mqtt_server is None:
    raise Exception("MQTT_SERVER environment variable is not set")


def test_internet_connection(url: str) -> Union[dict, None]:
    global logger
    global pending_messages
    logger.info("Testing internet connection...")
    timeout = 5  # Set a timeout of 5 seconds
    sw = StopWatch(True)
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        return {
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "status": response.status_code,
            "response_time": round(sw.end(raw=True).total_seconds() * 1000, 2),
            "error_text": "",
            "success": True,
            "type": 1
        }
    except requests.RequestException as re:
        pending_messages.append({
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "status": re.response.status_code,
            "response_time": round(sw.end(raw=True).total_seconds() * 1000, 2),
            "error_text": re.response.text,
            "success": False,
            "type": 1
        })
    except Exception as e:
        logger.error(f"Failed to test internet connection: {e}")

    return None


def run_speed_test() -> Union[dict, None]:
    global logger
    logger.info("Testing internet speed...")
    try:
        s = speedtest.Speedtest()
        s.get_best_server()
        download_speed = s.download()
        upload_speed = s.upload()
        ping = s.results.ping

        # Convert speeds to Mbps
        download_speed_mbps = download_speed / 1e6
        upload_speed_mbps = upload_speed / 1e6

        return {
            "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "download_speed": round(download_speed_mbps, 2),
            "upload_speed": round(upload_speed_mbps, 2),
            "ping": round(ping, 2),
            "type": 2
        }
    except Exception as e:
        logger.error(f"Failed to run speed test: {e}")
        return None


def _get_mqtt_client():
    global logger
    global mqtt_server
    try:
        mqtt_broker = mqtt_server
        mqtt_port = 1883
        client = mqtt.Client()
        client.connect(mqtt_broker, mqtt_port)
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        return None


def _publish_mqtt_message(topic: str, client, message, save_if_failed=True) -> bool:
    global pending_messages
    global logger
    try:
        client.publish(topic, json.dumps(message))
        client.disconnect()
        return True
    except Exception as e:
        logger.error(f"Failed to publish MQTT message: {e}")
        if save_if_failed:
            pending_messages.append(message)

        return False


def _publish_mqtt_message_to_net_mon_topic(client, message, save_if_failed=True):
    return _publish_mqtt_message("/home/net-monitor", client, message, save_if_failed)


def _publish_mqtt_message_to_alerts_info(client, message, save_if_failed=True):
    return _publish_mqtt_message("/alerts/info", client, message, save_if_failed)


def publish_single_message(message, where_to_publish: str = "net_mon"):
    global logger
    global pending_messages
    logger.info("Publishing message...")

    client = _get_mqtt_client()
    if client is None:
        pending_messages.append(message)
        return

    if where_to_publish == "net_mon":
        _publish_mqtt_message_to_net_mon_topic(client, message)
    elif where_to_publish == "alerts_info":
        _publish_mqtt_message_to_alerts_info(client, message)


def publish_pending_messages():
    global pending_messages
    global logger

    if len(pending_messages) == 0:
        logger.info("No pending messages to publish.")
        return

    logger.info("Publishing pending messages...")
    client = _get_mqtt_client()
    if client is None:
        return

    failed_messages = []
    for message in pending_messages:
        published = _publish_mqtt_message_to_net_mon_topic(client, message, save_if_failed=False)
        if published:
            continue
        failed_messages.append(message)

    pending_messages = failed_messages


def toggle_outage_control(success: bool):
    global internet_outage
    global internet_outage_sw

    if not internet_outage and not success:
        internet_outage = True
        internet_outage_sw.start()
        logger.info("Internet outage detected. Starting outage timer.")
        return

    if internet_outage and success:
        internet_outage = False
        elapsed_time = internet_outage_sw.end()
        msg = f"Internet outage resolved. Outage duration: {elapsed_time}"
        logger.info(msg)
        publish_single_message({"message": msg}, where_to_publish="alerts_info")
        return


def main():

    global pending_messages
    global site_list
    global logger
    initial_min = time.strftime("%M")

    while True:
        net_mon_result = test_internet_connection(next(site_list))
        if net_mon_result is not None:
            publish_single_message(net_mon_result)

        if time.strftime("%M") == initial_min:
            speed_test_result = run_speed_test()

            if speed_test_result is not None:
                publish_single_message(speed_test_result)

        if net_mon_result is not None:
            success = net_mon_result.get("success", False)
            if success:
                publish_pending_messages()
            toggle_outage_control(success)

        logger.info("Sleeping for 60 seconds...")
        time.sleep(60)


if __name__ == '__main__':
    main()
