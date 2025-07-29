import configparser
import logging
import unittest
from pathlib import Path

from mqtt_device.client.client_config import ClientConfig, config_as_dict


class TestClientConfig(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        logging.root.setLevel(logging.INFO)

    def test_load_from_file(self):

        file = Path("./resources/client_config.ini")
        app_config = ClientConfig.load_from_file(file)

        # self.assertTrue(app_config.test_mode)
        # self.assertTrue(app_config.logging)

        self.assertEqual(("192.168.24.19", 1234),  app_config.broker_address)
        self.assertEqual(["001M01", "001L01", "001M02", "001L02", "002L01", "002L02", "002PS01"], app_config.expected_devices)

        self.assertEqual(4, len(app_config.relationships))
        self.assertEqual([("001L01", "001M01"), ("001L02", "001M02"), ("002L02", "002PS01"), ("002L01", "002PS01")], app_config.relationships)

        print('ok')

    def test_config_as_dict_function(self):
        file = Path("./resources/client_config.ini")

        config = configparser.RawConfigParser()
        config.read(str(file))

        res = config_as_dict(config)

        # check section "Devices" => expect 3 values
        self.assertEqual(3, len(res["Devices"]))




