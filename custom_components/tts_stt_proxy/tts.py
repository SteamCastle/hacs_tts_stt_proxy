"""TTS platform for tts_stt_proxy."""
from .tts_entity import ProxyTTSEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up TTS platform from config entry."""
    coordinator = hass.data["tts_stt_proxy"]["coordinator"]
    async_add_entities([ProxyTTSEntity(hass, coordinator)], update_before_add=True)
