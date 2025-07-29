from typing import TypeVar, TYPE_CHECKING



if TYPE_CHECKING:
    from mqtt_device.core.device.device import Device
    from mqtt_device.core.client.client import Client

T_DEVICE = TypeVar('T_DEVICE', bound='Device')
T_CLIENT = TypeVar('T_CLIENT', bound='Client')
