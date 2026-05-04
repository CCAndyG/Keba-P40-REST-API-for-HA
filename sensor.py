from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        KebaStateSensor(coordinator, entry),
        KebaPowerSensor(coordinator, entry),
        KebaEnergySensor(coordinator, entry),
        KebaTempSensor(coordinator, entry),
    ])


class BaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def wb(self):
        data = self.coordinator.data or {}
        wallboxes = data.get("wallboxes") or []
        return wallboxes[0] if wallboxes else {}

    @property
    def meter(self):
        return self.wb.get("meter", {})

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


class KebaStateSensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_state"
        self._attr_name = "Wallbox Status"

    @property
    def native_value(self):
        return self.wb.get("state", "unknown")


class KebaPowerSensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_name = "Wallbox Leistung"
        self._attr_native_unit_of_measurement = "W"
        self._attr_device_class = "power"

    @property
    def native_value(self):
        return self.meter.get("totalActivePower", 0)


class KebaEnergySensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_energy"
        self._attr_name = "Wallbox Energie"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = "energy"
        self._attr_state_class = "total_increasing"

    @property
    def native_value(self):
        return self.meter.get("meterValue", 0)
        

class KebaTempSensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_temp"
        self._attr_name = "Wallbox Temperatur"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_class = "temperature"

    @property
    def native_value(self):
        value = self.meter.get("temperature")
        if value is None:
            return None
        return value / 100
