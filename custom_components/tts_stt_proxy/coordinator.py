"""Coordinator for Proxy TTS+STT."""
import asyncio
import logging
from datetime import timedelta
from typing import List, Optional, Dict

from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .tts_entity import TTSException
from .stt_entity import STTException

DOMAIN = "tts_stt_proxy"
_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = "tts_stt_proxy"
STORAGE_VERSION = 1


class ProxyTTSSTTCoordinator:
    failure_threshold: int = 3
    success_threshold: int = 1
    call_timeout: int = 30
    health_check_time: str = "02:00"
    log_level: str = "info"
    tts_services: List[Dict] = []
    stt_services: List[Dict] = []

    def __init__(self, hass):
        self.hass = hass
        self._store: Optional[Store] = None

    def _get_next_service(self, services: List[Dict]) -> Optional[str]:
        sorted_services = sorted(
            [s for s in services if s.get("enabled", False)],
            key=lambda s: s.get("priority", 99)
        )
        if not sorted_services:
            return None
        return sorted_services[0]["entity_id"]

    def get_next_tts_service(self) -> Optional[str]:
        return self._get_next_service(self.tts_services)

    def get_next_stt_service(self) -> Optional[str]:
        return self._get_next_service(self.stt_services)

    def record_failure(self, service_id: str, service_type: str):
        services = self.tts_services if service_type == "tts" else self.stt_services
        for svc in services:
            if svc["entity_id"] == service_id:
                svc["fail_count"] = svc.get("fail_count", 0) + 1
                if svc["fail_count"] >= self.failure_threshold:
                    svc["enabled"] = False
                    _LOGGER.warning(
                        "Service %s exceeded failure threshold (%d >= %d), disabled",
                        service_id, svc["fail_count"], self.failure_threshold
                    )
                return
        _LOGGER.debug("Service %s not found in %s services", service_id, service_type)

    def record_success(self, service_id: str, service_type: str):
        services = self.tts_services if service_type == "tts" else self.stt_services
        for svc in services:
            if svc["entity_id"] == service_id:
                svc["fail_count"] = 0
                if not svc.get("enabled", False):
                    svc["enabled"] = True
                    _LOGGER.warning("Service %s recovered, re-enabled", service_id)
                return
        _LOGGER.debug("Service %s not found in %s services", service_id, service_type)

    def get_tts_services(self) -> List[Dict]:
        return list(self.tts_services)

    def get_stt_services(self) -> List[Dict]:
        return list(self.stt_services)

    def update_config(self, config: Dict):
        if "tts_services" in config:
            self.tts_services = config["tts_services"]
        if "stt_services" in config:
            self.stt_services = config["stt_services"]
        if "health_check_time" in config:
            self.health_check_time = config["health_check_time"]
        if "failure_threshold" in config:
            self.failure_threshold = config["failure_threshold"]
        if "success_threshold" in config:
            self.success_threshold = config["success_threshold"]
        if "log_level" in config:
            self.log_level = config["log_level"]
        if "call_timeout" in config:
            self.call_timeout = config["call_timeout"]

    async def async_load(self):
        """Load persisted state from Store."""
        store = Store(self.hass, STORAGE_VERSION, STORAGE_KEY)
        data = await store.async_load()
        if data:
            self.tts_services = data.get("tts_services", [])
            self.stt_services = data.get("stt_services", [])
            self.health_check_time = data.get("health_check_time", "02:00")
            self.failure_threshold = data.get("failure_threshold", 3)
            self.success_threshold = data.get("success_threshold", 1)
            self.log_level = data.get("log_level", "info")
            self.call_timeout = data.get("call_timeout", 30)
        self._store = store

    async def async_save(self):
        """Persist current state to Store."""
        data = {
            "tts_services": self.tts_services,
            "stt_services": self.stt_services,
            "health_check_time": self.health_check_time,
            "failure_threshold": self.failure_threshold,
            "success_threshold": self.success_threshold,
            "log_level": getattr(self, "log_level", "info"),
            "call_timeout": self.call_timeout,
        }
        await self._store.async_save(data)

    async def call_tts_service(self, entity_id: str, message: str, language: str, options: Dict):
        """Call a TTS service and return audio data."""
        try:
            return await asyncio.wait_for(
                self.hass.services.async_call(
                    "tts",
                    "speak",
                    {"entity_id": entity_id, "message": message, "language": language, "options": options},
                    blocking=True,
                ),
                timeout=self.call_timeout,
            )
        except asyncio.TimeoutError:
            raise TTSException(f"TTS call to {entity_id} timed out after {self.call_timeout}s")

    async def call_stt_service(self, entity_id: str, audio_stream):
        """Call an STT service and return transcribed text."""
        try:
            return await asyncio.wait_for(
                self.hass.services.async_call(
                    "stt",
                    "async_process",
                    {"entity_id": entity_id, "audio_stream": audio_stream},
                    blocking=True,
                ),
                timeout=self.call_timeout,
            )
        except asyncio.TimeoutError:
            raise STTException(f"STT call to {entity_id} timed out after {self.call_timeout}s")

    def schedule_periodic_health_check(self):
        """Schedule daily health check at configured time."""
        async def daily_health_check():
            """Run health check once per day."""
            while True:
                now = dt_util.now()
                try:
                    hour, minute = map(int, self.health_check_time.split(":"))
                except (ValueError, AttributeError):
                    hour, minute = 2, 0
                target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if target <= now:
                    target = target + timedelta(days=1)
                wait_seconds = (target - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                await self.async_health_check()

        self.hass.async_create_task(daily_health_check())

    async def async_health_check(self):
        """Run health check on all TTS and STT services (3 attempts each)."""
        _LOGGER.info("Starting health check for all services")
        await self._health_check_services(self.tts_services, "tts")
        await self._health_check_services(self.stt_services, "stt")
        await self.async_save()
        _LOGGER.info("Health check complete")

    async def _health_check_services(self, services, service_type: str):
        """Check each service, retrying up to 3 times total."""
        for svc in services:
            for attempt in range(3):
                try:
                    if service_type == "tts":
                        await self.call_tts_service(svc["entity_id"], "", "en", {})
                    else:
                        await self.call_stt_service(svc["entity_id"], None)
                    self.record_success(svc["entity_id"], service_type)
                    break
                except Exception as exc:
                    _LOGGER.debug("Health check attempt %d/%d for %s failed: %s",
                                  attempt + 1, 3, svc["entity_id"], exc)
                    if attempt == 2:
                        self.record_failure(svc["entity_id"], service_type)
