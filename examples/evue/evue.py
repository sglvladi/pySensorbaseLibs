import logging
import json
import time
import socket

from pyemvue import pyemvue
from pyemvue.enums import Scale, Unit

from pysblibs.config import ConfigManager
from pysblibs.mqtt import MqttController
from pysblibs.utils import register_device, get_mac_address

logger = logging.getLogger('pysblibs.base')
formatter = logging.Formatter(
    "(%(asctime)s) [%(levelname)s:%(module)s:%(lineno)d]: %(message)s",
    "%H:%M:%S")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # connect() for UDP doesn't send packets
    s.connect(('10.0.0.0', 0))
    return s.getsockname()[0]


def print_recursive(usage_dict, info, depth=0):
    for gid, device in usage_dict.items():
        for channelnum, channel in device.channels.items():
            name = channel.name
            if name == 'Main':
                name = info[gid].device_name
            if channel.usage is None:
                continue
            print('-'*depth, f'{gid} {channelnum} {name} {channel.usage*60*60} kW')
            if channel.nested_devices:
                print_recursive(channel.nested_devices, info, depth+1)


def send_recursive(mqtt_client, usage_dict, info, depth=0):
    for gid, device in usage_dict.items():
        for channelnum, channel in device.channels.items():
            name = channel.name
            if name == 'Main':
                name = info[gid].device_name
            if name is None:
                channelnum = 9
            elif name == 'Balance':
                continue
            if channel.usage is None:
                continue
            mqtt_client.send_message('output', f'P{channelnum}', round(channel.usage*60*60*1e3))


def mqtt_callback(self, client, userdata, message):
    self._logger.info(f"Message received on topic {message.topic}")
    self._logger.info(f"Message payload {message.payload}")

    # if message.topic == f'{self._get_base_topics()}/commands':
    #     self._logger.info(f"Command received: {message.payload}")
    #     commands = json.loads(message.payload.decode('utf-8'))
    #     if 'fan_speed' in commands:
    #         self._logger.info(f"Fan speed command received: {commands['fan_speed']}")
    #         madoka.set_fan_speed(commands['fan_speed']['cool'], commands['fan_speed']['heat'])


def main():

    config = ConfigManager('config.json')

    mac = get_mac_address()
    payload = {
        "mac": mac,
        "model": config['model'],
        "hw_version": config['hw_version'],
        "fw_version": config['fw_version'],
        "token": config['reg_token'],
        "local_ip": get_local_ip()
    }
    data = register_device(payload)
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

    print(mqtt_client._get_base_topics())

    while True:
        devices = vue.get_devices()
        device_gids = []
        device_info = {}
        for device in devices:
            if not device.device_gid in device_gids:
                device_gids.append(device.device_gid)
                device_info[device.device_gid] = device
            else:
                device_info[device.device_gid].channels += device.channels

        device_usage_dict = vue.get_device_list_usage(deviceGids=device_gids, instant=None,
                                                      scale=Scale.SECOND.value,
                                                      unit=Unit.KWH.value)
        print('device_gid channel_num name usage unit')
        print_recursive(device_usage_dict, device_info)
        print('------------------------------------------')
        mqtt_client.send_device_disconnect(0)
        mqtt_client.send_message('output', 'RSSI', -50)
        send_recursive(mqtt_client, device_usage_dict, device_info)
        time.sleep(30)


vue = pyemvue.PyEmVue()
vue.login(username='sglvladi@gmail.com', password='neonJamon546!', token_storage_file='keys.json')
main()

a=2

