import asyncio
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        KebaPhaseSelect(coordinator, entry),
    ])


class KebaPhaseSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)

        self.entry = entry

        self._attr_unique_id = f"{entry.entry_id}_phase_select"
        self._attr_name = "Wallbox Phasen"

        self._attr_options = [
            "1-phasig",
            "3-phasig",
        ]
        
        # Wir starten standardmäßig mit der Anzeige "3-phasig"
        self._current_displayed_option = "3-phasig"

    @property
    def wallbox(self):
        data = self.coordinator.data or {}
        wallboxes = data.get("wallboxes") or []
        return wallboxes[0] if wallboxes else {}

    @property
    def current_option(self):
        # Zeigt immer den lokal gespeicherten Zustand an
        return self._current_displayed_option

    async def async_select_option(self, option: str):
        # Erzwingt das Senden, selbst wenn die Option optisch bereits ausgewählt war
        if option == "1-phasig":
            await self.coordinator.set_phases(1)
        elif option == "3-phasig":
            await self.coordinator.set_phases(3)

        # Zustand für die Anzeige aktualisieren
        self._current_displayed_option = option
        self.async_write_ha_state()

    @property
    def available(self):
        return self.coordinator.data is not None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": "KEBA P40 Wallbox",
            "manufacturer": "KEBA",
            "model": "KeContact P40",
        }
