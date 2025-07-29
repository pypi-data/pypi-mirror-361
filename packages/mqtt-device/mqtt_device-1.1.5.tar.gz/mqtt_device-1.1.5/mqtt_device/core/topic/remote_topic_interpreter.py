import json
from typing import TYPE_CHECKING

from mqtt_device.common.wait_until_success import wait_until_success
from mqtt_device.core.client.mqtt_client import ClientConnexionEvent
from mqtt_device.core.device.device_collection import DeviceAddedEvent
from mqtt_device.core.device.device_factory import RemoteDeviceFactory
from mqtt_device.core.device.device_property import DeviceProperty
from mqtt_device.core.device.local.local_client import LocalClient
from mqtt_device.core.device.type_var import T_CLIENT
from mqtt_device.core.topic.topic import TopicInterpreter, RawTopic, ClientTopic, DeviceTopic, PropertyTopic

if TYPE_CHECKING:
    from mqtt_device.core.device.remote import ApplicationClient
    from mqtt_device.core.device.remote import RemoteDevice


class ApplicationClientTopicInterpreter(TopicInterpreter['ApplicationClient']):


    def __init__(self, device_factory: RemoteDeviceFactory):
        super().__init__()

        # self._device_factory = DefaultFactory()
        self._device_factory = device_factory


    def _set_client(self, value: 'ApplicationClient'):
        super()._set_client(value)

        # connect to events
        self.client.remote_client_added += self.on_remote_client_added
        self.client.devices.device_added.register(self.on_remote_device_added)

    def on_remote_client_added(self, sender: LocalClient, remote_client: 'RemoteClient'):

        self.logger.info(f"Remote client '{remote_client.home_topic}' ADDED to client '{id(self.client)}'")
        self.client.subscribe_topic(f"{remote_client.home_topic}/+/$meta")

    def _add_prop(self, sender: 'RemoteDevice', prop: 'DeviceProperty'):
        # print("#### ADD PROP")
        prop.value_setted += self.on_remote_device_property_value_setted
        topic = f"{sender.home_topic}/{prop.property_name}"
        self.client.subscribe_topic(topic=topic)

    # def on_remote_device_added(self, sender: LocalClient, remote_device: 'RemoteDevice'):
    def on_remote_device_added(self, sender, event: DeviceAddedEvent['RemoteDevice']):

        remote_device = event.device
        self.client.subscribe_topic(f"{remote_device.home_topic}/+/$meta")

        # dont't forget existing props
        for prop in remote_device.properties:
            self._add_prop(sender=remote_device, prop=prop)

        remote_device.property_added += self._add_prop

    def on_remote_device_property_value_setted(self, sender: 'DeviceProperty', val):
        # print(f"## PROP CHANGED {sender.property_name}")
        prop_topic = f"{sender.device.home_topic}/{sender.property_name}/set"
        self.client.publish_topic(topic=prop_topic, payload=val, retain=sender.retention)

    def on_client_connected(self, sender: T_CLIENT, event: ClientConnexionEvent):

        # take only the env/id_env topics
        self.client.subscribe_topic(topic=f"{self.client.environment_name}/{self.client.id_env}/+/$connected")

    def process(self, raw_topic: RawTopic):

        self.logger.debug(f"receive : {raw_topic}")
        topic = self.instanciate_topic(raw_topic)

        if isinstance(topic, ClientTopic):
            self._process_client_topic(topic)
        elif isinstance(topic, DeviceTopic):
            self._process_device_topic(topic)
        elif isinstance(topic, PropertyTopic):
            self._process_property_topic(topic)
        else:
            self.logger.warning(f"Unknown topic form for topic : '{raw_topic}'")
            # print("DEVICE TOPIC!!")

    def _process_property_topic(self, topic: PropertyTopic):

        client = self.client

        remote_client = client.get_remote_client(client_id=topic.client_topic.client_id)  # self.client_topic.home_topic_str)

        device = remote_client.devices.get_by_id(topic.device_topic.device_id)

        device_prop = device.get_property(property_name=topic.property_id)

        if device_prop:
            device_prop._set_str_value(value_str=topic.payload)


    def _process_device_topic(self, topic: DeviceTopic):

        client = self.client

        client_topic = topic.client_topic
        remote_client = client.get_remote_client(client_id=client_topic.client_id)


        if not remote_client:
            self.logger.warning(f"Remote client '{client_topic}' unregistered")
            return

        remote_device = remote_client.devices.get_by_id(device_id=topic.device_id)
        # remote_device = wait_until_success(remote_client.devices.get_by_id, device_id=topic.device_id)

        if remote_device:
            # device exists already don't add property twice or more (happends when device restart)
            self.logger.warning(f"Remote device '{remote_device}' is already registered")
            return

        if topic.meta_field == "$meta":

            json_dict = json.loads(topic.payload)

            if "device_id" not in json_dict:
                json_dict["device_id"] = topic.device_id

            remote_device = self._device_factory.instantiate(json_dict)
            remote_device.client = remote_client




    def _process_client_topic(self, topic: ClientTopic):

        # discover case, the client is discovered and add to the client
        from mqtt_device.core.device.remote.remote_client import RemoteClient

        remote_client: RemoteClient = self.client.get_remote_client(client_id=topic.client_id, timeout=0)
        self.logger.debug(f"Search for client id: {topic.client_id} result: {remote_client}")

        if topic.meta_field == "$connected":

            if remote_client is None:

                self.logger.debug(f"Client '{topic.client_id}' dont exists and will be created")
                remote_client = RemoteClient(environment_name=topic.environment_name, id_env=topic.environment_id, client_id=topic.client_id)
                self.client.add_remote_client(remote_client=remote_client)

            # update the connection status
            # TODO : status is inconsistent in deployed devices("ok", "Dirty", "false", "True"), try to unify
            self.logger.debug(f"META IS CONNECTED paylaod = {topic.payload}")
            remote_client.is_connected = topic.payload.lower() in ["true", "ok"]
