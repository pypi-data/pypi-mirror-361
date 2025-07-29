import json
from typing import TypeVar, Generic, Dict, TYPE_CHECKING, Any

from obsub import event

from mqtt_device.common.common_log import create_logger
from mqtt_device.common.exception import DeviceException
from mqtt_device.event_listener.listener import EventArgs

if TYPE_CHECKING:
    from mqtt_device.core.device import Device


_T = TypeVar('_T')


class DeviceProperty(Generic[_T]):

    # def __init__(self, property_name: str, datatype: str, settable: bool = False, retention: bool = False, static: bool = False, static_value: _T = None):
    def __init__(self, property_name: str = None, datatype: str = None, settable: bool = False, retention: bool = False, value: _T = None):
        self.logger = create_logger(self)
        self.property_name: str = property_name
        self.datatype: str = datatype

        self.settable: bool = settable
        # self.static: bool = static
        self.retention: bool = retention

        # self.logger.info(f"PROP settable = {settable} retention= {retention}")
        # self.default_value = default_value

        self.device: 'Device' = None
        self._value: _T = value

        # self._set_value(static_value)

    @event
    def value_changed(self, old_val: object, new_val: object):
        pass

    # a value have been set (for settable properties)
    @event
    def value_setted(self, val: object):
        pass

    def toDict(self) -> dict:
        res = {
            'name': self.property_name,
            'datatype': self.datatype,
            'settable': self.settable,
            'retain': self.retention,
            'value': self.value
        }

        return res

    def fromDict(self, json_dict: Dict):
        self.property_name = json_dict.get('name')
        self.datatype = json_dict.get('datatype')
        self.settable = bool(json_dict.get('settable'))
        self.retention = bool(json_dict.get('retain'))
        self._set_str_value(json_dict.get('value'))

    # def toDictForJSON(self) -> Dict:
    #     return {
    #         'name': self.property_name,
    #         'datatype': self.datatype,
    #         'settable': self.settable,
    #         'retain': self.retention,
    #         'value': self.value
    #     }
    @classmethod
    def deserialize(cls, json_str: str) -> 'DeviceProperty':
        json_dict = json.loads(json_str)

        res = DeviceProperty()
        res.fromDict(json_dict)

        return res

    # internal set value without raising event and convert and check data type validity
    def _set_str_value(self, value_str: str):

        if value_str is None:
            # do nothing
            return

        if self.datatype.lower() in ["boolean", "bool"]:
            if not value_str.lower() in ["true", "false"]:
                raise DeviceException(f"Wrong value '{value_str}' but should be 'true' or 'false'")

            value = value_str.lower() == "true"
            self._set_value(value)
            # self.value = value_str.lower() == "true"

        if self.datatype.lower() == "integer":
            # self.value = int(value_str)
            value = int(value_str)
            self._set_value(value)

        if self.datatype.lower() in ["str"]:
            self._set_value(value_str)

        if self.datatype.lower() in ["json"]:
            # self.logger.critical("JSON TO IMPLEMENT!")
            self._set_value(value_str)

        if self.datatype.lower() == "float":
            # self.value = float(value_str)
            value = float(value_str)
            self._set_value(value)

    @property
    def value(self) -> _T:
        return self._value

    @value.setter
    def value(self, val: _T):

        if not self.settable:
            raise DeviceException(f"Property '{self.property_name}' is not settable")

        # don't check if value have changed (to catch event like lever pressed event always to true)
        self.logger.info(f"Value changed from {self._value} to {val}")
        self.value_setted(str(val))
        # self._value = val

    # internal set value
    def _set_value(self, val: _T):

        if val is None:
            return

        self.logger.info(f"Property '{self.property_name}' ({self.device}): Value changed from {self._value} to {val}")
        self.value_changed(self._value, val)
        self._value = val

    def __str__(self):
        msg = f"Property '{self.property_name}' belong to {self.device}"
        return msg

class DevicePropertyAddedEvent(EventArgs):

    def __init__(self, device_property: DeviceProperty):
        self.device_property = device_property
