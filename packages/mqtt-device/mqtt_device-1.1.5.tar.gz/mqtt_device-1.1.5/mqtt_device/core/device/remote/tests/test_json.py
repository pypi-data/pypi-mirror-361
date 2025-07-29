import json
import unittest
from time import sleep

from dependency_injector import containers, providers
from dependency_injector.providers import List

from mqtt_device.common.common_log import basic_config_log
from mqtt_device.core.client.mqtt_client import MQTTClient
from mqtt_device.core.device.device_factory import DeviceFactory, LocalDeviceFactory, RemoteDeviceFactory
from mqtt_device.core.device.local.local_client import LocalClient
from mqtt_device.core.device.local.local_device import LocalDevice
from mqtt_device.core.device.remote.remote_client import ApplicationClient

json_str3 = """
{
    "local_client": {
      "environment_name": "my_env",
      "id_env": "01",
      "client_id": "my_local_client",
      "mqtt":{"broker_ip":"localhost"}
    }
}
"""
json_str2 = """
{
    "mqtt":{"broker_ip":"localhost"}
}
"""

json_str = """{
"client":{"name":"John", "age":30, "city":"New York"}
}"""

json_str4 = """
{
    "strings": ["one", "two", "three"]
}

"""


def split_to_str(to_split: str) -> List[str]:

    if to_split is None:
        return None

    res = [elem.strip() for elem in to_split.split(',')]
    return res

class LocalClientContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    local_device_factory = providers.Singleton(LocalDeviceFactory)

    mqtt_client = providers.Factory(MQTTClient,
                                      broker_ip=config.mqtt.broker_ip,
                                      broker_port=config.mqtt.broker_port,
                                      client_id=config.mqtt.client_id.required(),
                                      )
    #  id_env: str, client_id: str, mqtt_client: 'MQTTClient'
    local_client = providers.Singleton(LocalClient,
                                       environment_name=config.local_client.environment_name.required(),
                                       id_env=config.local_client.id_env.required(),
                                       client_id=config.local_client.client_id.required(),
                                       mqtt_client=mqtt_client
                                       )

    remote_device_factory = providers.Singleton(RemoteDeviceFactory)

    # environment_name: str, id_env: str, client_id: str, mqtt_client: MQTTClient
    app_client = providers.Singleton(ApplicationClient,
                                     environment_name=config.application_client.environment_name.required(),
                                     id_env=config.application_client.id_env.required(),
                                     client_id=config.application_client.client_id.required(),
                                     mqtt_client=mqtt_client,
                                     device_factory=remote_device_factory,
                                     expected_devices=config.application_client.expected_devices.required()
                                    )



class TestRemoteClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        basic_config_log()

    def test_device_factory(self):

        container = LocalClientContainer()
        container.config.from_json("./test.json")

        factory = container.local_device_factory()

        for item in container.config.devices():
            res = factory.instantiate(item)
            print(res)

    def test_local_client_with_json(self):

        container = LocalClientContainer()
        container.config.from_json("./test.json")

        factory = container.local_device_factory()

        local_client = container.local_client()
        local_client.connect()
        sleep(1)

        for item in container.config.devices():
            res = factory.instantiate(item)
            local_client.devices.add(res)

        local_client.wait_until_ended()

        print("ok")



    def test_json_str(self):
        res = json.loads(json_str4)

        print("ok")

    def test_json(self):
        # https://realpython.com/python-json/
        # https://www.geeksforgeeks.org/serialize-and-deserialize-complex-json-in-python/
        # https://pynative.com/make-python-class-json-serializable/

        res = json.loads(json_str)

        lc = LocalClient(environment_name="my_env", id_env="01", client_id="my_client", mqtt_client=MQTTClient(broker_ip="locahost"))

        json_data = json.dumps(lc.__dict__, default=lambda o: o.__dict__, indent=4)



        print("ok")

