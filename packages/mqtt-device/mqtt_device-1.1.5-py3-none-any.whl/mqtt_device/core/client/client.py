import logging
import re
from logging import Logger
from typing import Generic

from mqtt_device.common.common_log import create_logger
from mqtt_device.core.client.mqtt_client import IMQTTClient
from mqtt_device.core.device.device_collection import DeviceCollection
from mqtt_device.core.device.type_var import T_DEVICE
from mqtt_device.core.topic.topic import TopicInterpreter, RawTopic


class BaseClient(Generic[T_DEVICE]):

    def __init__(self, environment_name: str, id_env: str):

        self._logger = create_logger(self)

        # self.client_id = client_id
        self.environment_name = environment_name
        self.id_env = id_env
        self._devices: DeviceCollection[T_DEVICE] = DeviceCollection()

    @property
    def logger(self) -> Logger:
        return self._logger

    # @property
    # def home_topic(self) -> str:
    #     res = f"{self.environment_name}/{self.id_env}/{self.client_id}"
    #     return res.replace(' ', '_')


    @property
    def devices(self) -> DeviceCollection[T_DEVICE]:
        return self._devices

    def __eq__(self, other: 'Client'):
        if type(other) != type(self):
            return False

        return self.environment_name == other.environment_name and self.id_env == other.id_env


class Client(Generic[T_DEVICE], BaseClient[T_DEVICE]):

    DEFAULT_QOS = 2
    DEFAULT_RETENTION = False

    def __init__(self, environment_name: str, id_env: str, mqtt_client: IMQTTClient, topic_interpreter: TopicInterpreter):
        super().__init__(environment_name, id_env)

        self._mqtt_client: IMQTTClient = mqtt_client
        # self._mqtt_client.client_id = client_id
        self._topic_interpretor: TopicInterpreter = topic_interpreter
        # self._topic_interpretor.client = self

        self.mqtt_client = mqtt_client

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def publish_topic(self, topic: str, payload: str, qos: int = DEFAULT_QOS, retain: bool = DEFAULT_RETENTION):
        self._mqtt_client.publish_topic(topic=topic, payload=payload, qos=qos, retain=retain)

    def subscribe_topic(self, topic: str):
        self._mqtt_client.subscribe_topic(topic=topic)

    def _on_message_received(self, sender: IMQTTClient, topic: str, message: str):
        self.logger.info(f"MESSAGE RECEIVED TOPIC = {topic} MSG = {message}")
        self._topic_interpretor.process(raw_topic=RawTopic(topic, message))

    @property
    def home_topic(self) -> str:
        res = f"{self.environment_name}/{self.id_env}/{self.client_id}"
        return res.replace(' ', '_')

    @property
    def client_id(self) -> str:
        return self._mqtt_client.client_id

    @property
    def mqtt_client(self) -> IMQTTClient:
        return self._mqtt_client

    @mqtt_client.setter
    def mqtt_client(self, value: IMQTTClient):

        if value is not None:
            self._mqtt_client = value

            # # override client id if client have an id
            # if self.client_id is not None:
            #     self._mqtt_client.client_id = self.client_id

            self._topic_interpretor.client = self

    def connect(self):
        if not self._mqtt_client.is_connected:
            self._mqtt_client.connect()

    def disconnect(self):

        # self.logger.error("##### NEED TO DISCONNECT!")
        if self._mqtt_client.is_connected:
            self._mqtt_client.disconnect()

    def wait_until_ended(self, timeout: float = None):

        if self.mqtt_client:
            self.mqtt_client.wait_until_ended(timeout=None)


class MessageFilter:

    def __init__(self, environment: str = "*", id_env: str = "*"):
        self.environment = environment
        self.id_env = id_env

    def is_in(self, topic: RawTopic) -> bool:

        if self.environment == "*":
            self.environment = ".*"

        if self.id_env == "*":
            self.id_env = ".*"

        pattern = f"^{self.environment}/{self.id_env}/.*"

        res = re.match(pattern, str(topic))

        return not res is None
