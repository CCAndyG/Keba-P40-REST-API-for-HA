from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        KebaStartChargingButton(coordinator, entry),
        KebaStopChargingButton(coordinator, entry),
    ])


class BaseKebaButton(CoordinatorEntity, ButtonEntity):

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def wallboxes(self):
        return self.coordinator.data.get("wallboxes") or []

    @property
    def serial(self):
        if not self.wallboxes:
            return None
        return self.wallboxes[0].get("serialNumber")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": "KEBA P40 Wallbox",
            "manufacturer": "KEBA",
            "model": "KeContact P40",
        }


class KebaStartChargingButton(BaseKebaButton):

    _attr_name = "Laden starten"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_start_charging"

    async def async_press(self):
        if self.serial:
            await self.coordinator.start_charging()


class KebaStopChargingButton(BaseKebaButton):

    _attr_name = "Laden stoppen"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_stop_charging"

    async def async_press(self):
        if self.serial:
            await self.coordinator.stop_charging()
