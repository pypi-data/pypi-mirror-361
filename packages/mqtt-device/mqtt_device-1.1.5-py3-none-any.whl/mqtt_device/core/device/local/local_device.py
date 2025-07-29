import json
import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from mqtt_device.core.device.device import IDevice, Device
from mqtt_device.core.device.event import LeverEvent
from mqtt_device.event_listener.listener import EventHandler

if TYPE_CHECKING:
    from mqtt_device.core.device.local import LocalClient

LOG_FORMAT = logging.Formatter('%(thread)d %(threadName)s %(asctime)s%(msecs)04d -- %(levelname)s -- %(message)s --  %(filename)s:%(lineno)d')

# only to configue a local module logger
module_logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(LOG_FORMAT)
module_logger.addHandler(ch)


class ILever(IDevice):

    @property
    @abstractmethod
    def lever_pressed(self) -> EventHandler[LeverEvent]:
        pass

    @property
    @abstractmethod
    def activate(self):
        pass


class LocalDevice(Device['LocalClient']):


    def __init__(self, device_id: str = None, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        self.declare_properties()

    @abstractmethod
    def declare_properties(self):
        pass

    @property
    def client(self) -> 'LocalClient':
        return self._client
    
    @client.setter
    def client(self, value: 'LocalClient'):
        if self._client is not None and value != self._client:
            raise Exception(f"Client {value} was already set need to code this case (remove from old client by example)")

        self._client = value
        # add the device to the client
        self._client.devices.add(self)


