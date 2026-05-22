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

    @property
    def wallbox(self):
        data = self.coordinator.data or {}
        wallboxes = data.get("wallboxes") or []
        return wallboxes[0] if wallboxes else {}

    @property
    def current_option(self):
        phase_used = self.wallbox.get("phaseUsed")

        if phase_used == "L1":
            return "1-phasig"

        return "3-phasig"

    async def async_select_option(self, option: str):
        if option == "1-phasig":
            await self.coordinator.set_phases(1)

        elif option == "3-phasig":
            await self.coordinator.set_phases(3)

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