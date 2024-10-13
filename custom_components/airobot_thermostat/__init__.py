from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .coordinator import AirobotDataUpdateCoordinator

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from yaml (not used here, since we use config flow)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up your integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize the DataUpdateCoordinator
    coordinator = AirobotDataUpdateCoordinator(
        hass, 
        entry.data["room"], 
        entry.data["host"], 
        entry.data["username"], 
        entry.data["password"]
    )

    # Store the coordinator so it's accessible in other parts of the integration
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator
    }

    # Fetch the first update to populate initial data
    await coordinator.async_config_entry_first_refresh()

    # Forward the setup to the platform (climate, sensor, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, ["climate", "sensor"])  # Properly await multiple setups


    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "climate")
    unload_ok = unload_ok and await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    # Remove the coordinator and clean up data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
