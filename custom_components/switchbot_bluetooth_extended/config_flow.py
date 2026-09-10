"""Set up Bots through Home Assistant's shared Bluetooth manager."""
from __future__ import annotations

import re
from typing import Any

import switchbot
import voluptuous as vol
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD

from .const import CONF_ADDRESS, CONF_NAME, DOMAIN


def _uid(address: str) -> str:
    """Preserve the unique IDs used by 0.1.0."""
    return address.replace(":", "").replace("-", "").lower()


def _short(address: str) -> str:
    return _uid(address)[-4:].upper()


def _normalize_address(address: str) -> str:
    address = address.strip()
    if not re.fullmatch(r"(?:[0-9a-fA-F]{12}|(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}|(?:[0-9a-fA-F]{2}-){5}[0-9a-fA-F]{2})", address):
        raise ValueError("Invalid BLE MAC address")
    compact = _uid(address).upper()
    return ":".join(compact[i:i + 2] for i in range(0, 12, 2))


def _parse_bot(info: BluetoothServiceInfoBleak):
    parsed = switchbot.parse_advertisement_data(info.device, info.advertisement)
    if not parsed or parsed.data.get("modelName") != switchbot.SwitchbotModel.BOT:
        return None
    return parsed


class SwitchBotExtendedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle discovery and manual setup without choosing a local adapter."""

    VERSION = 1

    def __init__(self) -> None:
        self._address: str | None = None
        self._bots: dict[str, str] = {}
        self._encrypted = False

    async def _async_set_address(self, address: str) -> None:
        await self.async_set_unique_id(_uid(address))
        self._abort_if_unique_id_configured()
        self._address = address

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> ConfigFlowResult:
        """Handle HA discovery, including advertisements received by proxies."""
        parsed = _parse_bot(discovery_info)
        if parsed is None:
            return self.async_abort(reason="not_supported")
        # An advertisement may come from a passive source while another HA
        # source can connect. Ask the manager instead of rejecting that source.
        if bluetooth.async_ble_device_from_address(
            self.hass, discovery_info.address.upper(), connectable=True
        ) is None:
            return self.async_abort(reason="not_connectable")
        await self._async_set_address(discovery_info.address)
        self._encrypted = bool(parsed.data.get("isEncrypted"))
        self.context["title_placeholders"] = {"name": f"Bot {_short(discovery_info.address)}"}
        return await self.async_step_confirm()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="user", menu_options=["select_device", "manual"])

    async def async_step_select_device(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            if address not in self._bots:
                return self.async_abort(reason="not_supported")
            await self._async_set_address(address)
            info = bluetooth.async_last_service_info(self.hass, address, connectable=False)
            parsed = _parse_bot(info) if info else None
            self._encrypted = bool(parsed and parsed.data.get("isEncrypted"))
            return await self.async_step_confirm()

        # Match Core: ask HA to scan, then parse its shared advertisement caches.
        await bluetooth.async_request_active_scan(self.hass)
        self._bots = {}
        current_ids = self._async_current_ids(include_ignore=False)
        for connectable in (True, False):
            for info in bluetooth.async_discovered_service_info(self.hass, connectable):
                if _uid(info.address) in current_ids or info.address in self._bots:
                    continue
                if _parse_bot(info) is None:
                    continue
                if bluetooth.async_ble_device_from_address(self.hass, info.address.upper(), connectable=True) is None:
                    continue
                self._bots[info.address] = f"Bot {_short(info.address)} ({info.address})"
        if not self._bots:
            return await self.async_step_manual()
        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(self._bots)}),
        )

    async def async_step_manual(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Accept a known MAC even if advertisement parsing cannot identify it."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                address = _normalize_address(user_input[CONF_ADDRESS])
            except ValueError:
                errors[CONF_ADDRESS] = "invalid_address"
            else:
                await self._async_set_address(address)
                await bluetooth.async_request_active_scan(self.hass)
                info = bluetooth.async_last_service_info(self.hass, address, connectable=False)
                parsed = switchbot.parse_advertisement_data(info.device, info.advertisement) if info else None
                if parsed and parsed.data.get("modelName") != switchbot.SwitchbotModel.BOT:
                    errors[CONF_ADDRESS] = "not_supported"
                elif bluetooth.async_ble_device_from_address(self.hass, address, connectable=True) is None:
                    errors["base"] = "not_connectable"
                else:
                    self._encrypted = bool(parsed and parsed.data.get("isEncrypted"))
                    return await self.async_step_confirm()
        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): str}),
            errors=errors,
        )

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        assert self._address is not None
        name = f"Bot {_short(self._address)}"
        if user_input is not None:
            # Recheck duplicates at submission, retaining 0.1.0 entry data/IDs.
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=name,
                data={CONF_ADDRESS: self._address, CONF_NAME: name, **user_input},
            )
        password_field = vol.Required(CONF_PASSWORD) if self._encrypted else vol.Optional(CONF_PASSWORD)
        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({password_field: str}),
            description_placeholders={"name": name, "address": self._address},
        )
