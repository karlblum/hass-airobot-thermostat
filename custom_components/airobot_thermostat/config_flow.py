import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_ROOM
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class AirobotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for custom thermostat."""

    VERSION = 1
    CONNECTION_CLASS = "local_polling"

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Try to connect to the device using the provided info
            try:
                room = user_input[CONF_ROOM]
                host = user_input[CONF_HOST]
                username = user_input[CONF_USERNAME]
                password = user_input[CONF_PASSWORD]
                
                # You can add some validation here by making a request to the thermostat
                # For example, you might want to check if /getStatuses endpoint is reachable.

                # If validation passes, we create the entry
                return self.async_create_entry(
                    title=room,
                    data=user_input
                )
            except Exception as e:
                _LOGGER.error("Error setting up thermostat: %s", e)
                errors["base"] = "connection_failed"

        # Show the form to the user
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_ROOM, default=""): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AirobotOptionsFlowHandler(config_entry)


class AirobotOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_show_form(step_id="init")
