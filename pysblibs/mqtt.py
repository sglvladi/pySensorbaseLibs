import json
import random
from enum import Enum

import paho.mqtt.client as mqtt

from pysblibs.base import Base
from pysblibs.utils import get_mac_address, register_device


class MqttConnResult(Enum):
    """
    The result of a connection attempt.
    """
    SUCCESS = 0
    WRONG_PROTOCOL = 1
    INVALID_CLIENT_ID = 2
    SERVER_UNAVAILABLE = 3
    BAD_USERNAME_OR_PASSWORD = 4
    NOT_AUTHORIZED = 5


class MqttController(Base):

    def __init__(self, host, port, username, passwd, user_id, **kwargs):
        super().__init__(**kwargs)

        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.user_id = user_id

        self.client_id = f"{get_mac_address()}_{random.randint(0, 1000)}"
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.username_pw_set(username, password=passwd)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.on_message_cb = None

        self.connected = False

    @property
    def mac_address(self):
        return get_mac_address()

    def connect(self):
        self.client.connect(self.host, self.port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        rc = MqttConnResult(rc)
        if rc == MqttConnResult.SUCCESS:
            self._logger.info(f"Connected to MQTT broker {self.host}:{self.port}")
            self.connected = True

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            self._logger.info(f"Subscribing to topics")
            self.client.subscribe(f'{self._get_base_topics()}/delete')
            self.client.subscribe(f'{self._get_base_topics()}/fw_update')
            self.client.subscribe(f'{self._get_base_topics()}/restart')
            self.client.subscribe(f'{self._get_base_topics()}/commands')
            self.client.subscribe(f'{self._get_base_topics()}/sensors/+/input/+')
            self.client.subscribe(f'{self._get_base_topics()}/sensors/+/delete/+')

            # Set will topic
            self.client.will_set(f'{self._get_base_topics()}/disconnect', 1, 1)
        else:
            self._logger.error(f"Connection failed with result code {rc}: {self.__rc_to_str(rc)}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        self._logger.info(f"Disconnected with result code {rc}")
        self.connected = False

    def on_message(self, client, userdata, message):
        self._logger.info(f"Message received on topic {message.topic}")
        self._logger.info(f"Message payload {message.payload}")

        if self.on_message_cb is not None:
            self.on_message_cb(self, client, userdata, message)

    def get_topic(self, type: str, sensor_id: str = None):
        topic = f'{self._get_base_topics()}'

        if (type == 'input' or type == 'output') and sensor_id is None:
            self._logger.error(f"Sensor ID is required for type {type}")
            return None

        if sensor_id is not None:
            topic += f'/sensors/{sensor_id}'

        if type == 'delete_sensor':
            topic += f'/delete'
        elif type == 'input':
            topic += f'/input/value'
        elif type == 'output':
            topic += f'/output/value'
        else:
            topic += f'/{type}'
        return topic

    def send_message(self, type, sensor_id=None, payload=None, qos=1, retain=False):
        topic = self.get_topic(type, sensor_id)
        self.client.publish(topic, payload, qos, retain)

    def send_sensor_disconnect(self, sensor_id, payload=1, qos=1, retain=False):
        self.send_message('disconnect', sensor_id, payload, qos, retain)

    def send_device_disconnect(self, payload=1, qos=1, retain=False):
        self.send_message('disconnect', payload=payload, qos=qos, retain=retain)

    def send_sensor_debug(self, sensor_id, payload, qos=1, retain=False):
        self.send_message('debug', sensor_id, payload, qos, retain)

    def send_device_debug(self, payload, qos=1, retain=False):
        self.send_message('debug', payload, qos, retain)

    def _get_base_topics(self):
        return f'/{self.user_id}/devices//{self.mac_address}'

    def __rc_to_str(self, rc):
        return MqttConnResult(rc).name