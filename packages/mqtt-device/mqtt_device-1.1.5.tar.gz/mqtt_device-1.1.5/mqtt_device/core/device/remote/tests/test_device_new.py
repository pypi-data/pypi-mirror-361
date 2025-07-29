import unittest
from logging import DEBUG
from typing import Dict, Collection

from mqtt_device.core.client.mqtt_client import MQTTClient, IMQTTClient, MessageReceivedEvent

from mqtt_device.common.tests.test_client_with_device_providers import IDeviceProvider, T_DEVICE
from mqtt_device.core.device import DeviceProperty

from mqtt_device.common.common_log import basic_config_log

from mqtt_device.event_listener.listener import EventHandler
from mqtt_device.core.device.remote import IDeviceNew, DeviceNew, RemoteDeviceNew, Gateway


class MyDevice(DeviceNew):


    def declare_properties(self):
        prop = DeviceProperty(property_name="activate", datatype="str", settable=True, retention=False)
        # res.append(prop)
        self.add_property(prop)


    # def get_properties(self) -> List[DeviceProperty]:
    #     res = list()
    #
    #     prop = DeviceProperty(property_name="activate", datatype="str", settable=True, retention=False)
    #     res.append(prop)
    #
    #     return res

class FakeMQTT(IMQTTClient):

    def __init__(self):
        self._message_received_event: EventHandler[MessageReceivedEvent] = EventHandler(self)

    @property
    def message_received(self) -> EventHandler[MessageReceivedEvent]:
        return self._message_received_event


class FakeDeviceProvider(IDeviceProvider):

    def __init__(self):
        self._devices: Dict[str, T_DEVICE] = dict()

    def add_device(self, device: T_DEVICE):
        self._devices[device.device_id] = device

    def get_device(self, device_id: str) -> T_DEVICE:
        return self._devices[device_id]

    def get_devices(self) -> Collection[T_DEVICE]:
        return self._devices.values()

    def device_added(self) -> EventHandler['DeviceAddedEvent']:
        pass


class TestDeviceNew(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        basic_config_log(level=DEBUG)

    def test_something(self):
        provider = FakeDeviceProvider()
        fake_mqtt: MQTTClient = FakeMQTT()

        gateway = Gateway(device_providers=provider, mqtt_client=fake_mqtt)
        # client = ApplicationClient(environment_name="env", id_env="01", client_id="app_client", mqtt_client=MagicMock())
        # #
        # interpretor.client = client

        device = MyDevice(device_id="my_device", device_type="windows", location="somewhere")

        remote = RemoteDeviceNew(device=device, gateway=gateway)
        # client.add_remote_client(RemoteClient(environment_name="souris_city", id_env="01", client_id="my_client"))

        prop = device.get_property("activate")
        prop._set_str_value("ON")

        # interpretor.process(RawTopic(topic_str="souris_city/01/my_client/my_device", payload="kikoo"))

    def test_gateway(self):
        provider = FakeDeviceProvider()
        fake_mqtt: MQTTClient = FakeMQTT()

        gateway = Gateway(device_providers=provider, mqtt_client=fake_mqtt)

        fake_mqtt.message_received(MessageReceivedEvent(topic_str="env/01/client/$connected", payload="kikoo"))
    # def test(self):
    #     client ) ApplicationClient

if __name__ == '__main__':
    unittest.main()
