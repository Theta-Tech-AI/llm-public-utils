from app.settings import use_cache


def test_default_is_off(monkeypatch):
    monkeypatch.delenv("USE_CACHE", raising=False)
    assert use_cache() is False
