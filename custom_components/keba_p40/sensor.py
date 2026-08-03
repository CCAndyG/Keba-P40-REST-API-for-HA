from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        KebaSerialNumSensor(coordinator, entry),
        KebaStateSensor(coordinator, entry),
        KebaPVState(coordinator, entry),
        KebaLeistungsfaktSensor(coordinator, entry),
        KebaPowerSensor(coordinator, entry),
        KebaEnergySensor(coordinator, entry),
        KebaTempSensor(coordinator, entry),
        # Neue Phasensensoren (Spannung)
        KebaVoltageL1Sensor(coordinator, entry),
        KebaVoltageL2Sensor(coordinator, entry),
        KebaVoltageL3Sensor(coordinator, entry),
        # Neue Phasensensoren (Strom)
        KebaCurrentL1Sensor(coordinator, entry),
        KebaCurrentL2Sensor(coordinator, entry),
        KebaCurrentL3Sensor(coordinator, entry),
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

    def _get_line_data(self, phase_name: str) -> dict:
        """Hilfsfunktion, um die Daten einer bestimmten Phase (L1, L2, L3) zu extrahieren."""
        lines = self.meter.get("lines") or []
        for line in lines:
            if line.get("socketPhase") == phase_name:
                return line
        return {}


class KebaSerialNumSensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_serialNumber"
        self._attr_name = "Wallbox Seriennummer"

    @property
    def native_value(self):
        return self.wb.get("serialNumber", "unknown")


class KebaStateSensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_state"
        self._attr_name = "Wallbox Status"

    @property
    def native_value(self):
        return self.wb.get("state", "unknown")


class KebaPVState(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_pv_status"
        self._attr_name = "Wallbox PV Status"

    @property
    def native_value(self):
        return self.coordinator.data.get("pvstatus", {}).get("pvStatus", "unknown")


class KebaLeistungsfaktSensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_totalPowerFactor"
        self._attr_name = "Wallbox Leistungsfaktor"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        value = self.meter.get("totalPowerFactor")
        return (value / 10) if value is not None else 0 


class KebaPowerSensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_name = "Wallbox Leistung"
        self._attr_native_unit_of_measurement = "kW"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        value = self.meter.get("totalActivePower")
        return (value / 1000000) if value is not None else 0 


class KebaEnergySensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_energy"
        self._attr_name = "Wallbox Energie"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        value = self.meter.get("meterValue")
        return (value / 1000000) if value is not None else 0        


class KebaTempSensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_temp"
        self._attr_name = "Wallbox Temperatur"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self):
        value = self.meter.get("temperature")
        if value is None:
            return None
        return value / 100


# ==============================================================================
# SPANNUNGSSENSOREN (VOLTAGE)
# ==============================================================================

class KebaVoltageL1Sensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_voltage_l1"
        self._attr_name = "Wallbox Spannung L1"
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        line = self._get_line_data("L1")
        return line.get("voltage")


class KebaVoltageL2Sensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_voltage_l2"
        self._attr_name = "Wallbox Spannung L2"
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        line = self._get_line_data("L2")
        return line.get("voltage")


class KebaVoltageL3Sensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_voltage_l3"
        self._attr_name = "Wallbox Spannung L3"
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        line = self._get_line_data("L3")
        return line.get("voltage")


# ==============================================================================
# STROMSENSOREN (CURRENT)
# ==============================================================================

class KebaCurrentL1Sensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_l1"
        self._attr_name = "Wallbox Strom L1"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        line = self._get_line_data("L1")
        value = line.get("current")
        return (value / 1000) if value is not None else None


class KebaCurrentL2Sensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_l2"
        self._attr_name = "Wallbox Strom L2"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        line = self._get_line_data("L2")
        value = line.get("current")
        return (value / 1000) if value is not None else None


class KebaCurrentL3Sensor(BaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_l3"
        self._attr_name = "Wallbox Strom L3"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        line = self._get_line_data("L3")
        value = line.get("current")
        return (value / 1000) if value is not None else None
