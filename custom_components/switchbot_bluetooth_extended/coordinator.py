"""Coordinator for SwitchBot Bluetooth Extended."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
import logging
from typing import Any

import switchbot
from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_PASSWORD
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_ADDRESS, CONF_NAME, DEFAULT_RETRY_COUNT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SwitchBotExtendedCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Manage one local SwitchBot Bot."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.address: str = entry.data[CONF_ADDRESS]
        self.device_name: str = entry.data.get(CONF_NAME, entry.title)
        self.device: switchbot.Switchbot | None = None
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{self.address}",
            update_interval=timedelta(minutes=15),
        )

    def _latest_parsed_advertisement(self):
        info = bluetooth.async_last_service_info(
            self.hass, self.address.upper(), connectable=True
        )
        if info is None:
            return None
        return switchbot.parse_advertisement_data(info.device, info.advertisement)

    def _ensure_device(self) -> switchbot.Switchbot:
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address.upper(), connectable=True
        )
        if ble_device is None:
            raise HomeAssistantError(
                f"SwitchBot {self.address} has no connectable Bluetooth route; "
                "check the ESPHome proxy's active connections and Bluetooth range"
            )
        if self.device is None:
            self.device = switchbot.Switchbot(
                device=ble_device,
                password=self.entry.data.get(CONF_PASSWORD),
                retry_count=DEFAULT_RETRY_COUNT,
            )
        parsed = self._latest_parsed_advertisement()
        if parsed is not None:
            if parsed.data.get("modelName") != switchbot.SwitchbotModel.BOT:
                raise HomeAssistantError(f"Bluetooth device {self.address} is not a Bot")
            self.device.update_from_advertisement(replace(parsed, device=ble_device))
        else:
            # Update the connection target even when a manually selected device
            # has no parseable advertisement yet. Use PySwitchbot's public API.
            self.device.update_from_advertisement(switchbot.SwitchBotAdvertisement(
                address=self.address, device=ble_device, rssi=-127, data={}
            ))
        return self.device

    async def _async_update_data(self) -> dict[str, Any]:
        """Refresh advertisement state and full Bot settings."""
        try:
            device = self._ensure_device()
            data: dict[str, Any] = dict(self.data or {})
            parsed = self._latest_parsed_advertisement()
            if parsed is not None:
                adv_data = parsed.data.get("data") or {}
                data.update(adv_data)
                data["rssi"] = parsed.rssi
            basic = await device.get_basic_info()
            if not basic:
                raise UpdateFailed("Bot returned no basic settings; check connectivity and password")
            data.update(basic)
            return data
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    async def async_refresh_after_command(self) -> None:
        """Refresh immediately after a write command."""
        await self.async_request_refresh()

    def _setting(self, key: str, default: Any) -> Any:
        return (self.data or {}).get(key, default)

    async def async_set_mode(self, switch_mode: bool) -> None:
        device = self._ensure_device()
        await device.set_switch_mode(
            switch_mode=switch_mode,
            strength=int(self._setting("strength", 100)),
            inverse=bool(self._setting("inverseDirection", False)),
        )
        await self.async_refresh_after_command()

    async def async_set_strength(self, strength: int) -> None:
        device = self._ensure_device()
        await device.set_switch_mode(
            switch_mode=bool(self._setting("switchMode", False)),
            strength=strength,
            inverse=bool(self._setting("inverseDirection", False)),
        )
        await self.async_refresh_after_command()

    async def async_set_inverse(self, inverse: bool) -> None:
        device = self._ensure_device()
        await device.set_switch_mode(
            switch_mode=bool(self._setting("switchMode", False)),
            strength=int(self._setting("strength", 100)),
            inverse=inverse,
        )
        await self.async_refresh_after_command()

    async def async_set_hold_seconds(self, seconds: int) -> None:
        device = self._ensure_device()
        await device.set_long_press(duration=seconds)
        await self.async_refresh_after_command()

    async def async_turn_on(self) -> None:
        device = self._ensure_device()
        if bool(self._setting("switchMode", False)):
            await device.turn_on()
        else:
            await device.press()
        await self.async_refresh_after_command()

    async def async_turn_off(self) -> None:
        device = self._ensure_device()
        if bool(self._setting("switchMode", False)):
            await device.turn_off()
        else:
            await device.press()
        await self.async_refresh_after_command()
