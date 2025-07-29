import socket
import unittest
from time import sleep

from mqtt_device.core.device.local.device import ILever

from mqtt_device.core.device.remote import ApplicationClient

from mqtt_device.core.client.mqtt_client import MQTTClient

from mqtt_device.common.common_log import basic_config_log
from mqtt_device.core.device.local import LocalClient
from mqtt_device.core.device.local import FakeLeverLocal

local_ip: str = None

class TestRemoteClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global local_ip

        basic_config_log()

        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)


    def test_remote_lever(self):

        local_mqtt = MQTTClient(broker_ip=local_ip)
        local = LocalClient(environment_name="env", id_env="01", client_id="local", mqtt_client=local_mqtt)
        local.connect()

        fake_lever = FakeLeverLocal(device_id="lever_1")
        local.add_device(fake_lever)

        remote_mqtt = MQTTClient(broker_ip=local_ip)
        app_client = ApplicationClient(environment_name="env", id_env="01", client_id="app", mqtt_client=remote_mqtt)

        app_client.connect()

        sleep(1)
        remote_lever = app_client.get_remote_device(device_id="lever_1").as_type(ILever)

        def on_lever_pressed(sender, event):
            print("PRESSED")

        remote_lever.lever_pressed.register(on_lever_pressed)
        sleep(1)
        fake_lever.activate()
        # remote_mqtt.wait_until_ended()

if __name__ == '__main__':
    unittest.main()
