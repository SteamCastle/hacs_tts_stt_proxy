"""Config flow for tts_stt_proxy."""
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from typing import List

from .const import DOMAIN


class ProxyTTSSTTOptionFlow(config_entries.OptionsFlow):
    """Handle options for tts_stt_proxy."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_options(user_input)

    async def async_step_options(self, user_input=None):
        """Configure options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_data = self.config_entry.data

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Optional("health_check_time", default=current_data.get("health_check_time", "02:00")): str,
                vol.Optional("failure_threshold", default=current_data.get("failure_threshold", 3)): cv.positive_int,
                vol.Optional("success_threshold", default=current_data.get("success_threshold", 1)): cv.positive_int,
                vol.Optional("log_level", default=current_data.get("log_level", "info")): vol.In(["debug", "info", "warning", "error"]),
                vol.Optional("call_timeout", default=current_data.get("call_timeout", 30)): cv.positive_int,
            }),
        )


class ProxyTTSSTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self):
        self.tts_services: List[str] = []
        self.stt_services: List[str] = []
        self.health_check_time = "02:00"
        self.failure_threshold = 3
        self.success_threshold = 1
        self.log_level = "info"
        self.call_timeout = 30

    async def async_step_user(self, user_input=None):
        """First step — select TTS services."""
        if user_input is not None:
            self.tts_services = user_input.get("tts_services", [])
            return await self.async_step_user_stt()

        all_states = self.hass.states.async_all()
        tts_entities = [
            state.entity_id for state in all_states
            if state.entity_id.startswith("tts.")
        ]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("tts_services", default=[]): cv.multi_select(
                    {e: e for e in tts_entities}
                )
            }),
        )

    async def async_step_user_stt(self, user_input=None):
        """Second step — select STT services."""
        if user_input is not None:
            self.stt_services = user_input.get("stt_services", [])
            return await self.async_step_priorities()

        all_states = self.hass.states.async_all()
        stt_entities = [
            state.entity_id for state in all_states
            if state.entity_id.startswith("stt.")
        ]

        return self.async_show_form(
            step_id="user_stt",
            data_schema=vol.Schema({
                vol.Optional("stt_services", default=[]): cv.multi_select(
                    {e: e for e in stt_entities}
                )
            }),
        )

    async def async_step_priorities(self, user_input=None):
        """Third step — confirm priorities."""
        if user_input is not None:
            return await self.async_step_options()

        return self.async_show_form(
            step_id="priorities",
            data_schema=vol.Schema({}),
            description_placeholders={
                "tts_services": ", ".join(self.tts_services) if self.tts_services else "(none)",
                "stt_services": ", ".join(self.stt_services) if self.stt_services else "(none)",
            },
        )

    async def async_step_options(self, user_input=None):
        """Fourth step — configure options."""
        if user_input is not None:
            self.health_check_time = user_input.get("health_check_time", "02:00")
            self.failure_threshold = user_input.get("failure_threshold", 3)
            self.success_threshold = user_input.get("success_threshold", 1)
            self.log_level = user_input.get("log_level", "info")
            self.call_timeout = user_input.get("call_timeout", 30)
            return self.async_create_entry(
                title="Proxy TTS+STT",
                data={
                    "tts_services": [
                        {"entity_id": eid, "priority": i+1, "enabled": True, "fail_count": 0}
                        for i, eid in enumerate(self.tts_services)
                    ],
                    "stt_services": [
                        {"entity_id": eid, "priority": i+1, "enabled": True, "fail_count": 0}
                        for i, eid in enumerate(self.stt_services)
                    ],
                    "health_check_time": self.health_check_time,
                    "failure_threshold": self.failure_threshold,
                    "success_threshold": self.success_threshold,
                    "log_level": self.log_level,
                    "call_timeout": self.call_timeout,
                },
            )

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Optional("health_check_time", default="02:00"): str,
                vol.Optional("failure_threshold", default=3): cv.positive_int,
                vol.Optional("success_threshold", default=1): cv.positive_int,
                vol.Optional("log_level", default="info"): vol.In(["debug", "info", "warning", "error"]),
                vol.Optional("call_timeout", default=30): cv.positive_int,
            }),
        )


class ProxyTTSSTTOptionFlow(config_entries.OptionsFlow):
    """Handle options for tts_stt_proxy."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_options(user_input)

    async def async_step_options(self, user_input=None):
        """Configure options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_data = self.config_entry.data

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Optional("health_check_time", default=current_data.get("health_check_time", "02:00")): str,
                vol.Optional("failure_threshold", default=current_data.get("failure_threshold", 3)): cv.positive_int,
                vol.Optional("success_threshold", default=current_data.get("success_threshold", 1)): cv.positive_int,
                vol.Optional("log_level", default=current_data.get("log_level", "info")): vol.In(["debug", "info", "warning", "error"]),
                vol.Optional("call_timeout", default=current_data.get("call_timeout", 30)): cv.positive_int,
            }),
        )
