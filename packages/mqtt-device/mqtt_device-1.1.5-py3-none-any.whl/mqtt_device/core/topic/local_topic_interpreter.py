from typing import TYPE_CHECKING

from mqtt_device.core.client.mqtt_client import ClientConnexionEvent
from mqtt_device.core.device.device_collection import DeviceAddedEvent

from mqtt_device.core.device.type_var import T_CLIENT
from mqtt_device.core.topic.topic import RawTopic, PropertyTopic, TopicInterpreter



if TYPE_CHECKING:
    from mqtt_device.core.device.local.local_device import LocalDevice
    from mqtt_device.core.device import DeviceProperty
    from mqtt_device.core.device.local import LocalClient


class LocalClientTopicInterpreter(TopicInterpreter['LocalClient']):

    def __init__(self):
        super().__init__()

    def _set_client(self, value: 'LocalClient'):
        super()._set_client(value)
        value.devices.device_added.register(self.on_local_device_added)
        # value.device_added += self.on_local_device_added
        value.mqtt_client.will_set(topic=f'{self.client.home_topic}/$connected', payload='False')

    # def on_client_connected(self, sender: T_CLIENT):
    def on_client_connected(self, sender: T_CLIENT, event: ClientConnexionEvent):

        self.client.publish_topic(topic=f"{self.client.home_topic}/$connected", payload="True", retain=True)

    def process(self, raw_topic: RawTopic):

        topic = self.instanciate_topic(raw_topic)

        if isinstance(topic, PropertyTopic):
            if topic._set:
                device = self.client.devices.get_by_id(topic.device_topic.device_id)
                device_prop = device.get_property(property_name=topic.property_id)
                device_prop._set_str_value(value_str=topic.payload)


    # def on_property_added(self, sender: 'LocalDevice', device_prop: 'BaseDeviceProperty'):
    #     print("KIKOOLOL")

    # def on_local_device_added(self, sender: 'LocalClient', device: 'LocalDevice'):
    def on_local_device_added(self, sender, event: DeviceAddedEvent['LocalDevice']):

        device = event.device
        json_device = device.serialize()

        self.client.publish_topic(topic=f"{device.home_topic}/$meta",
                                  payload=json_device,
                                  retain=True)

        for prop in device.properties:

            if prop.settable:
                self.client.subscribe_topic(topic=f"{device.home_topic}/{prop.property_name}/set")

            # if not prop.static:
            #     prop.value_changed += self.on_local_device_property_value_changed

            prop.value_changed += self.on_local_device_property_value_changed




    def on_local_device_property_value_changed(self, sender: 'DeviceProperty', old_val, new_val):
        prop_topic = f"{sender.device.home_topic}/{sender.property_name}"
        self.client.publish_topic(topic=prop_topic, payload=str(new_val), retain=sender.retention)
