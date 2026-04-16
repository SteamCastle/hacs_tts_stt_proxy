"""STT platform for tts_stt_proxy."""
from .stt_entity import ProxySTTEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up STT platform from config entry."""
    coordinator = hass.data["tts_stt_proxy"]["coordinator"]
    async_add_entities([ProxySTTEntity(hass, coordinator)], update_before_add=True)
