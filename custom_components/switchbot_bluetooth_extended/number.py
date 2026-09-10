"""Number entities for SwitchBot Bluetooth Extended."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfTime, UnitOfRatio
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SwitchBotExtendedConfigEntry
from .entity import SwitchBotExtendedEntity


async def async_setup_entry(hass, entry: SwitchBotExtendedConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        SwitchBotStrengthNumber(coordinator),
        SwitchBotHoldTimeNumber(coordinator),
    ])


class SwitchBotStrengthNumber(SwitchBotExtendedEntity, NumberEntity):
    _attr_translation_key = "strength"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfRatio.PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "strength")

    @property
    def native_value(self) -> float:
        return float((self.coordinator.data or {}).get("strength", 100))

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_strength(int(value))


class SwitchBotHoldTimeNumber(SwitchBotExtendedEntity, NumberEntity):
    _attr_translation_key = "press_hold_time"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 255
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "press-hold-time")

    @property
    def native_value(self) -> float:
        return float((self.coordinator.data or {}).get("holdSeconds", 0))

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_hold_seconds(int(value))
