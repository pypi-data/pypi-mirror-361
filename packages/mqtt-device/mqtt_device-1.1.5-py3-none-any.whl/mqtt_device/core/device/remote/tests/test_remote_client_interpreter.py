import logging
import unittest
from unittest.mock import MagicMock

from mqtt_device.core.device.device_property import DeviceProperty
from mqtt_device.core.device.remote.remote_client import ApplicationClient, RemoteClient
from mqtt_device.core.device.remote.remote_device import RemoteDevice
from mqtt_device.core.topic.remote_topic_interpreter import ApplicationClientTopicInterpreter
from mqtt_device.core.topic.topic import DeviceTopic, RawTopic

json_sample = """
{
    "type": "microwave",
    "location": "cagibi",
    "properties": [
        {
            "name": "temperature",
            "datatype": "float",
            "settable": true,
            "retain": true
        },
        {
            "name": "hygrometry",
            "datatype": "float",
            "settable": false,
            "retain": false
        },
        {
            "name": "brand",
            "datatype": "str",
            "static": true,
            "static_value": "philips"
        }
    ]
}
"""
class TestRemoteClientInterpreter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.root.setLevel(logging.DEBUG)

    def test_process_remote_device(self):
        mock_mqtt = MagicMock()
        client = ApplicationClient(environment_name="env", id_env="01", client_id="my client", mqtt_client=mock_mqtt)

        interpretor = ApplicationClientTopicInterpreter()
        interpretor.client = client

        remote_client = RemoteClient(environment_name="env", id_env="01", client_id="client")
        client.add_remote_client(remote_client)

        topic = "env/01/client/My_Device/$meta"
        payload = json_sample

        device_topic = DeviceTopic(raw_topic=RawTopic(topic_str=topic, payload=payload))
        interpretor._process_device_topic(device_topic)

    def test_process_client_topic_connection_status(self):
        mock_mqtt = MagicMock()
        # interpretor = ApplicationClientTopicInterpreter()

        client = ApplicationClient(environment_name="env", id_env="01", client_id="my client", mqtt_client=mock_mqtt)#, interpreter=interpretor)


        remote_client = RemoteClient(environment_name="env", id_env="01", client_id="some_client")
        client.add_remote_client(remote_client)

        interpretor = client._topic_interpretor

        remote_device = RemoteDevice(device_id="one")
        remote_client.add_device(remote_device)

        # def on_status_changed(sender: RemoteDevice, new_status: bool):
        #     print('STATUS')
        mock_on_status_changed = MagicMock()
        remote_device.connexion_status_changed += mock_on_status_changed


        topic = "env/01/some_client/$connected"

        raw_topic = RawTopic(topic_str=topic, payload="False")
        interpretor.process(raw_topic)

        # call(<mqtt_device.remote.device.device.RemoteDevice object at 0x000002414D12A040>, False)
        mock_on_status_changed.assert_called_with(remote_device, False)

        # print("kikoo")


    def test_process_client_topic_create_remote_client(self):

        mock_mqtt = MagicMock()

        # interpretor = ApplicationClientTopicInterpreter()
        # interpretor.client = client

        client = ApplicationClient(environment_name="env", id_env="01", client_id="my client", mqtt_client=mock_mqtt)

        interpretor = client._topic_interpretor
        topic = "env/01/client/$connected"

        raw_topic = RawTopic(topic_str=topic, payload="True")
        interpretor.process(raw_topic)

        expected = RemoteClient(environment_name="env", id_env="01", client_id="client")
        remote_client = client.get_remote_client("client")
        self.assertEqual(expected, remote_client)

    def test_process_device_topic_create_device(self):

        mock_mqtt = MagicMock()
        client = ApplicationClient(environment_name="env", id_env="01", client_id="my client", mqtt_client=mock_mqtt)
        interpretor = client._topic_interpretor

        remote_client = RemoteClient(environment_name="env", id_env="01", client_id="client")
        client.add_remote_client(remote_client)

        topic = "env/01/client/My_Device/$meta"
        payload = json_sample

        # def on_device_added(sender: RemoteClient, device: IDevice):
        #     print("ADDED!")
        #
        # remote_client.device_added += on_device_added

        raw_topic = RawTopic(topic_str=topic, payload=payload)
        interpretor.process(raw_topic)


        remote_device = remote_client.get_device(device_id="My_Device")

        expected = RemoteDevice(device_id="My_Device", device_type="microwave")
        expected._client = remote_client

        self.assertEqual(expected, remote_device)


    def test_property_device_topic_create_property(self):

        mock_mqtt = MagicMock()
        client = ApplicationClient(environment_name="env", id_env="01", client_id="my client", mqtt_client=mock_mqtt)
        interpretor = client._topic_interpretor

        remote_client = RemoteClient(environment_name="env", id_env="01", client_id="client")
        client.add_remote_client(remote_client)
        remote_device = RemoteDevice(device_id="device", device_type="microwave")
        remote_client.add_device(remote_device)

        topic = "env/01/client/device/temperature/$meta"
        payload = '{"datatype": "float", "settable": true, "retain": true}'

        raw_topic = RawTopic(topic_str=topic, payload=payload)
        interpretor.process(raw_topic)

        expected = DeviceProperty(property_name="temperature", datatype="float", settable=True, retention=True)
        expected.device = remote_device

        prop = remote_device.get_property("temperature")

        self.assertEqual(expected, prop)







