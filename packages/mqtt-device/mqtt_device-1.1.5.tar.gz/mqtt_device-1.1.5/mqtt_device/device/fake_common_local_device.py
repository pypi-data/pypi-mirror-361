from mqtt_device.core.device.device_property import DeviceProperty
from mqtt_device.core.device.event import LeverEvent
from mqtt_device.core.device.local.local_device import LocalDevice, ILever
from mqtt_device.device.feeder import IFeeder, FeederEvent, NosePokeEvent
from mqtt_device.event_listener.listener import EventHandler


class FakeLocalBeam(LocalDevice):

    DEVICE_TYPE = "beams"

    def __init__(self, device_id: str, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        prop = DeviceProperty(property_name="beam_state", datatype="str")
        self.add_property(prop)


class FakeLeverLocal(LocalDevice, ILever):

    DEVICE_TYPE = "levers"

    def __init__(self, device_id: str = None, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        self._lever_pressed: EventHandler[LeverEvent] = EventHandler(self)
        self.lever_pressed.register(self.on_lever_pressed)
    def declare_properties(self):

        prop = DeviceProperty(property_name="activate", datatype="str", settable=True)
        self.add_property(prop)

        prop.value_changed += self.on_activate

        prop = DeviceProperty(property_name="lever_state", datatype="str", settable=False)
        self.add_property(prop)

        # prop.value_changed += self.on_state_changed



    def activate(self):
        self.lever_state._set_str_value("pressed")

    def on_activate(self, sender: DeviceProperty, old: str, new: str):
        self.activate()

    def on_lever_pressed(self, sender, event: LeverEvent):
        self.get_property("lever_state")._set_str_value(event.serialize())
    # def on_state_changed(self, sender: DeviceProperty, old: str, new: str):
    #     self._lever_pressed(LeverEvent(id_device=self.device_id, date=datetime.datetime.now().timestamp()))

    @property
    def lever_state(self) -> DeviceProperty:
        prop = self.get_property("lever_state")
        return prop

    @property
    def lever_pressed(self) -> EventHandler[LeverEvent]:
        return self._lever_pressed


class FakeLocalFeeder(LocalDevice, IFeeder):

    DEVICE_TYPE = "feeders"

    def __init__(self, device_id: str = None, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        self._pellet_delivered: EventHandler[FeederEvent] = EventHandler(self)
        self._nose_poke: EventHandler[NosePokeEvent] = EventHandler(self)

        self.pellet_delivered.register(self.on_pellet_delivered)
        self.nose_poke.register(self.on_nose_poke)
        # self._pellet_detection: EventHandler[PelletEvent] = EventHandler(self)

    def declare_properties(self):

        prop = DeviceProperty(property_name="activate", datatype="str", settable=True)
        self.add_property(prop)

        prop.value_changed += self.on_activate

        prop = DeviceProperty(property_name="pellet_delivered", datatype="str")
        # prop.value_changed += self.on_pellet_delivered
        self.add_property(prop)

        prop = DeviceProperty(property_name="nose_poke", datatype="str")
        # prop.value_changed += self.on_nose_poke
        self.add_property(prop)

    def on_nose_poke(self, sender, event: NosePokeEvent):
        self.get_property("nose_poke")._set_str_value(event.serialize())
        # self._nose_poke(event=NosePokeEvent(id_device=self.device_id, date=datetime.datetime.now(), status="in"))

    # def on_nose_poke(self, sender: DeviceProperty, old_val: str, new_val: str):
    #     self._nose_poke(NosePokeEvent.deserialize(new_val))
    #     # self._nose_poke(event=NosePokeEvent(id_device=self.device_id, date=datetime.datetime.now(), status="in"))

    def on_pellet_delivered(self, sender, event:FeederEvent):
        self.get_property("pellet_delivered")._set_str_value(event.serialize())
    # def on_pellet_delivered(self, sender: DeviceProperty, old_val: str, new_val: str):
    #     # self._pellet_delivered(event=FeederEvent(id_device=self.device_id, date=datetime.datetime.now()))
    #     self._pellet_delivered(event=FeederEvent.deserialize(new_val))

    def on_activate(self, sender: DeviceProperty, old_val: str, new_val: str):
        self.activate()

    def activate(self):
        prop = self.get_property(property_name="pellet_delivered")
        prop._set_value("delivered")

    def activate_nose_poke(self):
        prop = self.get_property(property_name="nose_poke")
        prop._set_value("out")

    @property
    def pellet_delivered(self) -> EventHandler[FeederEvent]:
        return self._pellet_delivered

    @property
    def nose_poke(self) -> EventHandler[NosePokeEvent]:
        return self._nose_poke

    # @property
    # def pellet_detection(self) -> EventHandler[PelletEvent]:
    #     return self._pellet_detection
