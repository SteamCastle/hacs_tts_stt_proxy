"""Tests for config flow."""
import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_options_step_creates_entry_with_priorities():
    """Options step should create entry with priority-ordered services."""
    from custom_components.tts_stt_proxy.config_flow import ProxyTTSSTTConfigFlow

    flow = ProxyTTSSTTConfigFlow()
    # Services are now dicts with entity_id and priority set by async_step_priorities
    flow.tts_services = [
        {"entity_id": "tts.google_tts", "priority": 1, "enabled": True, "fail_count": 0},
        {"entity_id": "tts.edge_tts", "priority": 2, "enabled": True, "fail_count": 0},
    ]
    flow.stt_services = [
        {"entity_id": "stt.whisper_stt", "priority": 1, "enabled": True, "fail_count": 0},
    ]
    flow.health_check_time = "03:00"
    flow.failure_threshold = 5
    flow.success_threshold = 2
    flow.log_level = "debug"
    flow.call_timeout = 60

    result = await flow.async_step_options({
        "health_check_time": "03:00",
        "failure_threshold": 5,
        "success_threshold": 2,
        "log_level": "debug",
        "call_timeout": 60,
    })

    assert result["type"] == "create_entry"
    data = result["data"]
    assert len(data["tts_services"]) == 2
    assert data["tts_services"][0]["entity_id"] == "tts.google_tts"
    assert data["tts_services"][0]["priority"] == 1
    assert data["health_check_time"] == "03:00"
    assert data["failure_threshold"] == 5


@pytest.mark.asyncio
async def test_user_step_returns_tts_entities():
    """User step should return a form with TTS entities."""
    from custom_components.tts_stt_proxy.config_flow import ProxyTTSSTTConfigFlow

    flow = ProxyTTSSTTConfigFlow()
    flow.hass = MagicMock()
    flow.hass.states.async_all = MagicMock(return_value=[
        MagicMock(entity_id="tts.edge_tts"),
        MagicMock(entity_id="tts.google_tts"),
        MagicMock(entity_id="stt.whisper_stt"),
    ])

    result = await flow.async_step_user()

    assert result["type"] == "form"
    assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_user_stt_step_returns_stt_entities():
    """User STT step should return a form with STT entities."""
    from custom_components.tts_stt_proxy.config_flow import ProxyTTSSTTConfigFlow

    flow = ProxyTTSSTTConfigFlow()
    flow.hass = MagicMock()
    flow.hass.states.async_all = MagicMock(return_value=[
        MagicMock(entity_id="stt.whisper_stt"),
        MagicMock(entity_id="tts.edge_tts"),
    ])

    result = await flow.async_step_user_stt()

    assert result["type"] == "form"
    assert result["step_id"] == "user_stt"
