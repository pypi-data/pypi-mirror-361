import datetime
import json
import logging
import unittest
from unittest.mock import MagicMock



# class VideoMouseTracker(BaseMouseTracker):
#
#     def __init__(self):
#         self._logger = create_logger(self)
#
#     @property
#     def logger(self) -> Logger:
#         return self._logger
from mqtt_device.core.device.local.device import BaseMouseTracker

import mqtt_device
from mqtt_device.core.device import DeviceProperty
# from mqtt_device.local.device import BaseMouseTracker
from mqtt_device.core.device.remote import MouseTrackerDevice


class FakeMouseTrack(BaseMouseTracker):

    def __init__(self, nb_frames: int):
        self.nb_frames = nb_frames

    def start(self):
        for cpt in range(1, self.nb_frames+1):

            frame = mqtt_device.device.mouse_tracker_device.MouseTrackFrame(timestamp=cpt, center_of_mass=(cpt, cpt + 1), nose_pt=(cpt * 10, cpt * 10 + 1), tail_pt=(cpt * 100, cpt * 100 + 1))
            self.frame_received(frame)



class TestRemoteMouseTracker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # global local_ip

        logging.root.setLevel(logging.INFO)
        # # get the host ip
        # host_name = socket.gethostname()
        # local_ip = socket.gethostbyname(host_name)




    def test_remote_mouse_tracker_json_frame_received(self):

        mock_client = MagicMock()

        device = MouseTrackerDevice(device_id="tracker_1", device_type="mouse_tracker")
        device._client = mock_client

        device_property = DeviceProperty(property_name="track_frame", datatype="str")
        device.add_property(device_property)

        mock_cb = MagicMock()

        device.frame_received += mock_cb
        ts = datetime.datetime.now().timestamp()

        payload = {
            "timestamp": ts,
            "center_of_mass": (100, 123),
            "nose_pt": (45, 46),
            "tail_pt": (789, 456)
        }

        data_out = json.dumps(payload)

        # simulate a json frame
        device_property._set_value(data_out)

        expected = device._create_mouse_track_frame_from_json(data_out)
        mock_cb.assert_called_with(device, expected)



if __name__ == '__main__':
    unittest.main()
