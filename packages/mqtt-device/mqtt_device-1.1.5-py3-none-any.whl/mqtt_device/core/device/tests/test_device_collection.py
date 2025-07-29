import unittest

from mqtt_device.common.common_log import basic_config_log
from mqtt_device.core.device import Device
from mqtt_device.core.device import DeviceCollection
from mqtt_device.core.device.local import FakeLeverLocal, FakeLocalBeam

class TestRemoteClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        basic_config_log()

    def test_device_collection(self):
        lever_1 = FakeLeverLocal(device_id="lever_1")
        lever_2 = FakeLeverLocal(device_id="lever_2")
        beam_1 = FakeLocalBeam(device_id="beam_1")
        beam_2 = FakeLocalBeam(device_id="beam_2")

        dc = DeviceCollection([lever_1, lever_2, beam_1, beam_2])

        # search by id with result
        res = dc.get_by_id("lever_1")
        self.assertIsNotNone(res)

        # search unknown id
        res = dc.get_by_id("lever_789")
        self.assertIsNone(res)

        # search by type
        res = dc.get_by_type("levers")
        self.assertEqual(2, len(res))

        # test iter
        cpt = 0
        for device in dc:
            cpt += 1
            self.assertIsInstance(device, Device)

        self.assertEqual(cpt, 4)



    def test_add_existing_device(self):

        lever = FakeLeverLocal(device_id="lever_2")
        beam = FakeLocalBeam(device_id="beam_1")

        dc = DeviceCollection([lever, beam])

        lever = FakeLeverLocal(device_id="lever_2")
        dc.add(lever)

        self.assertEqual(2, len(dc))