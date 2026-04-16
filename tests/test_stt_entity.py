"""Tests for ProxySTTEntity."""
import pytest
from unittest.mock import MagicMock, AsyncMock


def test_stt_entity_requires_coordinator(mock_hass):
    """ProxySTTEntity should store a reference to the coordinator."""
    from custom_components.tts_stt_proxy.stt_entity import ProxySTTEntity

    mock_coordinator = MagicMock()

    entity = ProxySTTEntity(mock_hass, mock_coordinator)
    assert entity.coordinator is mock_coordinator


@pytest.mark.asyncio
async def test_stt_delegates_to_coordinator(mock_hass):
    from custom_components.tts_stt_proxy.stt_entity import ProxySTTEntity

    coordinator = MagicMock()
    coordinator.get_next_stt_service = MagicMock(return_value="stt.whisper_stt")
    coordinator.call_stt_service = AsyncMock(return_value="transcribed text")
    coordinator.record_success = MagicMock()

    entity = ProxySTTEntity(mock_hass, coordinator)

    # Mock audio stream and metadata
    mock_stream = MagicMock()
    mock_metadata = MagicMock()
    result = await entity.async_process_audio_stream(mock_metadata, mock_stream)

    coordinator.get_next_stt_service.assert_called_once()
    coordinator.call_stt_service.assert_called_once_with("stt.whisper_stt", mock_stream)
    coordinator.record_success.assert_called_once_with("stt.whisper_stt", "stt")
    assert result == "transcribed text"


@pytest.mark.asyncio
async def test_stt_raises_when_no_service_available(mock_hass):
    from custom_components.tts_stt_proxy.stt_entity import ProxySTTEntity
    from custom_components.tts_stt_proxy.stt_entity import STTException

    coordinator = MagicMock()
    coordinator.get_next_stt_service = MagicMock(return_value=None)

    entity = ProxySTTEntity(mock_hass, coordinator)
    mock_stream = MagicMock()
    mock_metadata = MagicMock()

    with pytest.raises(STTException, match="No healthy STT services"):
        await entity.async_process_audio_stream(mock_metadata, mock_stream)


@pytest.mark.asyncio
async def test_stt_records_failure_and_re_raises(mock_hass):
    from custom_components.tts_stt_proxy.stt_entity import ProxySTTEntity

    coordinator = MagicMock()
    coordinator.get_next_stt_service = MagicMock(return_value="stt.whisper_stt")
    coordinator.call_stt_service = AsyncMock(side_effect=Exception("STT error"))
    coordinator.record_failure = MagicMock()

    entity = ProxySTTEntity(mock_hass, coordinator)
    mock_stream = MagicMock()
    mock_metadata = MagicMock()

    with pytest.raises(Exception, match="STT error"):
        await entity.async_process_audio_stream(mock_metadata, mock_stream)

    coordinator.record_failure.assert_called_once_with("stt.whisper_stt", "stt")
