import logging
import unittest

from mqtt_device.core.client.client import BaseClient
from mqtt_device.core.device.remote import RemoteDevice


class TestBaseClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.root.setLevel(logging.INFO)

    def test_add_device(self):
        client: BaseClient[RemoteDevice] = BaseClient(environment_name="my_env", id_env="my_id", client_id="my_client")
        client.add_device(RemoteDevice(device_id="lever_1", device_type="levers", location="here"))
        client.add_device(RemoteDevice(device_id="beam_1", device_type="beams", location="there"))

        self.assertEqual(2, len(client.devices))
