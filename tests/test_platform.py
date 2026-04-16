"""Tests for TTS/STT platform registration."""
import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_tts_platform_registers_entity():
    from custom_components.tts_stt_proxy.tts import async_setup_entry
    from custom_components.tts_stt_proxy.tts_entity import ProxyTTSEntity

    mock_hass = MagicMock()
    mock_coord = MagicMock()
    mock_hass.data = {"tts_stt_proxy": {"coordinator": mock_coord}}
    mock_entry = MagicMock()

    added_entities = []

    def capture(entities, **kwargs):
        added_entities.extend(entities)

    await async_setup_entry(mock_hass, mock_entry, capture)

    assert len(added_entities) == 1
    entity = added_entities[0]
    assert isinstance(entity, ProxyTTSEntity)
    assert entity.coordinator is mock_coord


@pytest.mark.asyncio
async def test_stt_platform_registers_entity():
    from custom_components.tts_stt_proxy.stt import async_setup_entry
    from custom_components.tts_stt_proxy.stt_entity import ProxySTTEntity

    mock_hass = MagicMock()
    mock_coord = MagicMock()
    mock_hass.data = {"tts_stt_proxy": {"coordinator": mock_coord}}
    mock_entry = MagicMock()

    added_entities = []

    def capture(entities, **kwargs):
        added_entities.extend(entities)

    await async_setup_entry(mock_hass, mock_entry, capture)

    assert len(added_entities) == 1
    entity = added_entities[0]
    assert isinstance(entity, ProxySTTEntity)
    assert entity.coordinator is mock_coord
