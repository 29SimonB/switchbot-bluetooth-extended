"""Select entities for SwitchBot Bluetooth Extended."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SwitchBotExtendedConfigEntry
from .const import MODE_PRESS, MODE_SWITCH
from .entity import SwitchBotExtendedEntity


async def async_setup_entry(hass, entry: SwitchBotExtendedConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([SwitchBotModeSelect(entry.runtime_data)])


class SwitchBotModeSelect(SwitchBotExtendedEntity, SelectEntity):
    """Press/Switch mode selector."""

    _attr_translation_key = "mode"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = [MODE_PRESS, MODE_SWITCH]

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "mode")

    @property
    def current_option(self) -> str:
        return MODE_SWITCH if bool((self.coordinator.data or {}).get("switchMode", False)) else MODE_PRESS

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_mode(option == MODE_SWITCH)
