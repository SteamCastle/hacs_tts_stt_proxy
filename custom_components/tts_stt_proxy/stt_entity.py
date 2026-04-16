"""Proxy STT Entity."""
import logging

from homeassistant.components.stt import (
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioBitRates,
    AudioSampleRates,
    SpeechToTextEntity,
)
from homeassistant.exceptions import HomeAssistantError


_LOGGER = logging.getLogger(__name__)


class STTException(HomeAssistantError):
    """Exception raised when STT processing fails."""

    pass


class ProxySTTEntity(SpeechToTextEntity):
    """Proxy STT entity that forwards requests to configured services."""

    def __init__(self, hass, coordinator):
        self.hass = hass
        self.coordinator = coordinator

    @property
    def name(self) -> str:
        return "Proxy STT"

    @property
    def entity_id(self) -> str:
        return "stt.proxy_stt"

    @property
    def unique_id(self) -> str:
        return "proxy_stt"

    @property
    def supported_languages(self):
        """Return a list of supported languages."""
        return ["en"]

    @property
    def supported_formats(self):
        """Return a list of supported formats."""
        return [AudioFormats.WAV, AudioFormats.OGG]

    @property
    def supported_codecs(self):
        """Return a list of supported codecs."""
        return [AudioCodecs.PCM, AudioCodecs.OPUS]

    @property
    def supported_bit_rates(self):
        """Return a list of supported bit rates."""
        return [AudioBitRates.BITRATE_8, AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self):
        """Return a list of supported sample rates."""
        return [AudioSampleRates.SAMPLERATE_16000, AudioSampleRates.SAMPLERATE_44100]

    @property
    def supported_channels(self):
        """Return a list of supported channels."""
        return [AudioChannels.CHANNEL_MONO, AudioChannels.CHANNEL_STEREO]

    async def async_process_audio_stream(self, metadata, stream):
        """Process an audio stream via the next healthy STT service."""
        entity_id = self.coordinator.get_next_stt_service()
        if not entity_id:
            raise STTException("No healthy STT services available")

        try:
            result = await self.coordinator.call_stt_service(entity_id, stream)
            self.coordinator.record_success(entity_id, "stt")
            return result
        except Exception as exc:
            _LOGGER.debug("STT service %s failed: %s", entity_id, exc)
            self.coordinator.record_failure(entity_id, "stt")
            raise
