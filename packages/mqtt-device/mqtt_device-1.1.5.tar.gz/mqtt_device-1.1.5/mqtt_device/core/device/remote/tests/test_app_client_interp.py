import logging
import unittest

from mqtt_device.common.common_log import basic_config_log, create_logger
from mqtt_device.core.client.mqtt_client import IMQTTClient, MessageReceivedEvent, ClientConnexionEvent
from mqtt_device.event_listener.listener import EventHandler
from mqtt_device.core.device.remote import ApplicationClient, RemoteClient
from mqtt_device.core.device.remote import ApplicationClientTopicInterpreter


class FakeMQTT(IMQTTClient):

    def __init__(self):
        self.logger = create_logger(self)
        self._message_received_event: EventHandler[MessageReceivedEvent] = EventHandler(self)
        self._connected: EventHandler[ClientConnexionEvent] = EventHandler(self)

    @property
    def message_received(self) -> EventHandler[MessageReceivedEvent]:
        return self._message_received_event

    def connexion_error(self, text: str):
        pass

    @property
    def connected(self):
        return self._connected

    def disconnected(self):
        pass

    @property
    def is_connected(self) -> bool:
        pass

    @property
    def is_running(self) -> bool:
        pass

    def connect(self):
        self._connected(event=ClientConnexionEvent(is_connected=True))

    def disconnect(self):
        pass

    def wait_until_ended(self, timeout: int):
        pass

    def publish_topic(self, topic: str, payload=None, qos=2, retain: bool = False, properties=None):
        self.logger.info(f"Publishing topic {topic}, message {payload}, retain {retain}, properties {properties}")

    def subscribe_topic(self, topic: str, qos: int = 2):
        self.logger.info(f"Subscribing topic {topic}, qos={qos}")


class TestRemoteClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        basic_config_log(level=logging.DEBUG)


    def test(self):

        fake_mqtt = FakeMQTT()


        client = ApplicationClient(environment_name="my_env", id_env="my_id", client_id="my_client", mqtt_client=fake_mqtt)
        interpreter = ApplicationClientTopicInterpreter()
        client._topic_interpretor = interpreter

        client.connect()

        remote_client = RemoteClient(environment_name="my_env", id_env="my_id", client_id="remote_client1")

        client.add_remote_client(remote_client)

        client.wait_until_ended()


        print("ok")