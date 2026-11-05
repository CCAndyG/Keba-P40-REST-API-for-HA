"""Migration der Button-unique_ids auf ein eintragsspezifisches Schema.

Die Buttons hatten bis v1.2.2 eine feste, nicht eintragsspezifische
unique_id. Bei mehreren eingerichteten Wallboxen kollidierten sie dadurch
und Home Assistant verwarf die Buttons der zweiten Wallbox.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

BUTTON_PLATFORM = "button"

LEGACY_BUTTON_UNIQUE_IDS = {
    "keba_p40_start_charging": "start_charging",
    "keba_p40_stop_charging": "stop_charging",
}


def migrate(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Alte, globale Button-unique_ids auf eintragsspezifische umstellen."""

    registry = er.async_get(hass)

    for legacy_id, suffix in LEGACY_BUTTON_UNIQUE_IDS.items():

        entity_id = registry.async_get_entity_id(
            BUTTON_PLATFORM,
            DOMAIN,
            legacy_id,
        )

        if entity_id is None:
            continue

        registry_entry = registry.async_get(entity_id)

        if (
            registry_entry is None
            or registry_entry.config_entry_id != entry.entry_id
        ):
            continue

        new_unique_id = f"{entry.entry_id}_{suffix}"

        if registry.async_get_entity_id(
            BUTTON_PLATFORM,
            DOMAIN,
            new_unique_id,
        ):
            continue

        _LOGGER.debug(
            "Migriere unique_id von %s: %s -> %s",
            entity_id,
            legacy_id,
            new_unique_id,
        )

        registry.async_update_entity(entity_id, new_unique_id=new_unique_id)
