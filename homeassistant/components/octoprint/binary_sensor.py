"""Support for monitoring OctoPrint binary sensors."""
import logging
import time

import requests

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.core import callback

from .octoprint import OctoPrint

from . import BINARY_SENSOR_TYPES, DOMAIN as COMPONENT_DOMAIN, _LOGGER

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up OctoPrint binary sensor from a config entry."""
    devices = [OctoPrintBinarySensor('bin1', hass.data[COMPONENT_DOMAIN]['config'])]
    async_add_entities(devices, update_before_add=True)
    return True
    
async def async_remove_entry(hass, entry) -> None:
    """Handle removal of an entry."""
    _LOGGER.info("Remove binary_sensor\n%s", entry)
    
class OctoPrintBinarySensor(BinarySensorDevice):
    """Representation an OctoPrint binary sensor."""
    def __init__(self, name, api):
        """Initialize a new OctoPrint sensor."""
        self._is_on = False
        self._name = name
        self._available = True
        self._api = api
    
    @property
    def name(self):
        """Name of the device."""
        return self._name
        
    @property
    def available(self):
        """Device available."""
        return self._available

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on
        
    @property
    def device_info(self):
        return {
            'identifiers': {(DOMAIN, 'binary')},
            'manufacturer': 'OctoPrint',
            'model': 'OctoPrint binary sensor',
            'name': 'Octoprint binary',
            'sw_version': '0.0.2',
            'via_hub': (DOMAIN, '101hero'),
            'via_device': (DOMAIN, '101hero')
        }

    async def async_update(self):
        """Update data."""
        _LOGGER.debug("Async update: %s", self._api.api_key)
        return True

# def setup_platform(hass, config, add_entities, discovery_info=None):
#     """Set up the available OctoPrint binary sensors."""
#     if discovery_info is None:
#         return

#     name = discovery_info['name']
#     base_url = discovery_info['base_url']
#     monitored_conditions = discovery_info['sensors']
#     octoprint_api = hass.data[COMPONENT_DOMAIN][base_url]

#     devices = []
#     for octo_type in monitored_conditions:
#         new_sensor = OctoPrintBinarySensor(
#             octoprint_api, octo_type, BINARY_SENSOR_TYPES[octo_type][2],
#             name, BINARY_SENSOR_TYPES[octo_type][3],
#             BINARY_SENSOR_TYPES[octo_type][0],
#             BINARY_SENSOR_TYPES[octo_type][1], 'flags')
#         devices.append(new_sensor)
#     add_entities(devices, True)


# class OctoPrintBinarySensor(BinarySensorDevice):
#     """Representation an OctoPrint binary sensor."""

#     def __init__(self, api, condition, sensor_type, sensor_name, unit,
#                  endpoint, group, tool=None):
#         """Initialize a new OctoPrint sensor."""
#         self.sensor_name = sensor_name
#         if tool is None:
#             self._name = '{} {}'.format(sensor_name, condition)
#         else:
#             self._name = '{} {}'.format(sensor_name, condition)
#         self.sensor_type = sensor_type
#         self.api = api
#         self._state = False
#         self._unit_of_measurement = unit
#         self.api_endpoint = endpoint
#         self.api_group = group
#         self.api_tool = tool
#         _LOGGER.debug("Created OctoPrint binary sensor %r", self)

#     @property
#     def name(self):
#         """Return the name of the sensor."""
#         return self._name

#     @property
#     def is_on(self):
#         """Return true if binary sensor is on."""
#         return bool(self._state)

#     @property
#     def device_class(self):
#         """Return the class of this sensor, from DEVICE_CLASSES."""
#         return None

#     def update(self):
#         """Update state of sensor."""
#         try:
#             self._state = self.api.update(
#                 self.sensor_type, self.api_endpoint, self.api_group,
#                 self.api_tool)
#         except requests.exceptions.ConnectionError:
#             # Error calling the api, already logged in api.update()
#             return
