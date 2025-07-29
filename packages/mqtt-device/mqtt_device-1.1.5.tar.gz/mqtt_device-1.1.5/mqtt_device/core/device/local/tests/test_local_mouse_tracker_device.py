import json
import logging
import unittest
from threading import Thread
from time import sleep
from unittest.mock import MagicMock

# import mqtt_device.device.mouse_tracker_device
# from mqtt_device.device.mouse_tracker_device import MouseTrackFrame, BaseMouseTracker, LocalMouseTrackerDevice
# from mqtt_device.client.client import LocalClient
# from mqtt_device.device.device_new import DeviceProperty


# class VideoMouseTracker(BaseMouseTracker):
#
#     def __init__(self):
#         self._logger = create_logger(self)
#
#     @property
#     def logger(self) -> Logger:
#         return self._logger
import mqtt_device
from mqtt_device.core.device.local import LocalClient
from mqtt_device.core.device.local.device import BaseMouseTracker, LocalMouseTrackerDevice


class FakeMouseTrack(BaseMouseTracker):

    def __init__(self, nb_frames: int):
        self.nb_frames = nb_frames

    def start(self):

        thread = Thread(target=self._start, name="fake mouse tracker")
        thread.start()


    def _start(self):
        for cpt in range(1, self.nb_frames+1):

            frame = mqtt_device.core.device.local.device.mouse_tracker_device.MouseTrackFrame(timestamp=cpt, center_of_mass=(cpt, cpt + 1), nose_pt=(cpt * 10, cpt * 10 + 1), tail_pt=(cpt * 100, cpt * 100 + 1))
            self.frame_received(frame)




class TestLocalMouseTracker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # global local_ip

        logging.root.setLevel(logging.INFO)
        # # get the host ip
        # host_name = socket.gethostname()
        # local_ip = socket.gethostbyname(host_name)

    def test_wait_for_end(self):

        mock_mouse_tracker = MagicMock()
        local = LocalMouseTrackerDevice(mouse_tracker=mock_mouse_tracker, device_id="tracker_1")

        def stop():
            sleep(0.5)
            local.stop()

        thread = Thread(target=stop)
        thread.run()

        local.run()


    def test_track_frame_send_event(self):

        mouse_tracker = FakeMouseTrack(nb_frames=2)
        local = LocalMouseTrackerDevice(mouse_tracker=mouse_tracker, device_id="tracker_1")

        prop = local.get_property("track_frame")
        mock_prop_cb = MagicMock()
        prop.value_changed += mock_prop_cb

        mouse_tracker.start()

        expected_1 = {
            "timestamp": 1,
            "center_of_mass": (1, 2),
            "nose_pt": (10, 11),
            "tail_pt": (100, 101)
        }

        mock_prop_cb.assert_any_call(prop, None, json.dumps(expected_1))

        expected_2 = {
            "timestamp": 2,
            "center_of_mass": (2, 3),
            "nose_pt": (20, 21),
            "tail_pt": (200, 201)
        }
        mock_prop_cb.assert_any_call(prop, json.dumps(expected_1), json.dumps(expected_2))

    def test_local_mouse_tracker_send_mqtt_msg(self):

        mouse_tracker = FakeMouseTrack(nb_frames=1)
        local = LocalMouseTrackerDevice(mouse_tracker=mouse_tracker, device_id="tracker_1")

        mock_mqtt = MagicMock()
        client = LocalClient(environment_name="env", id_env="01", client_id="client", mqtt_client=mock_mqtt)

        client.add_device(local)

        mouse_tracker.start()

        expected_json = '{"timestamp": 1, "center_of_mass": [1, 2], "nose_pt": [10, 11], "tail_pt": [100, 101]}'

        mock_mqtt.publish_topic.assert_any_call(payload=expected_json, qos=2,
            retain=False, topic='env/01/client/tracker_1/track_frame')






if __name__ == '__main__':
    unittest.main()
