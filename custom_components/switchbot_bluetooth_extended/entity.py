"""Base entity for SwitchBot Bluetooth Extended."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwitchBotExtendedCoordinator


class SwitchBotExtendedEntity(CoordinatorEntity[SwitchBotExtendedCoordinator]):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SwitchBotExtendedCoordinator, suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.address.replace(':', '').lower()}-{suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address.upper())},
            connections={("bluetooth", coordinator.address.upper())},
            manufacturer="SwitchBot",
            model="WoHand",
            name=coordinator.device_name,
        )
