import logging
import time
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

DOMAIN = "keba_p40"
PLATFORMS = ["sensor", "binary_sensor", "select", "number"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = KebaCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class KebaCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        self.host = entry.data["host"]
        self.username = entry.data["username"]
        self.password = entry.data["password"]

        self.session = async_get_clientsession(hass)

        self.token = None
        self.expiry = 0

        super().__init__(
            hass,
            _LOGGER,
            name="keba_p40",
            update_interval=timedelta(seconds=30),
        )

    async def _get_token(self):
        url = f"https://{self.host}:8443/v2/jwt/login"

        try:
            async with self.session.post(
                url,
                json={
                    "username": self.username,
                    "password": self.password,
                },
                ssl=False,
            ) as resp:

                if resp.status != 200:
                    raise UpdateFailed(
                        f"Login fehlgeschlagen: {resp.status}"
                    )

                data = await resp.json()

        except Exception as err:
            raise UpdateFailed(f"Token Fehler: {err}")

        self.token = data.get("accessToken")
        self.expiry = time.time() + data.get("expiresIn", 900)

        if not self.token:
            raise UpdateFailed(f"Kein Token erhalten: {data}")

    async def _async_update_data(self):

        if not self.token or time.time() > self.expiry:
            await self._get_token()

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            async with self.session.get(
                f"https://{self.host}:8443/v2/wallboxes",
                headers=headers,
                ssl=False,
            ) as resp:

                if resp.status == 401:

                    _LOGGER.debug(
                        "Token abgelaufen, erneuere Token"
                    )

                    await self._get_token()

                    headers["Authorization"] = (
                        f"Bearer {self.token}"
                    )

                    async with self.session.get(
                        f"https://{self.host}:8443/v2/wallboxes",
                        headers=headers,
                        ssl=False,
                    ) as resp2:

                        data = await resp2.json()

                else:
                    data = await resp.json()

        except Exception as err:
            raise UpdateFailed(f"Update Fehler: {err}")

        try:
            async with self.session.get(
                f"https://{self.host}:8443/v2/configs/lmgmt",
                headers=headers,
                ssl=False,
            ) as cfg_resp:

                configs_data = await cfg_resp.json()

        except Exception as err:
            raise UpdateFailed(f"Config Fehler: {err}")

        return {
            "wallboxes": data.get("wallboxes") or [],
            "configs": configs_data.get("configs") or [],
        }


    async def set_phases(self, phases: int):
        """Set charging phases via phase-toggle endpoint."""

        if not self.token or time.time() > self.expiry:
            await self._get_token()

        wallboxes = self.data.get("wallboxes") or []

        if not wallboxes:
            raise UpdateFailed("Keine Wallbox gefunden")

        wallbox = wallboxes[0]
        serial = wallbox.get("serialNumber")

        if phases not in [1, 3]:
            raise ValueError("Nur 1 oder 3 Phasen erlaubt")

        # Der Parameter wird als Query-String an die URL angehängt
        url = f"https://{self.host}:8443/v2/wallboxes/{serial}/phase-toggle?numberOfPhases={phases}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

        # Wechsel von PUT auf POST und Entfernen des json-Parameters
        async with self.session.post(
            url,
            headers=headers,
            ssl=False,
        ) as resp:

            if resp.status not in [200, 204]:
                text = await resp.text()
                raise UpdateFailed(
                    f"Phasenumschaltung fehlgeschlagen: {resp.status} {text}"
                )

        await self.async_request_refresh()

        
    async def set_max_current(self, current: int):
        """Set max available current."""

        if not self.token or time.time() > self.expiry:
            await self._get_token()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        payload = {
            "configs": [
                {
                    "key": "max_available_current",
                    "value": str(current),
                }
            ]
        }

        async with self.session.put(
            f"https://{self.host}:8443/v2/configs/lmgmt",
            headers=headers,
            json=payload,
            ssl=False,
        ) as resp:

            if resp.status not in [200, 204]:

                text = await resp.text()

                raise UpdateFailed(
                    f"Stromlimit setzen fehlgeschlagen: "
                    f"{resp.status} {text}"
                )

        await self.async_request_refresh()
