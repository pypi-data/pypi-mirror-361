import logging
import unittest
from time import sleep
from unittest.mock import MagicMock

from mqtt_device.core.client.mqtt_client import MQTTClient
from mqtt_device.core.device import DeviceProperty

from mqtt_device.common.common_log import basic_config_log

from mqtt_device.core.device.remote import RemoteClient, ApplicationClient
from mqtt_device.core.device.remote import RemoteDevice


class FakeDevice1(RemoteDevice):
    DEVICE_TYPE = "fake_device"

class TestRemoteClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global local_ip

        basic_config_log(level=logging.DEBUG)

        # # get the host ip
        # host_name = socket.gethostname()
        # local_ip = socket.gethostbyname(host_name)

    def test_tmp_local_client(self):
        pass

    def test_tmp_remote_souris_city(self):
        mqtt_client = MQTTClient(broker_ip="192.168.24.14", broker_port=1884, client_id="application_SC_NDE")
        app_client = ApplicationClient(environment_name="souris_city", id_env="01", client_id="application_SC_NDE", mqtt_client=mqtt_client)
        app_client.connect()
        sleep(5)

        device = app_client.remote_devices
        sc = device.get_by_id("souris_city")

        app_client.wait_until_ended()


    def test_add_remote_client_call_subscribe(self):
        fake_mqtt = MagicMock()
        app_client = ApplicationClient(environment_name="env", id_env="01", client_id="app", mqtt_client=fake_mqtt)
        client_1 = RemoteClient(environment_name="my_xp", id_env="01", client_id="client_1")
        app_client.add_remote_client(client_1)

        # check subscribe is called by mqtt client
        fake_mqtt.subscribe_topic.assert_any_call(topic=client_1.home_topic +"/+/$meta")

    def test_add_remote_device_call_susbcribe(self):
        fake_mqtt = MagicMock()
        app_client = ApplicationClient(environment_name="env", id_env="01", client_id="app", mqtt_client=fake_mqtt)
        client_1 = RemoteClient(environment_name="my_xp", id_env="01", client_id="client_1")
        app_client.add_remote_client(client_1)
        device_1 = FakeDevice1(device_id="fake_device_1", location="room_1")

        client_1.add_device(device_1)
        # check subscribe is called by mqtt client
        fake_mqtt.subscribe_topic.assert_any_call(topic=device_1.home_topic+"/+/$meta")

    def test_add_remote_property_call_susbcribe(self):
        fake_mqtt = MagicMock()
        app_client = ApplicationClient(environment_name="env", id_env="01", client_id="app", mqtt_client=fake_mqtt)
        client_1 = RemoteClient(environment_name="my_xp", id_env="01", client_id="client_1")
        app_client.add_remote_client(client_1)
        device_1 = FakeDevice1(device_id="fake_device_1", location="room_1")
        client_1.add_device(device_1)
        prop = DeviceProperty(property_name="my_prop", datatype="str")
        device_1.add_property(prop)

        # check subscribe is called by mqtt client
        fake_mqtt.subscribe_topic.assert_any_call(topic='my_xp/01/client_1/fake_device_1/my_prop')

    def test_add_device(self):
        client_1 = RemoteClient(environment_name="my_xp", id_env="01", client_id="client_1")

        device_1 = FakeDevice1(device_id="fake_device_1", location="room_1")
        client_1.add_device(device_1)

        res = client_1.get_device("fake_device_1")
        self.assertEqual(device_1, res)

        self.assertEqual(1, len(client_1.devices))


if __name__ == '__main__':
    unittest.main()
