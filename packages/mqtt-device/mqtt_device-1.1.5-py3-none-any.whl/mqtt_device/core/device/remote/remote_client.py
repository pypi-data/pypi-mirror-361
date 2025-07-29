from typing import Dict, List

from obsub import event

from mqtt_device.core.client.client import BaseClient, Client, MessageFilter
from mqtt_device.core.client.mqtt_client import IMQTTClient
from mqtt_device.common.wait_until_success import wait_until_success
from mqtt_device.core.device.device_collection import DeviceAddedEvent
from mqtt_device.core.device.device_factory import RemoteDeviceFactory
from mqtt_device.core.device.remote.remote_device import RemoteDevice
from mqtt_device.core.topic.remote_topic_interpreter import ApplicationClientTopicInterpreter

class RemoteClient(BaseClient[RemoteDevice]):

    @event
    def connexion_status_changed(self, new_status: bool):
        pass

    def __init__(self, environment_name: str, id_env: str, client_id: str):
        super().__init__(environment_name, id_env)

        self.client_id: str = client_id
        self._is_connected: bool = None
        self._owner: ApplicationClient = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    # TODO => bad inheritance with duplication of home_topic, review this
    @property
    def home_topic(self) -> str:
        res = f"{self.environment_name}/{self.id_env}/{self.client_id}"
        return res.replace(' ', '_')

    @is_connected.setter
    def is_connected(self, value: bool):

        if self._is_connected != value:
            self.logger.info(f"Connexion status changed for client : {self.client_id} status = {self.is_connected}")
            self._is_connected = value
            # notify status have changed
            self.connexion_status_changed(value)

            list(map(lambda device: device.connexion_status_changed(value), self.devices.to_list()))


class ApplicationClient(Client[RemoteDevice]):

    def __init__(self, environment_name: str, id_env: str, mqtt_client: IMQTTClient, device_factory: RemoteDeviceFactory, expected_devices: List[str] = None):
        super().__init__(environment_name, id_env, mqtt_client, ApplicationClientTopicInterpreter(device_factory))

        self._remote_clients: Dict[str, RemoteClient] = dict()
        self.expected_devices = expected_devices
        # self._remote_device_added: EventHandler[DeviceAddedEvent[RemoteDevice]] = EventHandler(self)

    @event
    def remote_client_added(self, remote_client: 'RemoteClient'):
        pass

    @property
    def filter(self) -> MessageFilter:
        return self._filter

    @filter.setter
    def filter(self, value: MessageFilter):
        self._filter = value

    def connect(self):
        super().connect()
        self._wait_expected_devices()


    def _wait_expected_devices(self):

        if not self.expected_devices:
            return

        for expected in self.expected_devices:
            device = wait_until_success(self.devices.get_by_id, timeout=10, device_id=expected)
            if device is None:
                detected_devices = [elem.device_id for elem in self.devices]
                err_msg = f"Unable to found all expected devices :{self.expected_devices}\n" \
                          f"Devices detected : {detected_devices}"
                raise Exception(err_msg)
            else:
                self.logger.info(f"Expected devices '{expected}' is found ({device})")


    def on_remote_device_added(self, sender, event: DeviceAddedEvent[RemoteDevice]):
        device = event.device
        self.logger.debug(f"Device added : {device.device_id}")

        self.devices.add(event.device)

    def add_remote_client(self, remote_client: 'RemoteClient'):

        if not self._remote_clients.get(remote_client.client_id):
            self._remote_clients[remote_client.client_id] = remote_client
            self.remote_client_added(remote_client)
            # remote_client.device_added += self.on_device_added
            remote_client.devices.device_added.register(self.on_remote_device_added)

        else:
            self.logger.warning(f"Remote Client '{remote_client.home_topic}' already exists")

    # def get_remote_device(self, device_id: str, env_name: str = None, env_id: str = None, client_id: str = None, timeout: float = 1) -> 'RemoteDevice':
    def get_remote_device(self, device_id: str, timeout: float = 1) -> RemoteDevice:

        def try_to_get_device() -> 'RemoteDevice':
            # devices = self.remote_devices()
            devices = self.devices

            # res = [device for device in devices if device.device_id == device_id]
            device = devices.get_by_id(device_id)

            if device is not None:
                return res

        res = wait_until_success(callback=try_to_get_device, timeout=timeout)

        return res

    def get_remote_client(self, client_id: str, timeout: float = 0.5) -> RemoteClient:

        # self.logger.info("GET REMOTE CLIENT")
        topic_str = f'{client_id}'

        def try_to_get_client() -> RemoteClient:
            if self._remote_clients.get(topic_str):
                self.logger.debug(f"Remote client found '{topic_str}'")
                return self._remote_clients[topic_str]

        # print(f"### try client : {client_id} timeout={timeout}")
        res = wait_until_success(callback=try_to_get_client, timeout=timeout)

        return res






