"""Switch entities for SwitchBot Bluetooth Extended."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SwitchBotExtendedConfigEntry
from .entity import SwitchBotExtendedEntity


async def async_setup_entry(hass, entry: SwitchBotExtendedConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        SwitchBotControlSwitch(coordinator),
        SwitchBotReverseSwitch(coordinator),
    ])


class SwitchBotControlSwitch(SwitchBotExtendedEntity, SwitchEntity):
    """Main Bot control. In Press mode, both HA actions press the Bot."""

    _attr_name = None
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "control")
        self._assumed_on = False

    @property
    def assumed_state(self) -> bool:
        return not bool((self.coordinator.data or {}).get("switchMode", False))

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        if not bool(data.get("switchMode", False)):
            return self._assumed_on
        state = data.get("isOn")
        return bool(state) if state is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_turn_on()
        self._assumed_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_turn_off()
        self._assumed_on = False

    @property
    def extra_state_attributes(self):
        return {"switch_mode": bool((self.coordinator.data or {}).get("switchMode", False))}


class SwitchBotReverseSwitch(SwitchBotExtendedEntity, SwitchEntity):
    """Reverse on/off directions setting."""

    _attr_translation_key = "reverse_direction"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "reverse-direction")

    @property
    def available(self) -> bool:
        """Reverse only applies when the Bot reports Switch mode."""
        return super().available and bool(
            (self.coordinator.data or {}).get("switchMode", False)
        )


    @property
    def is_on(self) -> bool:
        return bool((self.coordinator.data or {}).get("inverseDirection", False))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_inverse(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_inverse(False)
