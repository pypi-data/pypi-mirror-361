import logging
import unittest
from unittest.mock import MagicMock

from mqtt_device.core.device.local.device import LocalDevice
from mqtt_device.core.device.local import LocalClient
from mqtt_device.core.device.remote import RemoteDevice


class TestLocalClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.root.setLevel(logging.DEBUG)

    # visual type check
    def test_local_client_type_check(self):

        lc = LocalClient(environment_name='local', id_env='local_id', client_id='local_client', mqtt_client=MagicMock())

        # should be in warning below
        lc.devices.add(RemoteDevice(device_id="my_id"))
        # should be ok
        lc.devices.add(LocalDevice(device_id="my_id"))
