import json
import socket
from abc import abstractmethod
from logging import Logger
from threading import Event, Thread
from time import sleep
from typing import Dict, Any

from mqtt_device.common.wait_until_success import wait_until_success
from mqtt_device.event_listener.listener import EventHandler, EventArgs
from obsub import event
from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTT_ERR_SUCCESS, MQTTv311

from mqtt_device.common.common_log import create_logger
from mqtt_device.common.exception import DeviceException

class MessageReceivedEvent(EventArgs):

    def __init__(self, topic_str: str, payload: str):
        self.topic = topic_str
        self.payload = payload

class ClientConnexionEvent(EventArgs):

    def __init__(self, is_connected: bool):
        self.is_connected = is_connected

class IMQTTClient:

    @property
    @abstractmethod
    def message_received(self) -> EventHandler[MessageReceivedEvent]:
        pass

    @event
    @abstractmethod
    def connexion_error(self, text: str):
        pass

    @property
    @abstractmethod
    def connected(self) -> EventHandler[ClientConnexionEvent]:
        pass


    @event
    def disconnected(self):
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        pass

    @property
    @abstractmethod
    def client_id(self) -> str:
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def wait_until_ended(self, timeout: int):
        pass

    @abstractmethod
    def publish_topic(self, topic: str, payload=None, qos=2, retain: bool=False, properties=None):
        pass

    @abstractmethod
    def subscribe_topic(self, topic: str, qos: int = 2):
        pass

    @abstractmethod
    def stop(self):
        pass

class MQTTClient(IMQTTClient):

    DEFAULT_PORT = 1883

    def __init__(self, client_id: str = None, broker_ip: str = None, broker_port: int = DEFAULT_PORT, keep_alive: int = 10, clean_session_at_start: bool = True):
        # print("#### INSTANCIATE MQTT")
        self._logger = create_logger(self)
        self._is_connected: bool = False
        self._is_running: bool = False

        # self._first_connexion = True
        self._client_id = client_id
        self._broker_ip = broker_ip if broker_port else MQTTClient.DEFAULT_PORT
        self._broker_port = broker_port

        self._clean_session_at_start = clean_session_at_start

        # when mqtt server don't receive connexion ping from this client > keep_alive s => send will_set testament
        self._keep_alive: int = keep_alive

        self._max_attempt: int = 3
        self.__mqtt_client: mqtt.Client = None

        # sync event
        self._is_finished_syncev = Event()

        # TODO => redundant with event to put it into Interface
        self._message_received: EventHandler[MessageReceivedEvent] = EventHandler(self)
        self._connected: EventHandler[ClientConnexionEvent] = EventHandler(self)


        #     @event
        #     def message_received(self, topic: str, message: str):
        #         pass

    @property
    def message_received(self) -> EventHandler[MessageReceivedEvent]:
        return self._message_received

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def connected(self) -> EventHandler[ClientConnexionEvent]:
        return self._connected

    @client_id.setter
    def client_id(self, value: str):
        self._client_id = value

    @property
    def broker_ip(self) -> str:
        return self._broker_ip

    @broker_ip.setter
    def broker_ip(self, value: str):
        self._broker_ip = value

    @property
    def broker_port(self) -> int:
        return self._broker_port

    @broker_port.setter
    def broker_port(self, value: int):
        self._broker_port = value

    @property
    def _mqtt_client(self) -> mqtt.Client:

        if not self.__mqtt_client:
            self._init_client()

        return self.__mqtt_client

    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    @property
    def is_running(self) -> bool:
        return self._is_running
    
    @is_running.setter
    def is_running(self, value: bool):

        self.logger.error(f"##### RUNNING TURN TO {value}")
        if value is True:
            self._is_finished_syncev.clear()
        else:
            self._is_finished_syncev.set()

        self._is_running = value

    def subscribe_topic(self, topic: str, qos: int = 2):

        if not self.is_connected:
            err_msg = f"Client '{self._client_id}' is not connected to a MQTT broker, unable to subscribe to topic : '{topic}'"
            self.logger.error(err_msg)

            raise DeviceException(err_msg)
        else:
            self.logger.info(f"Client '{self._client_id}' susbcribe to : '{topic}'")
            # self.subscribe_topic(topic=topic)
            self._mqtt_client.subscribe(topic, qos=qos)

    # SIMPLE WRAPPER
    def publish_topic(self, topic: str, payload=None, qos=2, retain: bool=False, properties=None):

        if not self.is_connected:
            self.logger.info(f"Client '{self._client_id}' is not connected to a MQTT broker, message '{topic}' with payload: '{payload}' could not not be send")
        else:
            self.logger.info(f"Client '{self._client_id}' publish to : '{topic}' with payload : {payload} (retain='{retain}')")
            # self.publish_topic(topic=topic, payload=payload, retain=retain, properties=properties)
            self._mqtt_client.publish(topic=topic, payload=payload, retain=retain, properties=properties, qos=qos)

    def disconnect(self):

        if self._mqtt_client:
            self._mqtt_client.disconnect()
            self._mqtt_client.loop_stop()
            self.is_running = False


    def connect(self):

        if self._clean_session_at_start:
            self._connect(clean_session=True)

        self._connect(clean_session=False)

    def _connect(self, clean_session: bool = False):

        num_attempt: int = 0

        broker_ip = self._broker_ip
        broker_port = self._broker_port

        self._init_client(clean_session=clean_session)


        while not self.is_connected:

            if num_attempt >= self._max_attempt:
                # from mqtt_device.common import DeviceException
                err_msg = f"Unable to connect to mqtt : '{broker_ip}:{broker_port}'"
                self.logger.error(err_msg)
                self.connexion_error(err_msg)
                raise DeviceException(err_msg)

            num_attempt += 1

            res = self._try_to_connect()

            if not res:
                self.logger.info(f"Attempt num : {num_attempt}/{self._max_attempt} failed")
                sleep(1)

        # send event only in "normal" mode connexion (to try to avoid bug at connexion time)
        if not clean_session:
            self.connected(ClientConnexionEvent(is_connected=True))

        self.logger.info(f"Client id '{self._client_id}' is connected")

    def _init_client(self, clean_session: bool = False):

        if self._is_connected:
            self._mqtt_client.disconnect()

        self._is_connected = False
        self._is_running = False

        self.logger.info(f"Initialize MQTT Client : {self._client_id}")

        if not self._client_id:
            raise DeviceException(f"Client id could not be None")

        # protocol = MQTTv5
        protocol = MQTTv311

        # clean session need to be false
        self.logger.info(f"Client id '{self._client_id}' created with clean_session='{clean_session}'")
        client = mqtt.Client(client_id=self._client_id, clean_session=clean_session, protocol=protocol)

        client.on_message = self._on_message
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect

        self.__mqtt_client = client

    def will_set(self, topic: str, payload=None, qos=2, retain: bool=False, properties=None):

        mqtt_client = self._mqtt_client
        mqtt_client.will_set(topic=topic, payload=payload, qos=qos, retain=retain)


    def _try_to_connect(self) -> bool:

        broker_ip = self._broker_ip
        broker_port = self._broker_port

        if not broker_port:
            broker_port = 1883

        try:

            self._mqtt_client.connect(host=broker_ip, port=broker_port, keepalive=self._keep_alive)
        except ConnectionRefusedError as exc:
            self.logger.error(f"Connexion error : {exc}")
            return False
        except socket.timeout as exc:
            self.logger.error(f"Connexion error : {exc}")
            return False

        self._start()
        # wait to switch of thread context and update is_connected status
        sleep(0.01)

        return self.is_connected

    def _on_disconnect(self, client: mqtt.Client, userdata, rc: int):
        self.logger.info(f"Client '{self._client_id}' Disconnected with rc:{rc}")
        self._is_connected = False
        self.disconnected()

    def _on_message(self, client: mqtt.Client, user_data: Any, message: mqtt.MQTTMessage):

        str_message = message.payload.decode(encoding='utf-8')

        self.logger.debug(f"Message received by client: {self._client_id} => topic:'{message.topic}' message:'{str_message}' retain:'{message.retain}'")
        # raise event
        # self.message_received(topic=message.topic, message=str_message)
        # TODO : with redundant event (replace the previous one?)
        self.message_received(event=MessageReceivedEvent(topic_str=message.topic, payload=str_message))

    def _on_connect(self, client: mqtt.Client, userdata, flags: Dict[str, int], rc: int):

        if rc == MQTT_ERR_SUCCESS:
            self._is_connected = True

            self.logger.debug(f"Mqtt Client '{self._client_id}': '{self._broker_ip}:{self._broker_port}' connected")

    def _start(self):

        if not self._is_running:

            self.logger.debug(f"Loop for client id '{self._client_id}' started")
            self._mqtt_client.loop_start()
            # rename the thread
            self._mqtt_client._thread.name = f"mqtt_{self._client_id}"
            self.is_running = True

        else:
            self.logger.warning(f"Client '{self._client_id}' is already started")

    def wait_until_ended(self, timeout: float = None) -> bool:
        res = self._is_finished_syncev.wait()
        return res

    def __del__(self):
        self.stop()

    def stop(self):

        if self._is_running:
            # self._mqtt_client.loop_stop()
            # self.logger.debug(f"Mqtt Client id '{self._client_id}' has ended the listening loop")
            self._mqtt_client.disconnect()
            self.is_running = False