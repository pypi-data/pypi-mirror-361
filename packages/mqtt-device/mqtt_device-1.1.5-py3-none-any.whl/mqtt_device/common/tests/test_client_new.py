import logging
import socket
import unittest
from time import sleep
from unittest.mock import MagicMock

from mqtt_device.core.client.client import MessageFilter
from mqtt_device.core.client.mqtt_client import MQTTClient
from mqtt_device.core.device.local.local_client import LocalClient
from mqtt_device.core.device.local.local_device import LocalDevice
from mqtt_device.core.device.remote.remote_client import RemoteClient
from mqtt_device.core.device.remote.remote_device import RemoteDevice
from mqtt_device.core.topic.topic import RawTopic
from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer

mosquitto: FakeMosquittoServer = None
local_ip: str = None

class TestBaseClientNew(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global local_ip

        logging.root.setLevel(logging.INFO)
        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)

    def test_LocalClient_add_local_device_TO_FINISH(self):

        class SomeDevice(LocalDevice):

            TYPE = "some_devices"
            def _bind_to_client(self):
                super()._bind_to_client()


        mock_mqtt_client: MQTTClient = MagicMock()
        client = LocalClient(environment_name="MyEnv", id_env="03", client_id="MyClient", mqtt_client=mock_mqtt_client)
        # local_device = LocalDevice(device_id="My Device")
        # local_device.client = client
        client.add_device(device=SomeDevice(device_id="MyDevice"))

        mock_mqtt_client.publish_topic.assert_called_once_with(topic="MyEnv/03/MyClient/MyDevice/$type", payload="some_devices", retain=True, qos=2)

    def test_MessageFilter_is_in(self):

        topic = RawTopic(topic_str="MyEnv/05/SomethingElse/AnotherThing")
        message_filter = MessageFilter(environment="MyEnv", id_env="05")
        self.assertTrue(message_filter.is_in(topic))

        message_filter = MessageFilter(environment="MyEnv", id_env="06")
        self.assertFalse(message_filter.is_in(topic))

    def test_MessageFilter_with_joker(self):

        topic = RawTopic(topic_str="MyEnv/05/SomethingElse/AnotherThing")
        message_filter = MessageFilter(environment="MyEnv", id_env="*")
        self.assertTrue(message_filter.is_in(topic))

        topic = RawTopic(topic_str="MyEnv/15/SomethingElse/AnotherThing")
        message_filter = MessageFilter(environment="MyEnv", id_env="*")
        self.assertTrue(message_filter.is_in(topic))

        topic = RawTopic(topic_str="MyEnvKO/32/SomethingElse/AnotherThing")
        message_filter = MessageFilter(environment="MyEnv", id_env="*")
        self.assertFalse(message_filter.is_in(topic))

        topic = RawTopic(topic_str="MyEnvKO/15/SomethingElse/AnotherThing")
        message_filter = MessageFilter(environment="*", id_env="*")
        self.assertTrue(message_filter.is_in(topic))


    def test_LocalClient_add_remote_client_with_and_without_filter(self):

        local_client = LocalClient(environment_name="SmartCage", id_env="01", client_id="MainApplication", mqtt_client=MagicMock())
        remote_client = RemoteClient(environment_name="SmartCage", id_env="01", client_id="Feeder")

        local_client.filter = MessageFilter(environment="SmartCage")
        local_client.add_remote_client(remote_client)
        self.assertEqual(1, len(local_client.get_all_remote_clients()))

        remote_client = RemoteClient(environment_name="NotSmartCage", id_env="01", client_id="Feeder")
        local_client.add_remote_client(remote_client)
        # not in the filter, client is not added
        self.assertEqual(1, len(local_client.get_all_remote_clients()))

    def test_LocalClient_get_all_devices(self):

        local_client = LocalClient(environment_name="SmartCage", id_env="01", client_id="MainApplication", mqtt_client=MagicMock())

        remote_client = RemoteClient(environment_name="Somenv", id_env="01", client_id="FirstClient")
        remote_client.add_remote_device(RemoteDevice(device_id="MyDevice1"))
        remote_client.add_remote_device(RemoteDevice(device_id="MyDevice2"))
        local_client.add_remote_client(remote_client)

        # devices = remote_client.get_remote_devices()

        remote_client = RemoteClient(environment_name="Somenv", id_env="02", client_id="SecondClient")
        remote_client.add_remote_device(RemoteDevice(device_id="MyDevice3"))
        local_client.add_remote_client(remote_client)

        res = local_client.remote_devices()
        self.assertEqual(3, len(res))

        # print("ok")


    def test_integration_add_client_and_devices(self):

        mosquitto = FakeMosquittoServer(ip=local_ip, kill_if_exists=True, verbose=False)
        mosquitto.start()

        mqtt_client = MQTTClient(client_id="My Test Client", broker_ip=local_ip)
        client = mqtt_client
        mqtt_client.connect()
        # client.connect()

        client.publish_topic(topic="SocialCage/01/STM01/$connected", payload="True", retain=True)
        client.publish_topic(topic="SocialCage/01/STM01/levier_1/$type", payload="levers", retain=True)

        mqtt_client = MQTTClient(client_id="My App Client", broker_ip=local_ip)
        app_client = LocalClient(environment_name="SocialCage", id_env="01", client_id="main_client", mqtt_client=mqtt_client)

        sleep(0.1)
        self.assertEqual(1, len(app_client._remote_clients))
        remote_client = app_client.get_remote_client("SocialCage/01/STM01")

        self.assertIsNotNone(remote_client)

        remote_device = remote_client.get_remote_device("levier_1")
        self.assertIsNotNone(remote_device)

        # print(len(remote_client.get_remote_devices()))
        # remotes = app_client._remote_clients

        client.wait_until_ended(100)




