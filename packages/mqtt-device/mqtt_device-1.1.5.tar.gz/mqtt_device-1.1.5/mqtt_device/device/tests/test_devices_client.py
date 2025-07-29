import logging
import unittest
from unittest.mock import Mock


# from tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer
from mqtt_device.common import create_fake_type
from mqtt_device.client.client_OLD import Client, DeviceException
from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer
from mqtt_device.core.device.local import DevicesClient
from mqtt_device.core.device.local import LocalDevice


class TestDevicesClientNew(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.root.setLevel(logging.INFO)

    def test_multiple_device_on_one_client(self):

        client = DevicesClient(client_id="My Client")

        fake_device_type = create_fake_type(LocalDevice)
        fake_device_type.group_type = Mock(return_value="bottles")
        fake_device = fake_device_type(location="cellar", device_id="first_device")

        client.device = fake_device

    def test_device_received_set_remote_request(self):
        mosquitto = FakeMosquittoServer()
        mosquitto.start()

        # create devices client and set his device to a fake one
        device_client = DevicesClient(client_id="MyClient")

        fake_device_type = create_fake_type(LocalDevice)
        fake_device_type.group_type = Mock(return_value="showers")
        fake_device = fake_device_type(location="bathroom", device_id="showers")
        fake_device.before_set = Mock(return_value=True)

        device_client.device = fake_device
        device_client.connect("127.0.0.1")

        mosquitto.send_message(topic=f"{fake_device.device_home_topic}/set", message="HELLO")

        # check before_set has been called and value have changed
        fake_device.before_set.assert_called_once_with(value="HELLO")
        self.assertEqual("HELLO", fake_device.value)



    def test_DevicesClient_set(self):

        mosquitto = FakeMosquittoServer()
        mosquitto.start()

        client = DevicesClient(client_id="My Client")

        fake_device_type = create_fake_type(LocalDevice)
        fake_device_type.group_type = Mock(return_value="bottles")
        fake_device = fake_device_type(location="cellar", device_id="red_wine")

        client.device = fake_device
        client.connect("127.0.0.1")

        # send set message
        mosquitto.send_message(topic=f"{fake_device.device_home_topic}/set", message="25")
        self.assertEqual("25", fake_device.value)
        mosquitto.send_message(topic=f"{fake_device.device_home_topic}/set", message="52")
        self.assertEqual("52", fake_device.value)

        mosquitto.kill()

    def test_connect_fail_max_nb_attempts(self):

        fake_client_type = create_fake_type(Client)
        client = fake_client_type(client_id="MyClient")
        client._max_attempt = 3

        client._try_to_connect = Mock(return_value=False)

        with self.assertRaises(DeviceException):
            client.connect("127.0.0.1")

        self.assertEqual(client._max_attempt, client._try_to_connect.call_count)

    def test_connect_success(self):

        mosquitto = FakeMosquittoServer()
        mosquitto.start()

        fake_client_type = create_fake_type(Client)
        client = fake_client_type(client_id="MyClient")

        self.assertFalse(client.is_connected)
        client.connect("127.0.0.1")
        self.assertTrue(client.is_connected)
