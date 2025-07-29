import logging
import socket
import unittest
from threading import Thread

from mqtt_device.common.common_log import basic_config_log

from mqtt_device.core.client.mqtt_client import MQTTClient
from mqtt_device.core.device.local import LocalClient
from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer
from mqtt_device.device.fake_common_device import FakeLeverLocal

mosquitto: FakeMosquittoServer = None
local_ip: str = None

class TestFakeLocalDevices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        basic_config_log()
        global local_ip

        logging.root.setLevel(logging.INFO)
        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)

    def test_activate(self):



        mosquitto = FakeMosquittoServer()
        mosquitto.start()

        mqtt_client = MQTTClient(broker_ip=local_ip)

        def run_test():
            other_client = MQTTClient(client_id="other_client", broker_ip=local_ip)
            other_client.connect()
            other_client.publish_topic(topic="my_xp/01/MyClient/fake_lever_1/activate/set", payload="ok")

        # create devices client and set his device to a fake one
        device_client = LocalClient(environment_name="my_xp", id_env="01", client_id="MyClient", mqtt_client=mqtt_client)
        mqtt_client.connect()

        fake_lever = FakeLeverLocal(device_id="fake_lever_1")
        device_client.add_device(fake_lever)

        thread_test = Thread(target=run_test)
        thread_test.start()

        mqtt_client.wait_until_ended()


