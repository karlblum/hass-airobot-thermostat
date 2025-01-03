import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.climate.const import PRESET_HOME, PRESET_AWAY
import aiohttp
import base64
from .const import API_URL_STATUS, API_URL_GET_SETTINGS, API_URL_SET_SETTINGS, DOMAIN

_LOGGER = logging.getLogger(__name__)

class AirobotDataUpdateCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, room, host, username, password):
        """Initialize the coordinator."""
        self._room = room
        self._host = host
        self._username = username
        self._password = password

        super().__init__(
            hass,
            _LOGGER,
            name=f"Airobot Thermostat {self._room}",
            update_interval=timedelta(seconds=15),
        )

    def _get_headers(self):
        """Return the headers for REST API with proper Basic Authentication."""
        credentials = f"{self._username}:{self._password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}"
        }

    async def _async_update_data(self):
        status_url = f"http://{self._host}{API_URL_STATUS}"
        get_settings_url = f"http://{self._host}{API_URL_GET_SETTINGS}"

        _LOGGER.debug("Fetching status data from URL: %s", status_url)
        _LOGGER.debug("Fetching settings data from URL: %s", get_settings_url)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch data from the status API
                async with session.get(status_url, headers=self._get_headers()) as status_response:
                    if status_response.status != 200:
                        raise UpdateFailed(f"Failed to fetch status data: {status_response.status}")
                    status_data = await status_response.json()

                    # Log the received status data for debugging
                    _LOGGER.debug("Received status data from thermostat: %s", status_data)

                # Fetch data from the settings API (for mode)
                async with session.get(get_settings_url, headers=self._get_headers()) as settings_response:
                    if settings_response.status != 200:
                        raise UpdateFailed(f"Failed to fetch settings data: {settings_response.status}")
                    settings_data = await settings_response.json()

                    # Log the received settings data for debugging
                    _LOGGER.debug("Received settings data from thermostat: %s", settings_data)

            preset_mode = settings_data.get("MODE", 1)  # Default to 1 (Home mode)
            setpoint_temp = settings_data.get("SETPOINT_TEMP_AWAY", 0) / 10 if preset_mode == 2 else settings_data.get("SETPOINT_TEMP", 0) / 10
            # Check if CO2 is valid (not 65535)
            co2_value = status_data.get("CO2", 65535)
            if co2_value == 65535:
                co2_value = None  # Set to None to indicate no valid CO2 reading

            hum_air_value = status_data.get("HUM_AIR", 0) / 10
            if hum_air_value > 100:
                hum_air_value = None
            
            temp_air_value = status_data.get("TEMP_AIR", 0) / 10
            if temp_air_value > 100:
                temp_air_value = None

            floor_temperature = status_data.get("TEMP_FLOOR", 0) / 10
            floor_temperature_available = 0 < floor_temperature < 100
            if not floor_temperature_available:
                floor_temperature = None


            return {
                "temperature": temp_air_value,
                "floor_temperature": floor_temperature,
                "floor_temperature_available": floor_temperature_available,
                "humidity": hum_air_value,
                "co2": co2_value,
                "aqi": status_data.get("AQI", 0),
                "setpoint_temp": setpoint_temp,
                "preset_mode": preset_mode,
                "heating_on": status_data.get("STATUS_FLAGS", [{}])[0].get("HEATING_ON", 0),
            }
        
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Network error: {e}")
        except ValueError as e:
            raise UpdateFailed(f"JSON decoding error: {e}")
        except Exception as e:
            raise UpdateFailed(f"Unexpected error: {e}")
    
    async def _set_temperature(self, target_temp: float):
        url = f"http://{self._host}{API_URL_SET_SETTINGS}"
        _LOGGER.debug("Setting temperature to %s on URL: %s", target_temp, url)
        
        # Determine which field to update based on the current mode: 1 = Home, 0 = Away
        current_mode = self.data.get("mode", 1)  # Default to Home if mode is missing

        # Select the correct temperature field based on the mode
        temp_field = "SETPOINT_TEMP" if current_mode == 1 else "SETPOINT_TEMP_AWAY"

        # Construct the payload
        payload = {
            "DEVICE_ID": self._username,  # Assuming the username is used as DEVICE_ID
            temp_field: int(target_temp * 10),  # Convert temperature to tenths of a degree
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self._get_headers()) as response:
                    _LOGGER.debug("Response status: %s", response.status)
                    
                    if response.status != 200:
                        response_text = await response.text()
                        _LOGGER.error("Failed to set temperature. Status: %s, Response: %s", response.status, response_text)
                        raise UpdateFailed(f"Failed to set temperature: {response.status}")

                    # Log success and return the response for further use if needed
                    _LOGGER.info("Successfully set temperature to %s", target_temp)

        except aiohttp.ClientError as e:
            _LOGGER.error("Network error when setting temperature on %s: %s", self._host, str(e))
            raise UpdateFailed(f"Network error: {e}")
        except ValueError as e:
            _LOGGER.error("JSON decoding error: %s. Response text: %s", str(e), traceback.format_exc())
            raise UpdateFailed(f"JSON decoding error: {e}")
        except Exception as e:
            _LOGGER.error("Unexpected error: %s. Traceback: %s", str(e), traceback.format_exc())
            raise UpdateFailed(f"Unexpected error: {e}")
    
    # this function is not available because Airobot does not supporting each thermostat mode independently
    # at least in the official app it allows only changing whole home status.
    """
    async def _set_preset_mode(self, preset_mode: str):
        url = f"http://{self._host}{API_URL_SET_SETTINGS}"
        
        # Determine the mode-specific settings (e.g., temperature for home/away)
        if preset_mode == PRESET_HOME:
            mode = 1  # Example mode for "Home"
        elif preset_mode == PRESET_AWAY:
            mode = 2  # Example mode for "Away"
        else:
            _LOGGER.error("Unsupported preset mode: %s", preset_mode)
            return

        payload = {
            "DEVICE_ID": self._username,
            "MODE": mode
        }

        _LOGGER.debug("Setting preset mode to %s with payload: %s", preset_mode, payload)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self._get_headers()) as response:
                    _LOGGER.debug("Response status: %s", response.status)

                    if response.status != 200:
                        response_text = await response.text()
                        _LOGGER.error("Failed to set preset mode. Status: %s, Response: %s", response.status, response_text)
                        raise UpdateFailed(f"Failed to set preset mode: {response.status}")

                    _LOGGER.info("Successfully set preset mode to %s", preset_mode)

        except aiohttp.ClientError as e:
            _LOGGER.error("Network error when setting preset mode on %s: %s", self._host, str(e))
            raise UpdateFailed(f"Network error: {e}")
        except Exception as e:
            _LOGGER.error("Unexpected error: %s. Traceback: %s", str(e), traceback.format_exc())
            raise UpdateFailed(f"Unexpected error: {e}")
    """