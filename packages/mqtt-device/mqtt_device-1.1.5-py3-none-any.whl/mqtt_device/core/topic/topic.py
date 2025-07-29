import logging
from abc import abstractmethod
from logging import Logger
from typing import TypeVar, List, Type, Generic

from mqtt_device.core.device.type_var import T_CLIENT
from mqtt_device.common.common_log import create_logger
from mqtt_device.core.client.mqtt_client import MQTTClient, MessageReceivedEvent, ClientConnexionEvent, IMQTTClient

_T = TypeVar('_T', bound='Topic')
# _U = TypeVar('_U', bound='Client')

logger = logging.getLogger(__name__)

class RawTopic:

    def __init__(self, topic_str: str, payload: str = None):
        self._logger = create_logger(self)

        self._splitted_topic = topic_str.split('/')
        self._payload = payload

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def payload(self) -> str:
        return self._payload

    def get_subtopic(self, start: int, end: int) -> 'RawTopic':
        topic_str = "/".join(self[start:end])
        return RawTopic(topic_str=topic_str)

    def __len__(self):
        return len(self._splitted_topic)

    def __getitem__(self, key: int):
        # if key is of invalid type or value, the list values will raise the error
        return self._splitted_topic[key]

    def __str__(self):

        res = "/".join(self._splitted_topic)

        return res



class Topic:

    def __init__(self, raw_topic: RawTopic):
        self._logger = create_logger(self)

        self._raw_topic = raw_topic
        self._payload: str = raw_topic.payload

        self._is_valid = None

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def payload(self) -> str:
        return self._payload

    @property
    def is_valid(self) -> bool:

        if not self._is_valid:
            self._is_valid = self._validate()

        return self._is_valid
    
    @property
    @abstractmethod
    def home_topic_str(self) -> str:
        pass

    @abstractmethod
    def _validate(self) -> bool:
        pass

    @property
    def raw_topic(self) -> RawTopic:
        return self._raw_topic

    @property
    def nb_levels(self) -> int:
        if self.meta_field:
            return len(self._raw_topic)-1
        else:
            return len(self._raw_topic)

    @property
    def meta_field(self) -> str:

        last_part = self._raw_topic[-1]
        if last_part[0] == "$":
            return last_part

        return None


    def __str__(self) -> str:
        return str(self._raw_topic)


class TopicInterpreter(Generic[T_CLIENT]):

    def __init__(self):

        self._topic_cls: List[Type[Topic]] = [ClientTopic, DeviceTopic, PropertyTopic]

        self._logger = create_logger(self)
        self._client: T_CLIENT = None

    def _set_client(self, value: T_CLIENT):

        if self._client:
            self.logger.info("Client is already setted")
            return

        self._client = value

        # Generics not works here?
        mqtt_client: IMQTTClient = value.mqtt_client

        mqtt_client.message_received.register(self.on_message_received)
        mqtt_client.connected.register(self.on_client_connected)


    @property
    def client(self) -> T_CLIENT:
        return self._client

    @client.setter
    def client(self, value: T_CLIENT):
        self._set_client(value)

    @property
    def logger(self) -> Logger:
        return self._logger

    # @property
    # def client(self) -> _U:
    #     return self._client

    @abstractmethod
    def on_client_connected(self, sender: T_CLIENT, event: ClientConnexionEvent):
        pass

    def instanciate_topic(self, raw_topic: RawTopic) -> Topic:

        for topic_cls in self._topic_cls:
            topic = topic_cls(raw_topic=raw_topic)

            if topic.is_valid:
                return topic

        return None

    # def on_message_received(self, sender: 'MQTTClient', topic: str, message: str):
    def on_message_received(self, sender: 'MQTTClient', event: MessageReceivedEvent):

        topic = event.topic
        message = event.payload

        self.logger.debug(f"MESSAGE RECEIVED TOPIC = {topic} MSG = {message}")
        # self._topic_interpretor.process(raw_topic=RawTopic(topic, message))
        self.process(raw_topic=RawTopic(topic, message))

    @abstractmethod
    def process(self, raw_topic: RawTopic):
        pass

        # self.client.subscribe_topic(topic="+/+/+/$connected")
        # self.client.publish_topic(topic=f"{self.client.home_topic}/$connected", payload="True", retain=True)


class ClientTopic(Topic):


    def __init__(self, raw_topic: RawTopic):
        super().__init__(raw_topic)

        self.environment_name: str = None
        self.environment_id: str = None
        self.client_id: str = None

    def _validate(self) -> bool:
        # Like => "SocialCage/01/STM01/$connected"
        if self.nb_levels == 3:
            self.environment_name = self.raw_topic[0]
            self.environment_id = self.raw_topic[1]
            self.client_id = self.raw_topic[2]

            return True

        return False

    @property
    def home_topic_str(self) -> str:
        return f"{self.environment_name}/{self.environment_id}/{self.client_id}"

class DeviceTopic(Topic):

    def __init__(self, raw_topic: RawTopic):
        super().__init__(raw_topic)

        self._client_topic: ClientTopic = None
        self._device_id: str = None

    @property
    def client_topic(self) -> ClientTopic:
        if self._client_topic is None:
            self._validate()

        return self._client_topic

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def home_topic_str(self) -> str:
        return f"{self.client_topic.home_topic_str}/{self.device_id}"

    def _validate(self) -> bool:
        # like SocialCage/01/STM01/lever_1/$type

        if self.nb_levels == 4:

            sub_topic = self.raw_topic.get_subtopic(0, 3)

            client_topic = ClientTopic(raw_topic=sub_topic)

            if client_topic.is_valid:
                self._client_topic = client_topic
                self._device_id = self.raw_topic[3]

                return True

        return False


class PropertyTopic(Topic):

    def __init__(self, raw_topic: RawTopic):
        super().__init__(raw_topic)

        self.device_topic: DeviceTopic = None
        self.property_id: str = None
        self._set: bool = False

    @property
    def client_topic(self) -> ClientTopic:
        if self.device_topic:
            return self.device_topic.client_topic

        return None

    # @property
    # def device_topic(self) -> DeviceTopic:
    #     return self._device_topic

    def _validate(self) -> bool:
        # like SocialCage/01/STM01/lever_1/state/$datatype

        if self.nb_levels <= 6:
            sub_topic = self.raw_topic.get_subtopic(0, 4)
            device_topic = DeviceTopic(raw_topic=sub_topic)

            if not device_topic.is_valid:
                return False

            self.device_topic = device_topic
            self.property_id = self.raw_topic[4]

            if self.nb_levels == 6:
                self._set = self.raw_topic[5] == "set"

            return True

        return False


