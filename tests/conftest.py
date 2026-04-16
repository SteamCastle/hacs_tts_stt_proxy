import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock haffmpeg module before any homeassistant imports
haffmpeg_core = types.ModuleType('haffmpeg.core')
haffmpeg_core.HAFFmpeg = types.SimpleNamespace()

haffmpeg_tools = types.ModuleType('haffmpeg.tools')
haffmpeg_tools.IMAGE_JPEG = None
haffmpeg_tools.FFVersion = None
haffmpeg_tools.ImageFrame = None

haffmpeg = types.ModuleType('haffmpeg')
haffmpeg.core = haffmpeg_core
haffmpeg.tools = haffmpeg_tools

sys.modules['haffmpeg'] = haffmpeg
sys.modules['haffmpeg.core'] = haffmpeg_core
sys.modules['haffmpeg.tools'] = haffmpeg_tools


@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.services = MagicMock()
    hass.states = MagicMock()
    return hass


@pytest.fixture
def mock_store_data():
    return {
        "tts_services": [
            {"entity_id": "tts.edge_tts", "priority": 1, "enabled": True, "fail_count": 0}
        ],
        "stt_services": [
            {"entity_id": "stt.whisper_stt", "priority": 1, "enabled": True, "fail_count": 0}
        ],
        "health_check_time": "02:00",
        "failure_threshold": 3,
        "success_threshold": 1,
        "log_level": "info",
        "call_timeout": 30,
    }
