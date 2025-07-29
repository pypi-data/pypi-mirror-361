

import datetime
import json
from abc import abstractmethod
from typing import TypeVar, Generic, Dict, Type

import pytz

from mqtt_device.core.device.type_var import T_DEVICE
from mqtt_device.event_listener.listener import EventArgs

# T_SER = TypeVar("T_SER")

class DateTimeEncoder(json.JSONEncoder):

    def default(self, z):
        if isinstance(z, datetime.datetime):
            return z.timestamp()
        else:
            return super().default(z)



class BaseEvent(EventArgs):

    EVENT_TYPE: str = None

    def __init__(self, id_device: str=None, date: datetime=None):
        self.id_device = id_device
        self.date = date
        # self.date = datetime.datetime.fromtimestamp(iso_date).isoformat()

    @property
    def event_type(self) -> str:
        if self.EVENT_TYPE:
            return self.EVENT_TYPE
        else:
            raise Exception(f"EVENT_TYPE for class '{type(self)}' needed")

    def serialize(self) -> str:
        json_dict = self.toDict()

        return json.dumps(json_dict, indent=4)
        # # res = json.dumps(self.__dict__, default=str)
        # res = f"""{{
        #     "id_device":"{self.id_device}",
        #     "timestamp":"{self.date.timestamp()}"
        #     }}
        #     """
        # return res

    @classmethod
    def deserialize(cls: Type[T_DEVICE], json_str: str) -> T_DEVICE:

        json_dict = json.loads(json_str)

        res = cls()
        res.fromDict(json_dict)

        return res
        # timezone = pytz.timezone('Europe/Paris')
        #
        # json_dict = json.loads(json_str)
        # self.date = datetime.datetime.fromtimestamp(float(json_dict["timestamp"])).astimezone(tz=timezone)
        # self.id_device = json_dict["id_device"]

    def toDict(self) -> Dict:

        res = {
            "id_device": self.id_device,
            "timestamp": self.date.timestamp()
        }

        return res

    def fromDict(self, json_dict: Dict):

        timezone = pytz.timezone('Europe/Paris')

        self.date = datetime.datetime.fromtimestamp(float(json_dict["timestamp"])).astimezone(tz=timezone)
        self.id_device = json_dict["id_device"]

class BaseIdentifiedEvent(BaseEvent):

    def __init__(self, id_device: str=None, date: datetime=None, rfid: str = None):
        super().__init__(id_device, date)
        self.rfid = rfid

    def toDict(self) -> Dict:
        res =  super().toDict()
        res["rfid"] = self.rfid

        return res

    def fromDict(self, json_dict: Dict):
        super().fromDict(json_dict)
        self.rfid = json_dict["rfid"]

class LeverEvent(BaseIdentifiedEvent):

    EVENT_TYPE = "id_lever"
