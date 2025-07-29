import datetime
import json
from abc import abstractmethod
from typing import Dict

from mqtt_device.core.device.device import Device, IDevice
from mqtt_device.core.device.device_property import DeviceProperty
from mqtt_device.core.device.event import BaseIdentifiedEvent, BaseEvent
from mqtt_device.core.device.remote.remote_device import RemoteDevice
from mqtt_device.event_listener.listener import EventHandler

class IFeeder(IDevice):

    @property
    @abstractmethod
    def pellet_delivered(self) -> EventHandler['FeederEvent']:
        pass

    @property
    @abstractmethod
    def nose_poke(self) -> EventHandler['NosePokeEvent']:
        pass

    @property
    @abstractmethod
    def pellet_detection(self) -> EventHandler['PelletEvent']:
        pass


class FeederDevice(Device, IFeeder):

    DEVICE_TYPE = "feeders"

    def __init__(self, device_id: str, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        self._pellet_delivered: EventHandler[FeederEvent] = EventHandler(self)
        self._nose_poke: EventHandler[NosePokeEvent] = EventHandler(self)
        self._pellet_detection: EventHandler[PelletEvent] = EventHandler(self)

    def declare_properties(self):

        prop = DeviceProperty(property_name="activate", datatype="str", settable=True)
        self.add_property(prop)

        prop = DeviceProperty(property_name="pellet_delivered", datatype="str")
        self.add_property(prop)

        prop = DeviceProperty(property_name="nose_poke", datatype="str")
        self.add_property(prop)

    def on_property_added(self, sender: 'Device', prop: 'DeviceProperty'):
        if prop.property_name == "activate":
            prop.value_changed += self.on_activate
        elif prop.property_name == "pellet_delivered":
            prop.value_changed += self.on_pellet_delivered
        elif prop.property_name == "nose_poke":
            prop.value_changed += self.on_nose_poke


    def on_nose_poke(self, sender: DeviceProperty, old_val: str, new_val: str):
        self._nose_poke(event=NosePokeEvent(id_device=self.device_id, date=datetime.datetime.now(), status="in"))

    def on_pellet_delivered(self, sender: DeviceProperty, old_val: str, new_val: str):
        self._pellet_delivered(event=FeederEvent(id_device=self.device_id, date=datetime.datetime.now()))

    def on_activate(self, sender: DeviceProperty, old_val: str, new_val: str):
        self.activate()

    def activate(self):
        prop = self.get_property(property_name="pellet_delivered")
        prop._set_value("delivered")

    def activate_nose_poke(self):
        prop = self.get_property(property_name="nose_poke")
        prop._set_value("out")

    @property
    def pellet_delivered(self) -> EventHandler['FeederEvent']:
        return self._pellet_delivered

    @property
    def nose_poke(self) -> EventHandler['NosePokeEvent']:
        return self._nose_poke

    @property
    def pellet_detection(self) -> EventHandler['PelletEvent']:
        return self._pellet_detection

class FeederEvent(BaseIdentifiedEvent):
    EVENT_TYPE = "feeder"

class NosePokeEvent(BaseIdentifiedEvent):
    EVENT_TYPE = "nose_poke"

    def __init__(self, id_device: str=None, date: datetime.datetime=None, status: str=None, rfid: str = None):
        super().__init__(id_device, date, rfid)
        self.status = status

    def toDict(self) -> Dict:
        res = super().toDict()
        res["status"] = self.status
        return res

    def fromDict(self, json_dict: Dict):
        super().fromDict(json_dict)
        self.status = json_dict["status"]

class PelletEvent(BaseIdentifiedEvent):
    EVENT_TYPE = "pellet"

class RemoteFeeder(RemoteDevice, IFeeder):

    DEVICE_TYPE = "feeders"

    def __init__(self, device_id: str = None, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        self._pellet_delivered: EventHandler[FeederEvent] = EventHandler(self)
        self._nose_poke: EventHandler[NosePokeEvent] = EventHandler(self)
        self._pellet_detection: EventHandler[PelletEvent] = EventHandler(self)

    def activate(self):
        # self.allowed_rfid.append(rfid)
        print("ACTIVATED!")
        prop = self.get_property("activate")
        prop.value = "ON"

    @property
    def pellet_delivered(self) -> EventHandler[FeederEvent]:
        return self._pellet_delivered

    @property
    def pellet_detection(self) -> EventHandler[PelletEvent]:
        return self._pellet_detection

    @property
    def nose_poke(self) -> EventHandler[NosePokeEvent]:
        return self._nose_poke

    def on_pellet_delivered(self, sender: DeviceProperty, old_val: str, new_val: str):

        # to be compatible with old version sending a straight str and the new version in json with timestamp
        try:
            # res_json = json.loads(new_val)
            # date = datetime.datetime.fromisoformat(res_json["date"])
            event = FeederEvent.deserialize(new_val)
            self.pellet_delivered(event)
            # self.lever_pressed(LeverEvent(id_device=sender.device.device_id, date=res_json["date"]))
        except json.decoder.JSONDecodeError:
            date_now = datetime.datetime.now()
            self.pellet_delivered(FeederEvent(id_device=sender.device.device_id, date=date_now))

    def on_nose_poke(self, sender: DeviceProperty, old_val: str, new_val: str):
        # date_now = datetime.datetime.now()
        # status = new_val
        # self.nose_poke(NosePokeEvent.deserialize(new_val))
        # # self.nose_poke(NosePokeEvent(id_device=sender.device.device_id, status=status, date=date_now))
        # to be compatible with old version sending a straight str and the new version in json with timestamp
        try:
            # res_json = json.loads(new_val)
            # date = datetime.datetime.fromisoformat(res_json["date"])
            event = NosePokeEvent.deserialize(new_val)
            self.nose_poke(event)
            # self.lever_pressed(LeverEvent(id_device=sender.device.device_id, date=res_json["date"]))
        except json.decoder.JSONDecodeError:
            date_now = datetime.datetime.now()
            self.nose_poke(NosePokeEvent(id_device=sender.device.device_id, date=date_now, status=new_val))


    def on_property_added(self, sender: RemoteDevice, prop: DeviceProperty):

        if prop.property_name == "pellet_delivered":
            prop.value_changed += self.on_pellet_delivered

        # if prop.property_name == "beam_pellet":
        #     prop.value_changed += self.on_beam_pellet

        if prop.property_name == "nose_poke":
            prop.value_changed += self.on_nose_poke

