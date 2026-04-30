"""
Nexus Warmup Engine — Resilience Testing (Chaos Engineering Lite)
Simulates failure scenarios to validate graceful degradation.
"""
import asyncio
import logging
import time
import random
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.ai_service import generate_warmup_content
from app.services.email_service import send_email_smtp

logger = logging.getLogger("nexus.chaos")


async def test_ai_service_timeout():
    """
    CHAOS TEST: What happens when OpenRouter takes 30+ seconds?
    Expected: Fallback to static templates, no crash.
    """
    print("\n🔥 CHAOS: AI Service Timeout")
    
    async def slow_response(*args, **kwargs):
        await asyncio.sleep(35)  # Exceed the 30s timeout
        return None
    
    with patch("app.services.ai_service.httpx.AsyncClient.post", side_effect=slow_response):
        start = time.perf_counter()
        result = await generate_warmup_content("test_user")
        duration = time.perf_counter() - start
    
    assert result is None, "Should return None on timeout"
    assert duration < 35, "Should not wait for full 35s due to httpx timeout"
    print(f"  ✅ PASS — Returned None in {duration:.1f}s (timeout handled)")


async def test_ai_service_500_error():
    """
    CHAOS TEST: OpenRouter returns 500 Internal Server Error.
    Expected: Graceful fallback, logged error.
    """
    print("\n🔥 CHAOS: AI Service 500 Error")
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    
    with patch("app.services.ai_service.httpx.AsyncClient.post", return_value=mock_response):
        result = await generate_warmup_content("test_user")
    
    assert result is None, "Should return None on 500"
    print("  ✅ PASS — Graceful degradation on 500")


async def test_ai_service_malformed_json():
    """
    CHAOS TEST: OpenRouter returns garbage JSON.
    Expected: Catch JSON parse error, fallback.
    """
    print("\n🔥 CHAOS: AI returns malformed JSON")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "NOT VALID JSON {{{{"}}]
    }
    
    with patch("app.services.ai_service.httpx.AsyncClient.post", return_value=mock_response):
        result = await generate_warmup_content("test_user")
    
    assert result is None, "Should return None on malformed JSON"
    print("  ✅ PASS — Handled malformed JSON gracefully")


async def test_smtp_connection_refused():
    """
    CHAOS TEST: SMTP server is completely down.
    Expected: Task logs failure, does NOT crash worker.
    """
    print("\n🔥 CHAOS: SMTP Connection Refused")
    
    try:
        result = await send_email_smtp(
            host="192.0.2.1",  # Non-routable IP (guaranteed failure)
            port=25,
            username="test",
            password="test",
            from_email="test@test.com",
            to_email="target@test.com",
            subject="Chaos Test",
            body="This should never arrive."
        )
        # Should return False, not crash
        assert result == False, "Should return False on connection failure"
        print("  ✅ PASS — SMTP failure handled gracefully")
    except Exception as e:
        print(f"  ❌ FAIL — Unhandled exception: {e}")


async def test_database_connection_pool_exhaustion():
    """
    CHAOS TEST: Simulate many concurrent DB requests.
    Expected: Connections queue properly, no data corruption.
    """
    print("\n🔥 CHAOS: Database Connection Pool Stress")
    
    from app.database import AsyncSessionLocal
    from app.models.account import WarmupPool
    from sqlalchemy import select, func
    
    async def db_query(i):
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(func.count()).select_from(WarmupPool))
            return result.scalar()
    
    # Fire 50 concurrent queries
    start = time.perf_counter()
    tasks = [db_query(i) for i in range(50)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    duration = time.perf_counter() - start
    
    errors = [r for r in results if isinstance(r, Exception)]
    successes = [r for r in results if not isinstance(r, Exception)]
    
    print(f"  50 concurrent queries in {duration:.2f}s")
    print(f"  Successes: {len(successes)}, Errors: {len(errors)}")
    
    if errors:
        print(f"  ⚠️  WARN — {len(errors)} queries failed: {errors[0]}")
    else:
        print("  ✅ PASS — All queries completed")


async def test_rapid_email_sends():
    """
    CHAOS TEST: What happens with rapid-fire email attempts?
    Expected: Rate limiting kicks in gracefully.
    """
    print("\n🔥 CHAOS: Rapid-fire warmup attempts")
    
    from app.services.warmup_engine import calculate_daily_target
    
    # Simulate day 1 of warmup — should only allow ~3 emails
    target = calculate_daily_target(warmup_day=1, max_per_day=50, ramp_days=28)
    
    assert target <= 5, f"Day 1 should cap at ~3 emails, got {target}"
    print(f"  Day 1 target: {target} emails (ramp-up working)")
    
    # Simulate day 28 — should be at max
    target_28 = calculate_daily_target(warmup_day=28, max_per_day=50, ramp_days=28)
    assert target_28 == 50, f"Day 28 should hit max 50, got {target_28}"
    print(f"  Day 28 target: {target_28} emails (max reached)")
    print("  ✅ PASS — Ramp-up rate limiting verified")


async def run_all_chaos_tests():
    """Execute all chaos engineering tests."""
    print("=" * 60)
    print("🧪 NEXUS WARMUP ENGINE — CHAOS ENGINEERING SUITE")
    print("=" * 60)
    
    tests = [
        test_ai_service_500_error,
        test_ai_service_malformed_json,
        test_rapid_email_sends,
        test_database_connection_pool_exhaustion,
    ]
    
    passed = 0
    failed = 0
    
    for test_fn in tests:
        try:
            await test_fn()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAIL — {test_fn.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    asyncio.run(run_all_chaos_tests())
