import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, HVACAction, ClimateEntityFeature, PRESET_HOME, PRESET_AWAY
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    thermostat = AirobotThermostat(coordinator)
    async_add_entities([thermostat], update_before_add=True)

class AirobotThermostat(CoordinatorEntity, ClimateEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"Airobot {coordinator._room} Thermostat"
        self._attr_unique_id = f"{DOMAIN}_{coordinator._username}_{coordinator._room}_climate"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_hvac_modes = [HVACMode.HEAT]
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_action = None
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        )
        self._attr_preset_modes = [PRESET_HOME, PRESET_AWAY]
        self._attr_preset_mode = None

    @property
    def preset_mode(self):
        mode = self.coordinator.data.get("preset_mode", 1)  # Default to Home
        if mode == 1:
            return PRESET_HOME
        elif mode == 2:
            return PRESET_AWAY
        return PRESET_HOME  # Default if unknown mode

    @property
    def current_temperature(self):
        return self.coordinator.data["temperature"]

    @property
    def target_temperature(self):
        return self.coordinator.data["setpoint_temp"]

    @property
    def hvac_action(self):
        return HVACAction.HEATING if self.coordinator.data["heating_on"] else HVACAction.IDLE

    @property
    def extra_state_attributes(self):
        return {
            "co2": self.coordinator.data["co2"],
            "aqi": self.coordinator.data["aqi"],
            "humidity": self.coordinator.data["humidity"]
        }
        
    async def async_set_temperature(self, **kwargs):
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if target_temperature is None:
            _LOGGER.error("No target temperature provided.")
            return

        await self.coordinator._set_temperature(target_temp=target_temperature)
        self._attr_target_temperature = target_temperature

        # Update the Home Assistant state
        await self.async_update_ha_state()

    async def async_set_preset_mode(self, preset_mode: str):
        if preset_mode not in self._attr_preset_modes:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)
            return

        # Call the coordinator's method to set the preset mode on the device
        # await self.coordinator._set_preset_mode(preset_mode)

        # Update the local state
        # self._attr_preset_mode = preset_mode

        # Request an update to reflect the new preset mode
        await self.async_update_ha_state()