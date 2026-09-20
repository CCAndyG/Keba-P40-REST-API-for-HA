"""Migrationen für bestehende Installationen der Keba P40 Integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import button_unique_ids

MIGRATIONS = (
    button_unique_ids,
)


def async_run_migrations(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Alle Migrationen für einen Config Entry ausführen."""

    for migration in MIGRATIONS:
        migration.migrate(hass, entry)
