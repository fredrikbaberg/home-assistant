import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    CONF_NAME, CONF_HOST, CONF_PORT, CONF_API_KEY, CONF_SSL
)

from . import CONFIG_SCHEMA
from .octoprint import OctoPrint

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'OctoPrint'
DOMAIN = 'octoprint'

@config_entries.HANDLERS.register(DOMAIN)
class OctoPrintFlowHandler(config_entries.ConfigFlow):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH
    
    def __init__(self):
        self.device_config = {}
        self.discovery_schema = {}
        self.import_schema = {}
    
    async def async_step_user(self, user_input=None):
        _LOGGER.debug("User: Setup with\n%s", user_input)
        errors = {}
        if user_input is not None:
            _LOGGER.debug("User: Got data to create device:\n%s", user_input)
            OP = OctoPrint(user_input[CONF_HOST], user_input[CONF_PORT])
            if not OP.get_api_key(user_input[CONF_NAME]):
                return self.async_abort(reason='connection_error')
            _LOGGER.debug("API key: %s", OP.api_key)
            return await self._create_entry()
        # If user_input is None, use discovered data or create new schema.
        if self.import_schema:
            _LOGGER.debug("Import schema:\n%s", self.import_schema)
        if self.discovery_schema:
            _LOGGER.debug("Discovery schema:\n%s", self.discovery_schema)
        data = self.import_schema or self.discovery_schema or {
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT): int
        }
        return self.async_show_form(
            step_id='user',
            description_placeholders=self.device_config,
            data_schema=vol.Schema(data),
            errors=errors
        )

    async def async_step_zeroconf(self, discovery_info):
        # Handle zeroconf discovery.
        _LOGGER.debug("Zeroconf: Found an Octoprint server: %s", discovery_info)
        ## Should perform checks, see config_flow.py in axis component.
        # Check that device is not being configured.
        # return self.async_abort(reason='already_in_progress')
        # Check that device has not already been added.
        # return self.async_abort(reason='already_configured')
        # Exctract if SSL is being used.
        self.discovery_schema = {
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_HOST, default=discovery_info[CONF_HOST]): str,
            vol.Required(CONF_PORT, default=discovery_info[CONF_PORT]): int
        }
        return await self.async_step_user()

    async def async_step_import(self, info):
        _LOGGER.debug("Import: Found an Octoprint server: %s", info)
        return await self.async_step_user()
        
    async def _create_entry(self):
        """Create entry for device.
        """
        _LOGGER.debug("Create entry")
        data = {
            CONF_NAME: "OctoPrint"
        }
        title = "{} - {}".format("OctoPrint", "5000")
        return self.async_create_entry(
            title=title,
            data=data
        )
