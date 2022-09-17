import json

from pysblibs.config import ConfigManager
from pysblibs.madoka import MadokaController
from pysblibs.mqtt import MqttController
from pysblibs.utils import register_device, get_mac_address


def mqtt_callback(self, client, userdata, message):
    self._logger.info(f"Message received on topic {message.topic}")
    self._logger.info(f"Message payload {message.payload}")

    if message.topic == f'{self._get_base_topics()}/commands':
        self._logger.info(f"Command received: {message.payload}")
        commands = json.loads(message.payload.decode('utf-8'))
        if 'fan_speed' in commands:
            self._logger.info(f"Fan speed command received: {commands['fan_speed']}")
            madoka.set_fan_speed(commands['fan_speed']['cool'], commands['fan_speed']['heat'])


madoka_mac_address = 'B8:F2:55:01:25:E0'

config = ConfigManager('config.json')

mac = get_mac_address()
data = register_device(config['reg_token'], mac)
config.set('user_id', data['user_id'])
config[('mqtt', 'host')] = data['mqtthost']
config[('mqtt', 'port')] = data['mqttport']
config[('mqtt', 'user')] = data['mqttusername']
config[('mqtt', 'password')] = data['mqttpassword']

mqtt_client = MqttController(config['mqtt']['host'],
                             int(config['mqtt']['port']),
                             config['mqtt']['user'],
                             config['mqtt']['password'],
                             config['user_id'])

mqtt_client.on_message_cb = mqtt_callback
mqtt_client.connect()

madoka = MadokaController(madoka_mac_address)

print(mqtt_client._get_base_topics())


while True:
    pass
a=2

