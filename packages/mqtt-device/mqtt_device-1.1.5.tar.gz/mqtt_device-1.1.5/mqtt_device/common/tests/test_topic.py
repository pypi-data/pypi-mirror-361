import logging
import socket
import unittest
from unittest.mock import MagicMock

# from mqtt_device.client.client_old import LocalClient, RemoteClient
# from mqtt_device.client.client import RemoteClient
# from mqtt_device.local.client import LocalClient
# from mqtt_device.remote.client import ApplicationClient
# # from mqtt_device.client.topic import TopicInterpretor, RawTopic, CommonTopic, \
# #     TopicInterpretorV2  # SystemDeviceTopic
# # from mqtt_device.device.lever import Lever
# from mqtt_device.client.topic import RawTopic
# from mqtt_device.device.device_new import RemoteDevice, DeviceProperty, LocalDevice
from mqtt_device.core.topic import ClientTopic, RawTopic
from mqtt_device.core.device.local import LocalClient
from mqtt_device.core.device.local.device import LocalDevice
from mqtt_device.core.device import DeviceProperty
from mqtt_device.core.device.remote import ApplicationClient, RemoteClient
from mqtt_device.core.device.remote import RemoteDevice
from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer

mosquitto: FakeMosquittoServer = None
local_ip: str = None

class FakeClient(LocalClient):
    pass


class TestTopicNew(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global local_ip

        logging.root.setLevel(logging.DEBUG)

        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)

    def test_topic_nb_levels(self):

        # from mqtt_device.client.topic import ClientTopic, RawTopic

        topic_str = "SocialCage/01/STM01/$connected"
        topic = ClientTopic(raw_topic=RawTopic(topic_str))

        self.assertEqual(3, topic.nb_levels)
        self.assertEqual("$connected", topic.meta_field)

        topic_str = "SocialCage/01/STM01/lever_1/state"
        topic = ClientTopic(raw_topic=RawTopic(topic_str))
        self.assertEqual(5, topic.nb_levels)
        self.assertIsNone(topic.meta_field)

    def test_local_client_interpretor_client_connection(self):

        mqtt_mock = MagicMock()
        local_client = LocalClient(environment_name="MyEnv", id_env="01", client_id="LOCAL", mqtt_client=mqtt_mock)

        interp = local_client._topic_interpretor

        # notify mqtt client is connected
        interp.on_client_connected(local_client)

        mqtt_mock.publish_topic.assert_called_with(payload='True', qos=2, retain=True, topic='MyEnv/01/LOCAL/$connected')

    def test_local_client_interpretor_add_local_device(self):

        mqtt_mock = MagicMock()
        local_client = LocalClient(environment_name="MyEnv", id_env="01", client_id="LOCAL", mqtt_client=mqtt_mock)

        device = LocalDevice(device_id="My_Device", device_type="lever")
        local_client.add_device(device)

        mqtt_mock.publish_topic.assert_called_with(payload='lever', qos=2, retain=True, topic='MyEnv/01/LOCAL/My_Device/$type')

    def test_local_client_interpretor_add_device_property(self):

        mqtt_mock = MagicMock()
        local_client = LocalClient(environment_name="MyEnv", id_env="01", client_id="LOCAL", mqtt_client=mqtt_mock)

        device = LocalDevice(device_id="My_Device", device_type="lever")
        device.add_property(DeviceProperty(property_name="My Prop", datatype="float", settable="True"))
        local_client.add_device(device)

        mqtt_mock.publish_topic.any_call(payload='float', qos=2, retain=True, topic='MyEnv/01/LOCAL/My_Device/My Prop/$datatype')
        mqtt_mock.publish_topic.any_call(payload='True', qos=2, retain=True, topic='MyEnv/01/LOCAL/My_Device/My Prop/$settable')
        mqtt_mock.subscribe_topic.any_call(topic='MyEnv/01/LOCAL/My_Device/My Prop/set')

    def test_local_client_device_property_set_value_changed_publish_topic(self):

        mqtt_mock = MagicMock()
        local_client = LocalClient(environment_name="MyEnv", id_env="01", client_id="LOCAL", mqtt_client=mqtt_mock)

        device = LocalDevice(device_id="My_Device", device_type="lever")
        prop = DeviceProperty(property_name="My Prop", datatype="float", settable="True")
        device.add_property(prop)

        local_client.add_device(device)

        prop._set_str_value("1879.256")

        mqtt_mock.publish_topic.any_call(payload=1879.256, qos=2, retain=False, topic='MyEnv/01/LOCAL/My_Device/My Prop')

    def test_local_client_process_set_property(self):

        mqtt_mock = MagicMock()
        local_client = LocalClient(environment_name="MyEnv", id_env="01", client_id="LOCAL", mqtt_client=mqtt_mock)

        interp = local_client._topic_interpretor

        device = LocalDevice(device_id="My_Device", device_type="lever")
        prop = DeviceProperty(property_name="My Prop", datatype="float", settable="True")
        device.add_property(prop)

        local_client.add_device(device)

        interp.process(RawTopic(topic_str="MyEnv/01/LOCAL/My_Device/My Prop/set", payload="789.65"))

        self.assertEqual(789.65, prop.value)

    def test_app_client_interpretor_add_remote_client(self):

        client = ApplicationClient(environment_name="ENV", id_env="ID_ENV", client_id="APP", mqtt_client=MagicMock())
        interp = client._topic_interpretor

        interp.on_message_received(sender=client, topic="ENV/ID_ENV/client/$connected", message="true")

        res = client.get_remote_client(env_name="ENV", env_id="ID_ENV", client_id="client")

        self.assertIsNotNone(res)

    def test_app_client_interpretor_remote_device_set_location(self):

        client = ApplicationClient(environment_name="ENV", id_env="ID_ENV", client_id="APP", mqtt_client=MagicMock())
        interp = client._topic_interpretor

        remote_client = RemoteClient(environment_name="ENV", id_env="ID_ENV", client_id="client")
        client.add_remote_client(remote_client)
        remote_device = RemoteDevice(device_id="device", device_type="sometype")
        remote_client.add_remote_device(remote_device)

        interp.on_message_received(sender=client, topic="ENV/ID_ENV/client/device/$location", message="tokyo")
        res = remote_client.get_remote_device("device")

        self.assertEqual("tokyo", res.location)

    def test_app_client_interpretor_add_remote_device(self):

        mock_mqtt = MagicMock()
        client = ApplicationClient(environment_name="ENV", id_env="ID_ENV", client_id="APP", mqtt_client=mock_mqtt)
        interp = client._topic_interpretor

        remote_client = RemoteClient(environment_name="ENV", id_env="ID_ENV", client_id="client")
        client.add_remote_client(remote_client)

        interp.on_message_received(sender=mock_mqtt, topic="ENV/ID_ENV/client/device/$type", message="sometype")

        res = client.get_remote_device(env_name="ENV", env_id="ID_ENV", client_id="client", device_id="device")

        self.assertIsNotNone(res)

    def test_app_client_interpretor_add_device_property(self):

        mock_mqtt = MagicMock()
        client = ApplicationClient(environment_name="ENV", id_env="ID_ENV", client_id="APP", mqtt_client=mock_mqtt)
        interp = client._topic_interpretor

        remote_client = RemoteClient(environment_name="ENV", id_env="ID_ENV", client_id="client")
        client.add_remote_client(remote_client)
        remote_device = RemoteDevice(device_id="device", device_type="sometype")
        remote_client.add_remote_device(remote_device)


        interp.on_message_received(sender=mock_mqtt, topic="ENV/ID_ENV/client/device/my_prop/$datatype", message="boolean")

        res = remote_device.get_property("my_prop")
        self.assertIsNotNone(res)


if __name__ == '__main__':
    unittest.main()
