import voluptuous as vol
import aiohttp

from homeassistant import config_entries

DOMAIN = "keba_p40"


class Flow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            if await self._test(user_input):
                return self.async_create_entry(
                    title=user_input["host"],
                    data=user_input,
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Required("username"): str,
                vol.Required("password"): str,
            }),
            errors=errors,
        )

    async def _test(self, data):
        try:
            timeout = aiohttp.ClientTimeout(total=10)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"https://{data['host']}:8443/v2/jwt/login",
                    json={
                        "username": data["username"],
                        "password": data["password"],
                    },
                    ssl=False,
                ) as resp:
                    return resp.status == 200

        except Exception:
            return False
