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
            self.tts_services = [
                {"entity_id": eid, "priority": i+1, "enabled": True, "fail_count": 0}
                for i, eid in enumerate(user_input.get("tts_services", []))
            ]
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
            self.stt_services = [
                {"entity_id": eid, "priority": i+1, "enabled": True, "fail_count": 0}
                for i, eid in enumerate(user_input.get("stt_services", []))
            ]
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
        """Third step — set priorities for TTS services."""
        if user_input is not None:
            # Update TTS priorities from user input
            for service in user_input.get("tts_services", []):
                for svc in self.tts_services:
                    if svc["entity_id"] == service["entity_id"]:
                        svc["priority"] = service["priority"]
                        break
            # Update STT priorities from user input
            for service in user_input.get("stt_services", []):
                for svc in self.stt_services:
                    if svc["entity_id"] == service["entity_id"]:
                        svc["priority"] = service["priority"]
                        break
            return await self.async_step_options()

        # Build schema for TTS priorities
        tts_schema_dict = {}
        for i, entity_id in enumerate(self.tts_services):
            default_priority = i + 1
            tts_schema_dict[vol.Optional(f"tts_{entity_id}", default=default_priority)] = cv.positive_int

        # Build schema for STT priorities
        stt_schema_dict = {}
        for i, entity_id in enumerate(self.stt_services):
            default_priority = i + 1
            stt_schema_dict[vol.Optional(f"stt_{entity_id}", default=default_priority)] = cv.positive_int

        # Combine schemas
        priority_schema = {}
        priority_schema.update(tts_schema_dict)
        priority_schema.update(stt_schema_dict)

        if not priority_schema:
            # No services selected, skip to options
            return await self.async_step_options()

        return self.async_show_form(
            step_id="priorities",
            data_schema=vol.Schema(priority_schema),
            description_placeholders={
                "tts_services": ", ".join([s["entity_id"] for s in self.tts_services]) if self.tts_services else "(none)",
                "stt_services": ", ".join([s["entity_id"] for s in self.stt_services]) if self.stt_services else "(none)",
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
                    "tts_services": self.tts_services,
                    "stt_services": self.stt_services,
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
                vol.Optional("health_check_time", default=self.health_check_time): str,
                vol.Optional("failure_threshold", default=self.failure_threshold): cv.positive_int,
                vol.Optional("success_threshold", default=self.success_threshold): cv.positive_int,
                vol.Optional("log_level", default=self.log_level): vol.In(["debug", "info", "warning", "error"]),
                vol.Optional("call_timeout", default=self.call_timeout): cv.positive_int,
            }),
        )
