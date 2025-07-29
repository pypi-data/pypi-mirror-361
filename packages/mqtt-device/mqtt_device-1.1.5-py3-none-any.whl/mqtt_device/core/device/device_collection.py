from typing import Generic, List, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from mqtt_device.common.common_log import create_logger
from mqtt_device.core.device.type_var import T_DEVICE
from mqtt_device.event_listener.listener import EventHandler, EventArgs


class DeviceAddedEvent(EventArgs, Generic[T_DEVICE]):

    def __init__(self, device: T_DEVICE):
        self.device = device

class DeviceRemovedEvent(EventArgs, Generic[T_DEVICE]):

    def __init__(self, device: T_DEVICE):
        self.device = device

class DeviceCollection(Generic[T_DEVICE]):

    def __init__(self) -> None:

        self.logger = create_logger(self)

        self._devices: List[T_DEVICE] = list()
        self._device_added: EventHandler[DeviceAddedEvent[T_DEVICE]] = EventHandler(self)
        self._device_removed: EventHandler[DeviceRemovedEvent[T_DEVICE]] = EventHandler(self)

    @property
    def device_added(self) -> EventHandler[DeviceAddedEvent[T_DEVICE]]:
        return self._device_added

    @property
    def device_removed(self) -> EventHandler[DeviceRemovedEvent[T_DEVICE]]:
        return self._device_removed


    def to_list(self) -> List[T_DEVICE]:
        return self._devices

    # # TODO : make verification before with wait_u_s and let get_by_id to be straight?
    # def get_by_id(self, device_id: str, timeout: float = 10) -> T_DEVICE:
    #     res = wait_until_success(self._get_by_id, timeout=timeout, device_id=device_id)
    #     return res

    def get_by_id(self, device_id: str) -> T_DEVICE:

        res = [device for device in self._devices if device.device_id == device_id]

        if len(res) == 0:
            return None
        else:
            # print(f"## res={res[0]}")
            return res[0]

    def get_by_type(self, device_type: str) -> 'DeviceCollection':

        res = [device for device in self._devices if device.device_type == device_type]
        return DeviceCollection(res)

    def add(self, device: T_DEVICE) -> bool:
        # print(f"### DEVICE ADDED {device.device_id}")
        if device not in self._devices:

            self._devices.append(device)
            self.device_added(event=DeviceAddedEvent(device=device))

            return True

        return False

    def remove(self, device: T_DEVICE) -> bool:
        # print(f"### DEVICE ADDED {device.device_id}")
        if device in self._devices:

            self._devices.remove(device)
            self.device_removed(event=DeviceRemovedEvent(device=device))

            return True

        return False

    def __add__(self, other: 'DeviceCollection[T_DEVICE]') -> 'DeviceCollection[T_DEVICE]':

        for device in other:
            status = self.add(device)
            if not status:
                raise Exception(f"Cannot add remote device {device.device_id} to collection because this id already exists and should be unique")

        return self

    def __contains__(self, device: T_DEVICE) -> bool:
        return device in self._devices

    def __iter__(self):
        return iter(self._devices)

    def __len__(self) -> int:
        return len(self._devices)
