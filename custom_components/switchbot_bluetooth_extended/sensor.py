"""Diagnostic sensors for SwitchBot Bluetooth Extended."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfRatio
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SwitchBotExtendedConfigEntry
from .entity import SwitchBotExtendedEntity


async def async_setup_entry(hass, entry: SwitchBotExtendedConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        SwitchBotBatterySensor(coordinator),
        SwitchBotFirmwareSensor(coordinator),
        SwitchBotRSSISensor(coordinator),
    ])


class SwitchBotBatterySensor(SwitchBotExtendedEntity, SensorEntity):
    _attr_translation_key = "battery"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfRatio.PERCENTAGE

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "battery")

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("battery")


class SwitchBotFirmwareSensor(SwitchBotExtendedEntity, SensorEntity):
    _attr_translation_key = "firmware"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "firmware")

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("firmware")


class SwitchBotRSSISensor(SwitchBotExtendedEntity, SensorEntity):
    _attr_translation_key = "bluetooth_signal"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "rssi")

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("rssi")
