"""Tests for ProxyTTSEntity."""
import pytest
from unittest.mock import AsyncMock, MagicMock


def test_tts_entity_requires_coordinator(mock_hass):
    """ProxyTTSEntity should store a reference to the coordinator."""
    from custom_components.tts_stt_proxy.tts_entity import ProxyTTSEntity

    mock_coordinator = MagicMock()

    entity = ProxyTTSEntity(mock_hass, mock_coordinator)
    assert entity.coordinator is mock_coordinator


@pytest.mark.asyncio
async def test_tts_delegates_to_coordinator(mock_hass):
    from custom_components.tts_stt_proxy.tts_entity import ProxyTTSEntity

    coordinator = MagicMock()
    coordinator.get_next_tts_service = MagicMock(return_value="tts.edge_tts")
    coordinator.call_tts_service = AsyncMock(return_value=b"audio_data")
    coordinator.record_success = MagicMock()

    entity = ProxyTTSEntity(mock_hass, coordinator)

    result = await entity.async_get_tts_audio("hello", "en", {})

    coordinator.get_next_tts_service.assert_called_once()
    coordinator.call_tts_service.assert_called_once_with("tts.edge_tts", "hello", "en", {})
    coordinator.record_success.assert_called_once_with("tts.edge_tts", "tts")
    assert result == b"audio_data"


@pytest.mark.asyncio
async def test_tts_raises_when_no_service_available(mock_hass):
    from custom_components.tts_stt_proxy.tts_entity import ProxyTTSEntity, TTSException

    coordinator = MagicMock()
    coordinator.get_next_tts_service = MagicMock(return_value=None)

    entity = ProxyTTSEntity(mock_hass, coordinator)

    with pytest.raises(TTSException, match="No healthy TTS services"):
        await entity.async_get_tts_audio("hello", "en", {})


@pytest.mark.asyncio
async def test_tts_records_failure_and_re_raises(mock_hass):
    from custom_components.tts_stt_proxy.tts_entity import ProxyTTSEntity

    coordinator = MagicMock()
    coordinator.get_next_tts_service = MagicMock(return_value="tts.edge_tts")
    coordinator.call_tts_service = AsyncMock(side_effect=Exception("Network error"))
    coordinator.record_failure = MagicMock()

    entity = ProxyTTSEntity(mock_hass, coordinator)

    with pytest.raises(Exception, match="Network error"):
        await entity.async_get_tts_audio("hello", "en", {})

    coordinator.record_failure.assert_called_once_with("tts.edge_tts", "tts")
