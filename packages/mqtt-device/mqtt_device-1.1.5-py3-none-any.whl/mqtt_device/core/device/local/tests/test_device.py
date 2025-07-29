import logging
import socket
import unittest
from unittest.mock import MagicMock

from mqtt_device.common.exception import DeviceException
from mqtt_device.core.device.local import LocalClient
from mqtt_device.core.device.local.device import LocalDevice
from mqtt_device.core.device import DeviceProperty
from mqtt_device.core.device.remote import RemoteClient
from mqtt_device.core.device.remote import RemoteDevice
from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer

mosquitto: FakeMosquittoServer = None
local_ip: str = None

class TestDevice(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     logging.root.setLevel(logging.INFO)

    @classmethod
    def setUpClass(cls):
        global local_ip

        logging.root.setLevel(logging.INFO)
        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)

    # def test_local_device_set_property_publish_topic_TO_FINISH(self):
    #
    #     mqtt_client = MagicMock()
    #
    #     local_client = LocalClient(environment_name="My XP", id_env="01", client_id="My local client", mqtt_client=mqtt_client)
    #     device = LocalDevice(device_id="My local device", device_type="some_type")
    #     device_prop = DeviceProperty(property_name="my_prop", datatype="boolean", settable=True)
    #     device.add_properties(device_prop)
    #
    #     def on_new_val(sender: DeviceProperty, old_val, new_val):
    #         print("NEW VAL")
    #
    #     device_prop.value_changed += on_new_val
    #
    #     device_prop.value = True

    # def test_remote_device_property_receive_new_value(self):
    #     mock_mqtt = MagicMock()
    #
    #     local_client = LocalClient(environment_name="ENV", id_env="ENV ID", client_id="Client", mqtt_client=mock_mqtt)
    #     remote_client = RemoteClient(environment_name="RENV", id_env="01", client_id="Remote Client")
    #     remote_device = RemoteDevice(device_id="Remote", device_type="lever")
    #     remote_prop = DeviceProperty(property_name="some_prop", datatype="float", settable=True)


    def test_remote_device_property_set_value_send_topic(self):
        mock_mqtt = MagicMock()

        local_client = LocalClient(environment_name="ENV", id_env="ENV ID", client_id="Client", mqtt_client=mock_mqtt)
        remote_client = RemoteClient(environment_name="RENV", id_env="01", client_id="Remote Client")
        remote_device = RemoteDevice(device_id="Remote", device_type="lever")
        remote_prop = DeviceProperty(property_name="some_prop", datatype="float", settable=True)

        # local_client.add_remote_client(remote_client)
        remote_client.add_device(remote_device)

        remote_device.add_property(remote_prop)

        remote_prop.value = 16458.2

        mock_mqtt.publish_topic.assert_called_with(payload=16458.2, qos=2, retain=False, topic='ENV/01/Remote_Client/Remote/some_prop/set')

        # call.publish_topic(payload=16458.2, qos=2, retain=False, topic='RENV/01/Remote_Client/Remote/some_prop/set')

        # print("OK")






        remote_prop.value = 456.865

    def test_remote_device_status_connexion_changed_throw_events(self):

        local_client = LocalClient(environment_name="ENV", id_env="ENV ID", client_id="Client", mqtt_client=MagicMock())

        remote_client = RemoteClient(environment_name="RENV", id_env="01", client_id="Remote Client")

        # add two remote devices
        remote_device = RemoteDevice(device_id="Remote", device_type="lever")
        cb_1 = MagicMock()
        remote_device.connexion_status_changed += cb_1
        remote_client.add_remote_device(remote_device)
        cb_2 = MagicMock()
        remote_device.connexion_status_changed += cb_2

        remote_device = RemoteDevice(device_id="Remote 2", device_type="lever")
        remote_client.add_remote_device(remote_device)

        local_client.add_remote_client(remote_client)

        remote_client.is_connected = False
        remote_client.is_connected = True

        self.assertEqual(2, cb_1.call_count)
        self.assertEqual(2, cb_2.call_count)




    def test_local_device_publish_autodescription(self):

        # mosquitto = FakeMosquittoServer(ip=local_ip)
        # mosquitto.start()

        mqtt_client = MagicMock()

        local_client = LocalClient(environment_name="My XP", id_env="01", client_id="My local client", mqtt_client=mqtt_client)
        device = LocalDevice(device_id="My local device", device_type="some_type")
        device.add_property(DeviceProperty(property_name="my_prop", datatype="boolean", settable=True))

        local_client.add_device(device)

        # expected
        mqtt_client.publish_topic.assert_any_call(topic='My_XP/01/My_local_client/My_local_device/$type', payload='some_type', qos=2, retain=True)
        mqtt_client.publish_topic.assert_any_call(topic='My_XP/01/My_local_client/My_local_device/my_prop/$datatype', payload='boolean', qos=2, retain=True)
        mqtt_client.publish_topic.assert_any_call(topic='My_XP/01/My_local_client/My_local_device/my_prop/$settable', payload='True', qos=2, retain=True)

        prop = device.get_property("my_prop")
        self.assertIsNotNone(prop)
        self.assertTrue(prop.settable)
        self.assertEqual("boolean", prop.datatype)

    def test_local_device_home_topic(self):

        local_client = LocalClient(environment_name="My XP", id_env="01", client_id="My local client", mqtt_client=MagicMock())
        device = LocalDevice(device_id="My local device")
        device._client = local_client

        expected = "My_XP/01/My_local_client/My_local_device"
        self.assertEqual(expected, device.home_topic)

    def test_DeviceProperty_boolean(self):

        propert = DeviceProperty(property_name="my_prop", datatype="boolean")

        with self.assertRaises(DeviceException):
            propert._set_str_value("truez")

        propert._set_str_value("false")
        self.assertFalse(propert.value)
        propert._set_str_value("true")
        self.assertTrue(propert.value)

    def test_DeviceProperty_float(self):

        propert = DeviceProperty(property_name="my_prop", datatype="float")

        propert._set_str_value("0.123")
        self.assertEqual(0.123, propert.value)

