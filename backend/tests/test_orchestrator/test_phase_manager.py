"""Tests for Phase Manager."""
import pytest
import asyncio
from backend.orchestrator.phase_manager import PhaseManager, PhaseStatus


class TestPhaseManager:
    def setup_method(self):
        self.pm = PhaseManager({"test_phase": 5, "fast_phase": 2})

    @pytest.mark.asyncio
    async def test_execute_phase_success(self):
        async def handler(inputs):
            return {"result": "ok"}

        result = await self.pm.execute_phase("test_phase", handler, {})
        assert result.status == PhaseStatus.COMPLETED
        assert result.data["result"] == "ok"
        assert result.duration_s >= 0

    @pytest.mark.asyncio
    async def test_execute_phase_timeout(self):
        async def slow_handler(inputs):
            await asyncio.sleep(10)
            return {}

        result = await self.pm.execute_phase("fast_phase", slow_handler, {}, timeout_override=1)
        assert result.status == PhaseStatus.TIMEOUT

    @pytest.mark.asyncio
    async def test_execute_phase_failure(self):
        async def failing_handler(inputs):
            raise ValueError("test error")

        result = await self.pm.execute_phase("test_phase", failing_handler, {})
        assert result.status == PhaseStatus.FAILED
        assert "test error" in result.error

    @pytest.mark.asyncio
    async def test_sequential_phases(self):
        async def handler1(inputs):
            return {"step": 1}
        async def handler2(inputs):
            return {"step": 2}

        phases = [
            {"id": "p1", "handler": handler1},
            {"id": "p2", "handler": handler2},
        ]
        results = await self.pm.execute_phases_sequential(phases)
        assert len(results) == 2

    def test_get_summary(self):
        self.pm.results["test"] = PhaseResult("test", PhaseStatus.COMPLETED, duration_s=1.5)
        summary = self.pm.get_summary()
        assert "test" in summary["phases"]
        assert summary["total_duration_s"] == 1.5
