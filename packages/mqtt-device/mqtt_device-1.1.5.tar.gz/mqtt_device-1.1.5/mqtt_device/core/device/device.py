import json
from abc import abstractmethod
from logging import Logger
from typing import Generic, Dict, List, Type

from obsub import event

from mqtt_device.common.common_log import create_logger
from mqtt_device.common.wait_until_success import wait_until_success
from mqtt_device.core.device.device_property import DeviceProperty, DevicePropertyAddedEvent

from mqtt_device.core.device.type_var import T_CLIENT, T_DEVICE
from mqtt_device.event_listener.listener import EventHandler


class IDevice:

    @abstractmethod
    def add_property(self, prop: DeviceProperty):
        pass

    @abstractmethod
    def get_property(self, prop_name: str) -> DeviceProperty:
        pass

    @property
    @abstractmethod
    def property_added(self) -> EventHandler[DevicePropertyAddedEvent]:
        pass

    @property
    @abstractmethod
    def device_id(self) -> str:
        pass

    @property
    @abstractmethod
    def location(self) -> str:
        pass

class Device(Generic[T_CLIENT], IDevice):

    DEVICE_TYPE: str = None

    @event
    def connexion_status_changed(self, new_status: bool):
        pass

    @abstractmethod
    def on_property_added(self, sender: 'Device', prop: DeviceProperty):
        pass



    def __init__(self, device_id: str=None, device_type: str = None, location: str = None):
        self._logger = create_logger(self)
        self._device_id = device_id
        self._client: T_CLIENT = None

        self._properties: Dict[str, DeviceProperty] = dict()
        self._location = location
        self.property_added += self.on_property_added

        self._device_type: str = None

        if self.DEVICE_TYPE and device_type:
            self.logger.warning(f"device type arg '{device_type}' is ignored and DEVICE_TYPE is used instead")

        if self.DEVICE_TYPE:
            self._device_type = self.DEVICE_TYPE
        elif device_type:
            self._device_type = device_type

        self._prop_added: EventHandler[DevicePropertyAddedEvent] = EventHandler(self)

    def serialize(self) -> str:
        json_dict = self.toDict()

        return json.dumps(json_dict, indent=4)

    def toDict(self) -> dict:

        res = {
            'device_id': self.device_id,
            'type': self.device_type,
            'location': self.location,
            'properties': [prop.toDict() for prop in self.properties]
            # 'properties': [prop.toDictForJSON() for prop in self.properties]
        }

        return res

    @classmethod
    def deserialize(cls: Type[T_DEVICE], json_str: str) -> T_DEVICE:
        json_dict = json.loads(json_str)

        try:
            res = cls()
            res.fromDict(json_dict)
        except Exception as exc:
            err_msg = f"unable to deserialize device of type:'{cls}'"

            # TODO : create log handler for class method ... and dont only print it
            print(err_msg)
            raise exc

        return res

    def fromDict(self, json_dict: Dict):
        self._device_id = json_dict['device_id']
        self._location = json_dict['location']

        if 'properties' not in json_dict:
            return

        for propertie_json in json_dict['properties']:
            # print(propertie)
            property = DeviceProperty.deserialize(json.dumps(propertie_json))
            self.add_property(property)

    @property
    def location(self) -> str:
        return self._location

    @location.setter
    def location(self, value: str):
        self._location = value

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_type(self) -> str:
        return self._device_type

    @event
    def property_added(self, device_property: 'DeviceProperty'):
        pass

    @property
    def logger(self) -> Logger:
        return self._logger

    def add_property(self, device_property: 'BaseDeviceProperty'):

        if not device_property.property_name in self._properties:
            self._properties[device_property.property_name] = device_property

            self.logger.info(f"Property '{device_property.property_name}' added")
            device_property.device = self

            #self.property_added(DevicePropertyAddedEvent(device_property))
            self.property_added(device_property)


    @property
    def properties(self) -> List['DeviceProperty']:
        return list(self._properties.values())


    def get_property(self, property_name: str, timeout: float = 1) -> 'DeviceProperty':

        # self.logger.info(f"get property:'{property_name}'")

        def try_to_get_property():
            if property_name in self._properties:
                res = self._properties[property_name]
                return res

        res = wait_until_success(callback=try_to_get_property, timeout=timeout)

        if not res:
            self.logger.error(f"Unable to found property '{property_name}' for device :'{self.device_id}'")
            existing_props = [prop.property_name for prop in self.properties]
            self.logger.error(f"existings props = {existing_props}")

        return res

    @property
    def home_topic(self) -> str:

        if not self._client:
            return None

        res = f"{self._client.home_topic}/{self._device_id}"
        return res.replace(' ', '_')


    @property
    def client(self) -> T_CLIENT:
        return self._client

    @client.setter
    def client(self, value: T_CLIENT):
        if self._client is not None and value != self._client:
            raise Exception(f"Client {value} was already set need to code this case (remove from old client by example)")

        self._client: T_CLIENT = value
        # add the device to the client
        # TODO : type check error for add ... find why?
        self._client.devices.add(self)
        # self._client.devices.add(self)

    def __eq__(self, other: 'Device'):
        return self.device_id == other.device_id and self.location == other.location

    def __str__(self):
        msg = f"device {self.device_id} of type {self.device_type}"
        return msg

    def as_type(self, cls: Type[T_DEVICE]) -> T_DEVICE:

        if isinstance(self, cls):
            return self
        else:
            self.logger.warning(f"Device id:'{self.device_id}' found but not the expected type(exp:'{cls}', actual:'{type(self)}') ")
            return None
