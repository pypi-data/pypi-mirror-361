from mqtt_device.core.client.client import Client
from mqtt_device.core.client.mqtt_client import IMQTTClient
from mqtt_device.core.device.local.local_device import LocalDevice

from mqtt_device.core.topic.local_topic_interpreter import LocalClientTopicInterpreter


class LocalClient(Client[LocalDevice]):

    def __init__(self, environment_name: str, id_env: str, mqtt_client: IMQTTClient):
        super().__init__(environment_name, id_env, mqtt_client, LocalClientTopicInterpreter())