import datetime
import json
from typing import Dict, Type, TypeVar, TYPE_CHECKING

from obsub import event

from mqtt_device.common.exception import DeviceException
from mqtt_device.core.device.device import Device
from mqtt_device.core.device.device_property import DeviceProperty
from mqtt_device.core.device.event import LeverEvent
from mqtt_device.core.device.local.local_device import module_logger, ILever
from mqtt_device.event_listener.listener import EventHandler

if TYPE_CHECKING:
    from mqtt_device.core.device.remote import RemoteClient

T = TypeVar('T')

class RemoteDevice(Device):

    # registered_device_cls: Dict[str, Type['RemoteDevice']] = dict()

    def __init__(self, device_id: str, device_type: str = None, location: str=None):
        super().__init__(device_id, device_type, location)
        # self.property_added += self.on_property_added
        # self.property_added.register(self.on_property_added)

    # def on_property_added(self, sender: 'RemoteDevice', prop: DeviceProperty):
    #     self.logger.debug("Not implemented")

    # def __init_subclass__(cls: Type['RemoteDevice']):
    #
    #     device_type = cls.DEVICE_TYPE
    #
    #     if not device_type:
    #         return
    #
    #     if device_type in cls.registered_device_cls:
    #         err_msg = f"Conflict with group type '{device_type}'. This type is already registered with another class"
    #         module_logger.error(err_msg)
    #         raise DeviceException(err_msg)
    #     else:
    #         module_logger.info(f"Class {cls}, subclass of remote device of type '{device_type}' is registered")
    #         cls.registered_device_cls[device_type] = cls

    def add_property(self, device_property: 'BaseDeviceProperty'):
        self.logger.debug(f"Device prop added {device_property.property_name}")
        # if self.client is None:
        #     raise DeviceException("Remote device should be added to a remote client before adding a property")

        super().add_property(device_property)

    @property
    def is_connected(self) -> bool:

        if self.remote_client:
            return self.remote_client.is_connected

        return False

    # Alias to client
    @property
    def remote_client(self) -> 'RemoteClient':
        return self.client


    def __eq__(self, other: 'RemoteDevice'):

        if not isinstance(other, type(self)):
            return None

        return self.home_topic == other.home_topic


# class MouseTrackerDevice(RemoteDevice):
#
#     DEVICE_TYPE = "mouse_tracker"
#
#     @event
#     def frame_received(self, mouse_track_frame):
#         pass
#
#     def on_property_added(self, sender: RemoteDevice, prop: DeviceProperty):
#         if prop.property_name == "track_frame":
#             prop.value_changed += self.on_frame_received
#
#     def on_frame_received(self, sender: DeviceProperty, old: str, new: str):
#         mouse_track = self._create_mouse_track_frame_from_json(new)
#         self.frame_received(mouse_track)
#
#     @staticmethod
#     def _create_mouse_track_frame_from_json(json_data: str) -> MouseTrackFrame:
#
#         res = json.loads(json_data)
#
#         center_of_mass = tuple(res['center_of_mass']) if res['center_of_mass'] else None
#         nose_pt = tuple(res['nose_pt']) if res['nose_pt'] else None
#         tail_pt = tuple(res['tail_pt']) if res['tail_pt'] else None
#
#         mouse_track = MouseTrackFrame(timestamp=res["timestamp"],
#                                       center_of_mass=center_of_mass,
#                                       nose_pt=nose_pt,
#                                       tail_pt=tail_pt)
#
#
#         return mouse_track


class RemoteLever(RemoteDevice, ILever):

    DEVICE_TYPE = "levers"

    def __init__(self, device_id: str = None, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        self._lever_pressed: EventHandler[LeverEvent] = EventHandler(self)

    @property
    def lever_pressed(self) -> EventHandler[LeverEvent]:
        return self._lever_pressed

    def on_state_changed(self, sender: DeviceProperty, old_val: str, new_val: str):
        # print("## STATE CHANGED")

        # to be compatible with old version sending a straight str and the new version in json with timestamp
        try:
            # res_json = json.loads(new_val)
            # date = datetime.datetime.fromisoformat(res_json["date"])
            event = LeverEvent.deserialize(new_val)
            self.lever_pressed(event)
            # self.lever_pressed(LeverEvent(id_device=sender.device.device_id, date=res_json["date"]))
        except json.decoder.JSONDecodeError:
            date_now = datetime.datetime.now()
            self.lever_pressed(LeverEvent(id_device=sender.device.device_id, date=date_now))

    def on_property_added(self, sender: RemoteDevice, prop: DeviceProperty):

        # print(f"## PROP ADDED = {prop.property_name}")
        if prop.property_name == "lever_state":
            prop.value_changed += self.on_state_changed
