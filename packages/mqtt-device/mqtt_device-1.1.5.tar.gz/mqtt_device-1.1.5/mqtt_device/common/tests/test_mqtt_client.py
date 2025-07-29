import logging
import socket
import unittest
from time import sleep
from unittest.mock import Mock, MagicMock

from mqtt_device.common.exception import DeviceException
from mqtt_device.core.client.mqtt_client import MQTTClient
from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer

mosquitto: FakeMosquittoServer = None
local_ip: str = None


def run_client(ip: str):
    client = MQTTClient(client_id="My Client", broker_ip=ip, keep_alive=1)
    client.connect()
    sleep(10)



class TestMQTTClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global local_ip
        logging.root.setLevel(logging.DEBUG)

        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)


    def tearDown(self):
        if mosquitto:
            mosquitto.kill()

    def test_connect_success(self):

        mosquitto = FakeMosquittoServer(ip=local_ip)
        mosquitto.start()

        client = MQTTClient(client_id="My Client", broker_ip=local_ip)
        mock_cv_connect = MagicMock()
        client.connected += mock_cv_connect

        client.connect()
        mock_cv_connect.assert_called_once_with(client)

    def test_connection_fail(self):

        client = MQTTClient(client_id="My Client", broker_ip=local_ip)
        client._try_to_connect = Mock()

        # connexion negative attempts end by an exception
        with self.assertRaises(DeviceException):
            client.connect()

    def test_stop_send_disconnect_event(self):

        mosquitto = FakeMosquittoServer(ip=local_ip)
        mosquitto.start()

        client = MQTTClient(client_id="My Client", broker_ip=local_ip)
        mock_cv_disconnect = MagicMock()
        client.disconnected += mock_cv_disconnect
        client.connect()

        # close connexion
        mosquitto.kill()

        mock_cv_disconnect.assert_called_once_with(client)


    def test_wait_terminated_with_timeout(self):

        mosquitto = FakeMosquittoServer(ip=local_ip, verbose=True)
        mosquitto.start()

        client = MQTTClient(client_id="My Client", broker_ip=local_ip, keep_alive=1)
        client.connect()

        # test without timeout
        client.stop()
        is_not_timeout = client.wait_until_ended(timeout=0.5)
        self.assertTrue(is_not_timeout)

        # test with ended by timeout
        client.connect()
        is_not_timeout = client.wait_until_ended(timeout=0.5)
        self.assertFalse(is_not_timeout)

    def test_will_set_testament_event(self):

        mosquitto = FakeMosquittoServer(ip=local_ip, verbose=True)
        mosquitto.start()

        last_will_topic = 'hello/will'
        # create a client with a last will
        client_1 = MQTTClient(client_id="My Client", broker_ip=local_ip, keep_alive=1)
        client_1.will_set(topic=last_will_topic, payload='Last will', qos=2, retain=False)  # , 0, False)

        # create a second client subscribing to last will
        client_2 = MQTTClient(client_id="My Client 2", broker_ip=local_ip)

        client_1.connect()
        client_2.connect()

        # subscribe to LW
        client_2.subscribe_topic(topic=last_will_topic)

        # interrupt connexion in dirty way
        client_1._mqtt_client.loop_stop()

        mock_cb_on_message = MagicMock()
        client_2.message_received += mock_cb_on_message
        client_2.message_received += lambda client, topic, message: client_2.stop()

        is_not_timeout = client_2.wait_until_ended(timeout=5)

        # check not ended by timeout
        self.assertTrue(is_not_timeout)
        mock_cb_on_message.assert_called_once_with(client_2, message='Last will', topic=last_will_topic)


if __name__ == '__main__':
    unittest.main()
