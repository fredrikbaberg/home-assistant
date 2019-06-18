import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    CONF_NAME, CONF_HOST, CONF_PORT, CONF_API_KEY, CONF_SSL,
    CONF_ALIAS, CONF_FRIENDLY_NAME, CONF_DEVICE, CONF_URL
)
from homeassistant.core import callback

from . import CONFIG_SCHEMA, DOMAIN, DEFAULT_NAME
from .octoprint import OctoPrint

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 80

CONF_HOSTNAME = "hostname"

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Required(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_API_KEY): cv.string
}, extra=vol.ALLOW_EXTRA)

@callback
def configured_devices(hass):
    """Return a set of the configured devices."""
    return {entry.data[CONF_NAME]: entry for entry
            in hass.config_entries.async_entries(DOMAIN)}

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
            vol.Required(CONF_ALIAS): str,
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Required(CONF_SSL): bool
        }
        return self.async_show_form(
            step_id='user',
            description_placeholders=self.device_config,
            data_schema=vol.Schema(data),
            errors=errors
        )

    async def async_step_zeroconf(self, discovery_info):
        """Prepare configuration for a discovered OctoPrint instance.
        
        Triggered by discovery or zeroconf component.
        Reference: See axis component config_flow.py.
        """
        device_id = discovery_info[CONF_NAME] # Use CONF_NAME as ID.
        self.context[CONF_NAME] = device_id
        # Check that device is not being configured.
        if any(device_id == flow['context'][CONF_NAME] for flow in self._async_in_progress()):
            _LOGGER.info("%s in progress.", device_id)
            return self.async_abort(reason='already_in_progress')
        # Check that device has not already been added.
        device_entries = {entry.data[CONF_NAME]: entry for entry in self._async_current_entries()}
        if device_id in device_entries:
            _LOGGER.info("%s already configured.", device_id)
            entry = device_entries[device_id]
            await self._update_entry(entry, discovery_info[CONF_HOST])
            return self.async_abort(reason='already_configured')
        # Should exctract if SSL is being used.
        _LOGGER.debug("Zeroconf: Found an Octoprint server: %s", discovery_info)
        self.discovery_schema = {
            vol.Optional(CONF_ALIAS, default=DEFAULT_NAME): str,
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_HOST, default=discovery_info[CONF_HOST]): str,
            vol.Required(CONF_PORT, default=discovery_info[CONF_PORT]): int
        }
        #device_config = DEVICE_SCHEMA({})
        #device_config[CONF_HOST] = DEVICE_SCHEMA(discovery_info)
        #_LOGGER.debug(device_config)
        # return await self.async_step_user()
        return await self.async_step_confirm()

    async def async_step_import(self, info):
        _LOGGER.debug("Import: Found an Octoprint server: %s", info)
        return await self.async_step_user()
        
    async def async_step_confirm(self, info=None):
        if info is None:
            return self.async_show_form(
               step_id='confirm'
            )
        return await self._create_entry(info)

    async def _create_entry(self, info):
        """Create entry for device.
        """
        _LOGGER.debug("Create entry \n%s", info)
        data = {
            CONF_NAME: "dev.local",
            CONF_URL: "http{}://{}:{}".format("", "", ""),
            CONF_HOST: "172.17.0.1",
            CONF_PORT: 5000,
            CONF_API_KEY: "85ee2a2d628fceec9da7e088baf1ea96"
        }
        title = "{} - {}".format("OctoPrint", "5000")
        return self.async_create_entry(
            title=title,
            data=data
        )
        
    async def _update_entry(self, entry, host):
        """Update existing entry if it is the same device."""
        _LOGGER.info("Update: %s, %s", entry, host)
        entry.data[CONF_HOST] = host
        self.hass.config_entries.async_update_entry(entry)