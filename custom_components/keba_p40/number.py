from homeassistant.components.number import (
    NumberEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        KebaMaxCurrentNumber(coordinator, entry),
    ])


class KebaMaxCurrentNumber(
    CoordinatorEntity,
    NumberEntity,
):

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)

        self.entry = entry

        self._attr_unique_id = (
            f"{entry.entry_id}_max_current"
        )

        self._attr_name = (
            "Wallbox Maximalstrom"
        )

        self._attr_native_min_value = 6000
        self._attr_native_max_value = 16000
        self._attr_native_step = 500

        self._attr_native_unit_of_measurement = "mA"

    @property
    def configs(self):
        data = self.coordinator.data or {}
        return data.get("configs") or []

    @property
    def native_value(self):

        for config in self.configs:

            if (
                config.get("key")
                == "max_available_current"
            ):

                try:
                    return int(config.get("value"))
                except Exception:
                    return 6000

        return 6000

    async def async_set_native_value(
        self,
        value: float,
    ):

        await self.coordinator.set_max_current(
            int(value)
        )

    @property
    def available(self):
        return self.coordinator.data is not None

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.entry.entry_id)
            },
            "name": "KEBA P40 Wallbox",
            "manufacturer": "KEBA",
            "model": "KeContact P40",
        }