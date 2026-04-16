"""Proxy TTS Entity."""
import logging
from typing import Any, Dict, List

from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)


class TTSException(HomeAssistantError):
    """Exception raised when TTS processing fails."""

    pass


class ProxyTTSEntity(TextToSpeechEntity):
    def __init__(self, hass, coordinator):
        self.hass = hass
        self.coordinator = coordinator

    @property
    def name(self) -> str:
        return "Proxy TTS"

    @property
    def entity_id(self) -> str:
        return "tts.proxy_tts"

    @property
    def unique_id(self) -> str:
        return "proxy_tts"

    @property
    def default_language(self) -> str:
        return "en"

    @property
    def supported_languages(self) -> List[str]:
        return ["en", "es", "fr", "de", "zh", "ja", "ko"]

    async def async_get_tts_audio(self, message: str, language: str, options: Dict[str, Any]):
        """Request TTS audio from the proxy service."""
        entity_id = self.coordinator.get_next_tts_service()
        if not entity_id:
            raise TTSException("No healthy TTS services available")

        try:
            audio = await self.coordinator.call_tts_service(entity_id, message, language, options)
            self.coordinator.record_success(entity_id, "tts")
            return audio
        except Exception as exc:
            _LOGGER.debug("TTS service %s failed: %s", entity_id, exc)
            self.coordinator.record_failure(entity_id, "tts")
            raise
