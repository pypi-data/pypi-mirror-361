import logging
import unittest
from threading import Thread
from time import sleep
from unittest.mock import MagicMock

from mqtt_device.core.device.remote import ApplicationClient, RemoteClient
from mqtt_device.core.device.remote import RemoteDevice

class FakeDevice1(RemoteDevice):

    DEVICE_TYPE = "fake_device_1"

    def fake_method(self):
        pass

class FakeDevice2(RemoteDevice):

    DEVICE_TYPE = "fake_device_2"

    def fake_method_2(self):
        pass

def create_test_app_client() -> ApplicationClient:

    app_client = ApplicationClient(environment_name="my_xp", id_env="01", client_id="my_client",
                                   mqtt_client=MagicMock())

    client_1 = RemoteClient(environment_name="my_xp", id_env="01", client_id="client_1")
    app_client.add_remote_client(client_1)
    device_1 = FakeDevice1(device_id="fake_device_1", location="room_1")
    client_1.add_remote_device(device_1)
    device_2 = FakeDevice1(device_id="fake_device_2", location="room_2")
    client_1.add_remote_device(device_2)

    client_2 = RemoteClient(environment_name="my_xp", id_env="01", client_id="client_2")
    app_client.add_remote_client(client_2)
    device_3 = FakeDevice2(device_id="fake_device_3", location="room_3")
    client_2.add_remote_device(device_3)

    return app_client

class TestApplicationClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.root.setLevel(logging.DEBUG)

    def test_get_remote_device_by_device_id(self):

        app_client = create_test_app_client()

        res = app_client.get_remote_device(device_id="fake_device_1")
        self.assertEqual("fake_device_1", res.device_id)

        res = app_client.get_remote_device(device_id="fake_device_4")
        self.assertIsNone(res)

        res = app_client.get_remote_device(device_id="fake_device_3")
        self.assertEqual("fake_device_3", res.device_id)

    def test_remote_device_as_type(self):

        app_client = create_test_app_client()
        res = app_client.get_remote_device(device_id="fake_device_1").as_type(FakeDevice2)
        self.assertIsNone(res)

        res = app_client.get_remote_device(device_id="fake_device_1").as_type(FakeDevice1)
        self.assertIsInstance(res, FakeDevice1)

    def test_wait_for_get_remote_client(self):

        app_client = ApplicationClient(environment_name="my_xp", id_env="01", client_id="my_client", mqtt_client=MagicMock())

        app_client.connect()

        def run_test():
            # delay the add of the client
            sleep(1)
            remote_client = RemoteClient(environment_name="some_env", id_env="some_id", client_id="some_client")
            app_client.add_remote_client(remote_client)
            print("KIKOO")

        thread = Thread(target=run_test)
        thread.start()

        remote_client = app_client.get_remote_client(client_id="some_client", timeout=2)

        self.assertIsNotNone(remote_client)

