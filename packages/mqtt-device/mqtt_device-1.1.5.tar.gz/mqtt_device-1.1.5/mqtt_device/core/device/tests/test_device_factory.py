import json
import logging
import unittest

from mqtt_device.core.device.device_factory import DeviceFactory, LocalDeviceFactory, RemoteDeviceFactory
from mqtt_device.core.device.local.local_device import LocalDevice
from mqtt_device.core.device.remote.remote_device import RemoteLever
from mqtt_device.device.fake_common_local_device import FakeLeverLocal


class TestDeviceFactory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.root.setLevel(logging.DEBUG)


    def test_serialization_device(self):
        with open("./resources/device_lever_1.json", 'r') as file:
            json_str = file.read()


        res = RemoteLever.deserialize(json_str)

        # lever = RemoteLever(device_id="my_remote_lever")

        # json_str = lever.serialize()

        print("ok")



    def test_local_device_factory(self):

        lever = FakeLeverLocal(device_id="my_device", device_type="levers")
        factory: LocalDeviceFactory = LocalDeviceFactory()

        # with existings type
        res = factory.instantiate(lever.toDict()).as_type(FakeLeverLocal)
        self.assertIsNotNone(res)

        # with unknown type
        unknown_str = """{
            "device_id": "my_unknown_device",
            "type": "kikoo",
            "location": "",
            "properties": []
        }"""

        json_dict = json.loads(unknown_str)

        with self.assertRaises(Exception):
            res = factory.instantiate(json_dict)


        print("ok")

    def test_remote_device_factory(self):
        factory = RemoteDeviceFactory()
