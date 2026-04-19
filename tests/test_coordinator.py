"""Tests for ProxyTTSSTTCoordinator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import sys


def test_get_next_tts_service_returns_first_enabled():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.tts_services = [
        {"entity_id": "tts.edge_tts", "priority": 1, "enabled": True, "fail_count": 0},
        {"entity_id": "tts.google_tts", "priority": 2, "enabled": True, "fail_count": 0},
    ]

    result = coord.get_next_tts_service()
    assert result == "tts.edge_tts"


def test_get_next_tts_service_skips_disabled():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.tts_services = [
        {"entity_id": "tts.edge_tts", "priority": 1, "enabled": False, "fail_count": 3},
        {"entity_id": "tts.google_tts", "priority": 2, "enabled": True, "fail_count": 0},
    ]

    result = coord.get_next_tts_service()
    assert result == "tts.google_tts"


def test_get_next_tts_service_returns_none_when_all_disabled():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.tts_services = [
        {"entity_id": "tts.edge_tts", "priority": 1, "enabled": False, "fail_count": 5},
    ]

    result = coord.get_next_tts_service()
    assert result is None


def test_record_failure_increments_count():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    store.async_save = AsyncMock()
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.tts_services = [
        {"entity_id": "tts.edge_tts", "priority": 1, "enabled": True, "fail_count": 0},
    ]
    coord.record_failure("tts.edge_tts", "tts")

    assert coord.tts_services[0]["fail_count"] == 1


def test_record_failure_disables_at_threshold():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    store.async_save = AsyncMock()
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.failure_threshold = 3
    coord.tts_services = [
        {"entity_id": "tts.edge_tts", "priority": 1, "enabled": True, "fail_count": 2},
    ]
    coord.record_failure("tts.edge_tts", "tts")

    assert coord.tts_services[0]["enabled"] is False
    assert coord.tts_services[0]["fail_count"] == 3


def test_record_success_resets_count():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    store.async_save = AsyncMock()
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.tts_services = [
        {"entity_id": "tts.edge_tts", "priority": 1, "enabled": True, "fail_count": 2},
    ]
    coord.record_success("tts.edge_tts", "tts")

    assert coord.tts_services[0]["fail_count"] == 0


def test_record_success_reenables_disabled_service():
    """record_success re-enables a previously-disabled service (recovery path)."""
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    store.async_save = AsyncMock()
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.tts_services = [
        {"entity_id": "tts.edge_tts", "priority": 1, "enabled": False, "fail_count": 3},
    ]

    coord.record_success("tts.edge_tts", "tts")

    assert coord.tts_services[0]["enabled"] is True
    assert coord.tts_services[0]["fail_count"] == 0


def test_get_next_stt_service_returns_first_enabled():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.stt_services = [
        {"entity_id": "stt.whisper_stt", "priority": 1, "enabled": True, "fail_count": 0},
        {"entity_id": "stt.google_stt", "priority": 2, "enabled": False, "fail_count": 3},
    ]

    result = coord.get_next_stt_service()
    assert result == "stt.whisper_stt"


def test_store_persists_and_loads_data(mock_store_data):
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator
    import asyncio
    from homeassistant.helpers.storage import Store

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()

    async def mock_async_load():
        return mock_store_data

    mock_store = MagicMock(spec=Store)
    mock_store.async_load = mock_async_load

    with patch("custom_components.tts_stt_proxy.coordinator.Store") as MockStore:
        MockStore.return_value = mock_store

        coord = ProxyTTSSTTCoordinator(hass)
        asyncio.run(coord.async_load())

        assert len(coord.tts_services) == 1
        assert coord.tts_services[0]["entity_id"] == "tts.edge_tts"
        assert coord.health_check_time == "02:00"
        assert coord.failure_threshold == 3


def test_async_save_persists_data(mock_store_data):
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator
    import asyncio
    from homeassistant.helpers.storage import Store

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()

    mock_store = MagicMock(spec=Store)
    mock_store.async_save = AsyncMock()
    mock_store.async_load = AsyncMock(return_value=None)

    with patch("custom_components.tts_stt_proxy.coordinator.Store") as MockStore:
        MockStore.return_value = mock_store

        coord = ProxyTTSSTTCoordinator(hass)
        coord.tts_services = [
            {"entity_id": "tts.edge_tts", "priority": 1, "enabled": True, "fail_count": 2},
        ]

        asyncio.run(coord.async_load())  # This sets up _store
        asyncio.run(coord.async_save())

        mock_store.async_save.assert_called_once()
        saved_data = mock_store.async_save.call_args[0][0]
        assert saved_data["tts_services"][0]["fail_count"] == 2


def test_get_tts_services_returns_all():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.tts_services = [
        {"entity_id": "tts.a", "priority": 1, "enabled": True, "fail_count": 0},
        {"entity_id": "tts.b", "priority": 2, "enabled": False, "fail_count": 5},
    ]

    result = coord.get_tts_services()
    assert len(result) == 2
    assert result[0]["entity_id"] == "tts.a"


def test_update_config_replaces_services():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    store.async_save = AsyncMock()
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.tts_services = [
        {"entity_id": "tts.old", "priority": 1, "enabled": True, "fail_count": 0},
    ]

    new_config = {
        "tts_services": [
            {"entity_id": "tts.new", "priority": 1, "enabled": True, "fail_count": 0},
        ],
        "stt_services": [],
        "health_check_time": "03:00",
        "failure_threshold": 5,
        "success_threshold": 2,
        "log_level": "debug",
        "call_timeout": 60,
    }
    coord.update_config(new_config)

    assert coord.tts_services[0]["entity_id"] == "tts.new"
    assert coord.health_check_time == "03:00"
    assert coord.failure_threshold == 5


def test_default_data():
    """Store returns no data — defaults apply."""
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    assert coord.failure_threshold == 3
    assert coord.success_threshold == 1
    assert coord.call_timeout == 30
    assert coord.health_check_time == "02:00"
    assert coord.tts_services == []
    assert coord.stt_services == []


@pytest.mark.asyncio
async def test_call_tts_service_uses_hass_services():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    hass.services.async_call = AsyncMock(return_value=MagicMock())
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.call_timeout = 30

    await coord.call_tts_service("tts.edge_tts", "hello world", "en", {})

    hass.services.async_call.assert_called_once()
    call_args = hass.services.async_call.call_args
    assert call_args[0][0] == "tts"


@pytest.mark.asyncio
async def test_call_stt_service_uses_hass_services():
    from custom_components.tts_stt_proxy.coordinator import ProxyTTSSTTCoordinator

    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    hass.services.async_call = AsyncMock(return_value="transcribed text")
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    hass.helpers.storage.Store = MagicMock(return_value=store)

    coord = ProxyTTSSTTCoordinator(hass)
    coord.call_timeout = 30

    mock_stream = MagicMock()
    await coord.call_stt_service("stt.whisper_stt", mock_stream)

    hass.services.async_call.assert_called_once()
    call_args = hass.services.async_call.call_args
    assert call_args[0][0] == "stt"
    assert call_args[0][2]["entity_id"] == "stt.whisper_stt"


@pytest.mark.asyncio
async def test_async_setup_entry_creates_coordinator_and_forwards():
    from custom_components.tts_stt_proxy import async_setup_entry, DOMAIN

    mock_hass = MagicMock()
    mock_hass.data = {}
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"
    mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)

    with patch("custom_components.tts_stt_proxy.ProxyTTSSTTCoordinator") as MockCoord:
        with patch("custom_components.tts_stt_proxy.async_register_services", AsyncMock()):
            mock_coord = MagicMock()
            mock_coord.async_load = AsyncMock()
            mock_coord.schedule_periodic_health_check = MagicMock()
            MockCoord.return_value = mock_coord

            result = await async_setup_entry(mock_hass, mock_entry)

            assert result is True
            assert "coordinator" in mock_hass.data[DOMAIN]
            mock_coord.schedule_periodic_health_check.assert_called_once()
            mock_hass.config_entries.async_forward_entry_setups.assert_called_with(
                mock_entry, ["tts", "stt"]
            )


@pytest.mark.asyncio
async def test_async_unload_entry_unloads():
    from custom_components.tts_stt_proxy import async_unload_entry, DOMAIN

    mock_hass = MagicMock()
    mock_entry = MagicMock()
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    mock_hass.data = {
        DOMAIN: {"coordinator": MagicMock()}
    }

    result = await async_unload_entry(mock_hass, mock_entry)

    assert result is True
    assert mock_hass.config_entries.async_unload_platforms.called


@pytest.mark.asyncio
async def test_async_setup_entry_loads_config_from_entry_data():
    """async_setup_entry should load TTS/STT services from entry.data."""
    from custom_components.tts_stt_proxy import async_setup_entry, DOMAIN
    import asyncio

    mock_hass = MagicMock()
    mock_hass.data = {}
    mock_hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)

    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"
    mock_entry.data = {
        "tts_services": [
            {"entity_id": "tts.edge_tts", "priority": 1, "enabled": True, "fail_count": 0}
        ],
        "stt_services": [
            {"entity_id": "stt.whisper", "priority": 1, "enabled": True, "fail_count": 0}
        ],
        "health_check_time": "03:00",
        "failure_threshold": 5,
        "success_threshold": 2,
        "log_level": "debug",
        "call_timeout": 60,
    }

    # Mock the Store to avoid actual file system access
    mock_store = MagicMock()
    mock_store.async_load = AsyncMock(return_value=None)
    mock_store.async_save = AsyncMock()

    with patch("custom_components.tts_stt_proxy.async_register_services", AsyncMock()):
        with patch("custom_components.tts_stt_proxy.coordinator.Store", return_value=mock_store):
            result = await async_setup_entry(mock_hass, mock_entry)

            assert result is True
            coord = mock_hass.data[DOMAIN]["coordinator"]
            assert len(coord.tts_services) == 1
            assert coord.tts_services[0]["entity_id"] == "tts.edge_tts"
            assert len(coord.stt_services) == 1
            assert coord.stt_services[0]["entity_id"] == "stt.whisper"
            assert coord.health_check_time == "03:00"
            assert coord.failure_threshold == 5
            assert coord.success_threshold == 2
            assert coord.log_level == "debug"
            assert coord.call_timeout == 60
