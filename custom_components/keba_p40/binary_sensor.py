from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        KebaPlugSensor(coordinator, entry),
    ])


class BaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def wb(self):
        data = self.coordinator.data or {}
        wallboxes = data.get("wallboxes") or []
        return wallboxes[0] if wallboxes else {}

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": "KEBA P40 Wallbox",
            "manufacturer": "KEBA",
            "model": "KeContact P40",
        }


class KebaPlugSensor(BaseBinarySensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_plug"
        self._attr_name = "Fahrzeug verbunden"

    @property
    def is_on(self):
        return self.wb.get("vehiclePlugged", False)
