from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTemperature
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor entities from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    entities = [
        AirobotTemperatureSensor(coordinator),
        AirobotHumiditySensor(coordinator),
        AirobotHeatingStatusSensor(coordinator)
    ]

    if coordinator.data.get("co2") is not None:
        entities.append(AirobotCO2Sensor(coordinator))

    if coordinator.data.get("floor_temperature_available"):
        entities.append(AirobotFloorTemperatureSensor(coordinator))

    async_add_entities(entities, update_before_add=True)

class AirobotTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Representation of the temperature sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Airobot {coordinator._room} Temp"
        self._attr_unique_id = f"{DOMAIN}_{coordinator._username}_{coordinator._room}_temp"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = "temperature"

    @property
    def state(self):
        return self.coordinator.data["temperature"]

class AirobotHumiditySensor(CoordinatorEntity, SensorEntity):
    """Representation of the humidity sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Airobot {coordinator._room} Humidity"
        self._attr_unique_id = f"{DOMAIN}_{coordinator._username}_{coordinator._room}_humidity"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = "humidity"

    @property
    def state(self):
        return self.coordinator.data["humidity"]

class AirobotCO2Sensor(CoordinatorEntity, SensorEntity):
    """Representation of the CO2 sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Airobot {coordinator._room} CO2"
        self._attr_unique_id = f"{DOMAIN}_{coordinator._username}_{coordinator._room}_co2"
        self._attr_native_unit_of_measurement = "ppm"
        self._attr_device_class = "carbon_dioxide"

    @property
    def state(self):
        return self.coordinator.data["co2"]

class AirobotHeatingStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of the heating status sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Airobot {coordinator._room} Heating Status"
        self._attr_unique_id = f"{DOMAIN}_{coordinator._username}_{coordinator._room}_heating_status"

    @property
    def state(self):
        """Return the state of the sensor."""
        heating_on = self.coordinator.data.get("heating_on")
        return "On" if heating_on else "Off"

    @property
    def icon(self):
        """Return an icon based on the heating status."""
        return "mdi:radiator" if self.state == "On" else "mdi:radiator-off"
        
class AirobotFloorTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Representation of the floor temperature sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Airobot {coordinator._room} Floor Temperature"
        self._attr_unique_id = f"{DOMAIN}_{coordinator._username}_{coordinator._room}_floor_temp"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = "temperature"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("floor_temperature")
