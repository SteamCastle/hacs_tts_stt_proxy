"""Services for tts_stt_proxy."""
import logging
from homeassistant.core import ServiceCall

_LOGGER = logging.getLogger(__name__)


async def async_register_services(hass):
    """Register manual health check service."""

    async def trigger_health_check(service: ServiceCall):
        service_type = service.data.get("service_type")
        entity_id = service.data.get("entity_id")
        coordinator = hass.data["tts_stt_proxy"]["coordinator"]

        if entity_id:
            # Check single entity
            if service_type == "tts":
                services = coordinator.tts_services
            elif service_type == "stt":
                services = coordinator.stt_services
            else:
                services = coordinator.tts_services + coordinator.stt_services

            for svc in services:
                if svc["entity_id"] == entity_id:
                    svc_type = service_type or ("tts" if entity_id.startswith("tts.") else "stt")
                    for attempt in range(3):
                        try:
                            if svc_type == "tts":
                                await coordinator.call_tts_service(entity_id, "", "en", {})
                            else:
                                await coordinator.call_stt_service(entity_id, None)
                            coordinator.record_success(entity_id, svc_type)
                            break
                        except Exception:
                            if attempt == 2:
                                coordinator.record_failure(entity_id, svc_type)
                    break
        else:
            # Check all
            await coordinator.async_health_check()

        await coordinator.async_save()

    hass.services.async_register(
        "tts_stt_proxy", "trigger_health_check", trigger_health_check
    )
