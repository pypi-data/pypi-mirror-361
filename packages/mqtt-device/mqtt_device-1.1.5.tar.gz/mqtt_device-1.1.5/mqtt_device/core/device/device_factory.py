import json
from typing import Generic, Dict, Type

from mqtt_device.common.common_log import create_logger
from mqtt_device.core.device.local.local_device import LocalDevice
from mqtt_device.core.device.remote.remote_device import RemoteDevice, RemoteLever
from mqtt_device.core.device.type_var import T_DEVICE
from mqtt_device.device.fake_common_local_device import FakeLeverLocal
from mqtt_device.device.feeder import RemoteFeeder


# from mqtt_device.device.fake_common_device import FakeLeverLocal


class DeviceFactory(Generic[T_DEVICE]):

    def __init__(self):
        self.logger = create_logger(self)
        self._device_type_cls: Dict[str, Type[T_DEVICE]] = {}

        self._init_associations()

    def _init_associations(self):
        pass

    def add_association(self, device_type_str: str, device_type: Type[T_DEVICE]):

        if device_type_str not in self._device_type_cls:
            self._device_type_cls[device_type_str] = device_type


    def instantiate(self, json_dict: Dict) -> T_DEVICE:

        device_type = json_dict["type"]
        # device_id = json_dict["device_id"]
        # location = json_dict["location"]

        if device_type in self._device_type_cls:
            json_str = json.dumps(json_dict)
            res = self._device_type_cls[device_type].deserialize(json_str)
        else:
            err_msg = \
                f"""Unknown device type: {device_type}.
                Available types: '{', '.join(self._device_type_cls.keys())}'
                """
            raise Exception(err_msg)

        return res

class LocalDeviceFactory(DeviceFactory[LocalDevice]):

    def _init_associations(self):
        self.add_association("levers", FakeLeverLocal)

class RemoteDeviceFactory(DeviceFactory[RemoteDevice]):

    def _init_associations(self):
        self.add_association("levers", RemoteLever)
        self.add_association("feeders", RemoteFeeder)
