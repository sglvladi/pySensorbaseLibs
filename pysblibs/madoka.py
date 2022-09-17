import asyncio

from pymadoka import force_device_disconnect, discover_devices, FanSpeedStatus, FanSpeedEnum
from pymadoka.connection import ConnectionStatus
from pymadoka.controller import Controller

from .base import Base


class MadokaController(Base):

    def __init__(self, mac_address, **kwargs):
        super().__init__(**kwargs)
        self.mac_address = mac_address
        self._controller = Controller(self.mac_address)

    def set_fan_speed(self, cool_speed: str, heat_speed: str):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._set_fan_speed(cool_speed, heat_speed))

    async def _connect(self):
        await force_device_disconnect(self._controller.connection.address)
        await discover_devices()
        await self._controller.start()
        return

    async def _set_fan_speed(self, cool_speed: str, heat_speed: str):
        if self._controller.connection.connection_status != ConnectionStatus.CONNECTED:
            await self._connect()
        fan_speed_status = FanSpeedStatus(FanSpeedEnum[cool_speed], FanSpeedEnum[heat_speed])
        return await self._controller.fan_speed.update(fan_speed_status)

