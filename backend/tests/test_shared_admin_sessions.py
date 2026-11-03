import pytest

from app.admin import auth, shared_store, ui
from app.core.config import settings
from tests.conftest import login


@pytest.fixture
def redis(monkeypatch):
    data, expirations = {}, {}
    clock = [1000.0]
    monkeypatch.setattr(settings, "UPSTASH_REDIS_REST_URL", "https://redis.example.test")
    monkeypatch.setattr(settings, "UPSTASH_REDIS_REST_TOKEN", "test-token")
    monkeypatch.setattr(auth.session_store, "_clock", lambda: clock[0])
    def command(*parts):
        op = parts[0]
        key = parts[1] if op != "EVAL" else parts[3]
        if expirations.get(key, float("inf")) <= clock[0]:
            data.pop(key, None)
        if op == "GET":
            return data.get(key)
        if op == "DEL":
            data.pop(key, None)
            return 1
        if op == "SET":
            if "XX" in parts and key not in data:
                return None
            data[key] = parts[2]
            expirations[key] = clock[0] + int(parts[4])
            return "OK"
        if op == "EVAL":
            data[key] = int(data.get(key, 0)) + 1
            expirations[key] = clock[0] + int(parts[4])
            return data[key]
        raise AssertionError(f"Unexpected Redis operation: {op}")
    monkeypatch.setattr(shared_store, "command", command)
    return data, clock


def test_sessions_survive_instance_changes_and_logout_is_shared(redis):
    _, clock = redis
    first = auth.SessionStore(clock=lambda: clock[0])
    second = auth.SessionStore(clock=lambda: clock[0])
    session = first.create()
    first.clear()  # simulate a cold Vercel instance losing all process memory
    restored = second.get(session.sid)
    assert restored is not None and restored.sid == session.sid
    second.destroy(session.sid)
    first.save(session)  # an older in-flight request must not recreate it
    assert first.get(session.sid) is None


def test_shared_sessions_expire_and_login_throttle_is_cross_instance(redis):
    _, clock = redis
    sessions = auth.SessionStore(clock=lambda: clock[0])
    session = sessions.create()
    a, b = auth.LoginThrottle(), auth.LoginThrottle()
    for _ in range(auth.MAX_FAILED_LOGINS):
        a.record_failure("test-client")
    assert b.is_locked("test-client")
    b.reset("test-client")
    assert not a.is_locked("test-client")
    clock[0] += settings.ADMIN_SESSION_IDLE_MINUTES * 60 + 1
    assert sessions.get(session.sid) is None


def test_flash_notifications_are_persisted_for_the_next_instance(redis):
    _, clock = redis
    sessions = auth.SessionStore(clock=lambda: clock[0])
    session = sessions.create()
    ui.flash(session, "Saved for the next request")
    restored = sessions.get(session.sid)
    assert restored.flashes == [["success", "Saved for the next request"]]


def test_admin_login_remains_authenticated_after_process_memory_is_cleared(client, redis):
    assert login(client).status_code == 303
    auth.session_store.clear()
    page = client.get("/admin")
    assert page.status_code == 200
    token = page.text.split('name="csrf_token" value="')[1].split('"')[0]
    assert client.post("/admin/logout", data={"csrf_token": token}).status_code == 303
    assert client.get("/admin").status_code == 303
