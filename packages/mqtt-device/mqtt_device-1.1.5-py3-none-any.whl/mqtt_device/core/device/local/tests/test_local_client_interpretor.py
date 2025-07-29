import json
import logging
import unittest
from unittest.mock import Mock, MagicMock

from mqtt_device.core.device.local import LocalClient
from mqtt_device.core.device.local.device import LocalDevice
from mqtt_device.core.device import DeviceProperty
from mqtt_device.core.topic.local_topic_interpreter import LocalClientTopicInterpreter


class Microwave(LocalDevice):

    DEVICE_TYPE = "microwave"

    def __init__(self, power: int, brand: str, is_rotative: bool, device_id: str, location: str = None):
        self.power = power
        self.brand = brand
        self.is_rotative = is_rotative
        super().__init__(device_id, location)


        # self.init_properties()

    def declare_properties(self):

        prop = StaticProperty(property_name="power", datatype="integer", static_value=self.power)
        self.add_property(prop)
        # prop._set_value(self.power)

        prop = StaticProperty(property_name="brand", datatype="str", static_value=self.brand)
        self.add_property(prop)
        # prop._set_value(self.brand)

        prop = StaticProperty(property_name="is_rotative", datatype="bool", static_value=self.is_rotative)
        self.add_property(prop)

    # def init_properties(self):
    #
    #     prop = DeviceProperty(property_name="power", datatype="integer", settable=True, retention=True, default_value=self.power)
    #     self.add_property(prop)
    #     # prop._set_value(self.power)
    #
    #     prop = DeviceProperty(property_name="brand", datatype="str", settable=False, retention=True, default_value=self.brand)
    #     self.add_property(prop)
    #     # prop._set_value(self.brand)
    #
    #     prop = DeviceProperty(property_name="is_rotative", datatype="bool", settable=False, retention=True, default_value=self.is_rotative)
    #     self.add_property(prop)
    #     # prop._set_value(self.is_rotative)




class TestLocalClientInterpreter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        logging.root.setLevel(logging.DEBUG)

    def test_local_device_added_publish_topic(self):

        mock_mqtt = MagicMock()

        client = LocalClient(environment_name="env", id_env="01", client_id="client", mqtt_client=mock_mqtt)
        local_device = LocalDevice(device_id="My Device", device_type="microwave", location="cagibi")
        local_device._client = client

        interpretor = LocalClientTopicInterpreter()
        interpretor.client = client
        interpretor.on_local_device_added(Mock(), local_device)

        expected_topic = "env/01/client/My_Device/$meta"

        mock_mqtt.publish_topic.assert_any_call(
            topic=expected_topic, payload='{"type": "microwave", "location": "cagibi"}', qos=2, retain=True
        )

    def test_local_device_toJSON(self):

        properties = [
            DeviceProperty(property_name="temperature", datatype="float", settable=True, retention=True),
            DeviceProperty(property_name="hygrometry", datatype="float", settable=False, retention=False),
            StaticProperty(property_name="brand", datatype="str", static_value="philips")
        ]

        local_device = LocalDevice(device_id="My Device", device_type="microwave", location="cagibi")

        for item in properties:
            local_device.add_property(item)

        res = local_device.toJSON()
        json_res = json.loads(res)

        self.assertEqual('microwave', json_res['type'])
        self.assertEqual('cagibi', json_res['location'])
        self.assertEqual(3, len(json_res['properties']))


    def test_add_device_publish_properties_topic(self):

        # device_prop = DeviceProperty(property_name="temperature", datatype="float", settable=True, retention=True)

        mock_mqtt = MagicMock()
        client = LocalClient(environment_name="env", id_env="01", client_id="client", mqtt_client=mock_mqtt)

        # interpretor = LocalClientTopicInterpreter(client=client)

        # fake_local_device_type = create_fake_type(LocalDevice)
        properties = [
            DeviceProperty(property_name="temperature", datatype="float", settable=True, retention=True),
            DeviceProperty(property_name="hygrometry", datatype="float", settable=False, retention=False),
            DeviceProperty(property_name="brand", datatype="str", retention=True)
        ]

        local_device = LocalDevice(device_id="My Device", device_type="microwave", location="cagibi")

        for item in properties:
            local_device.add_property(item)

        local_device._client = client

        interpretor = LocalClientTopicInterpreter()
        interpretor.client = client

        interpretor.on_local_device_added(Mock(), local_device)

        expected_topic = "env/01/client/My_Device/$meta"

        res = local_device.toJSON()

        mock_publish = mock_mqtt.publish_topic

        mock_publish.assert_any_call(
            topic=expected_topic, payload=res, qos=2, retain=True
        )

    def test_device_property_changed_value(self):

        device_prop = DeviceProperty(property_name="temperature", datatype="float", settable=True, retention=True)

        mock_mqtt = MagicMock()
        client = LocalClient(environment_name="env", id_env="01", client_id="client", mqtt_client=mock_mqtt)
        local_device = LocalDevice(device_id="My Device", device_type="microwave", location="cagibi")
        local_device._client = client

        local_device.add_property(device_prop)

        interpreter = LocalClientTopicInterpreter()
        interpreter.client = client
        interpreter.on_local_device_added(Mock(), local_device)

        mock_mqtt.reset_mock()

        device_prop._set_str_value("23.56")

        # call.publish_topic(topic='env/01/client/My_Device/temperature', payload="23.56", qos=2, retain=True)
        expected_topic = "env/01/client/My_Device/temperature"

        mock_mqtt.publish_topic.assert_any_call(
            topic=expected_topic, payload="23.56", qos=2, retain=True
        )


    def test_with_fake_microwave(self):

        mock_mqtt = MagicMock()
        client = LocalClient(environment_name="env", id_env="01", client_id="client", mqtt_client=mock_mqtt)

        microwave = Microwave(power=900, brand="Moulinex", is_rotative=True, device_id="my micro", location="kitchen")

        client.add_device(microwave)

        print("OK")

