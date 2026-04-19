"""Proxy TTS+STT integration."""
import logging
from .coordinator import ProxyTTSSTTCoordinator
from .services import async_register_services
from .config_flow import ProxyTTSSTTOptionFlow

_LOGGER = logging.getLogger(__name__)

DOMAIN = "tts_stt_proxy"


async def async_setup_entry(hass, entry):
    """Set up tts_stt_proxy from a config entry."""
    coordinator = ProxyTTSSTTCoordinator(hass)
    await coordinator.async_load()

    # Load configuration from entry.data (set by config flow)
    if "tts_services" in entry.data:
        coordinator.tts_services = entry.data["tts_services"]
    if "stt_services" in entry.data:
        coordinator.stt_services = entry.data["stt_services"]
    if "health_check_time" in entry.data:
        coordinator.health_check_time = entry.data["health_check_time"]
    if "failure_threshold" in entry.data:
        coordinator.failure_threshold = entry.data["failure_threshold"]
    if "success_threshold" in entry.data:
        coordinator.success_threshold = entry.data["success_threshold"]
    if "log_level" in entry.data:
        coordinator.log_level = entry.data["log_level"]
    if "call_timeout" in entry.data:
        coordinator.call_timeout = entry.data["call_timeout"]

    hass.data.setdefault(DOMAIN, {})["coordinator"] = coordinator

    coordinator.schedule_periodic_health_check()

    await async_register_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, ["tts", "stt"])

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass, entry):
    """Handle options update."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    coordinator.update_config(entry.options)
    await coordinator.async_save()


async def async_unload_entry(hass, entry):
    """Unload tts_stt_proxy config entry."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator and coordinator._health_check_task:
        coordinator._health_check_task.cancel()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["tts", "stt"])
    if unload_ok:
        hass.data[DOMAIN].pop("coordinator", None)
    return unload_ok
