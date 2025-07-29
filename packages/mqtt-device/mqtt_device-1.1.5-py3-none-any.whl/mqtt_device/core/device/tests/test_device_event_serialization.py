import unittest
from datetime import datetime

import pytz

from mqtt_device.common.common_log import basic_config_log
from mqtt_device.core.device.event import LeverEvent


class TestEventDeviceSerialization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        basic_config_log()

    def test(self):
        date_str = "2024-07-31 11:39:51+02:00"
        date = datetime.fromisoformat(date_str)
        timezone = pytz.timezone('Europe/Paris')
        dt_object = date.astimezone(tz=timezone)


        event = LeverEvent(id_device="lever_1", date=date)

        json_str = event.serialize()

        event2 = LeverEvent.deserialize(json_str)

        # other = LeverEvent()
        # other.deserialize(json_str)




        print("ok")