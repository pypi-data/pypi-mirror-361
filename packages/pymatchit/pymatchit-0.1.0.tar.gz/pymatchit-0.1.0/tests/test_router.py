from pymatchit import PyRouter

import pytest

def test_insert_and_at():
    router = PyRouter()
    router.insert("/hello", "world")
    result = router.at("/hello")
    assert result
    handler, params = result
    assert handler == "world"
    assert params == {}

def test_insert_with_params():
    router = PyRouter()
    router.insert("/user/{id}", "user_handler")
    result = router.at("/user/42")
    assert result
    handler, params = result
    assert handler == "user_handler"
    assert params == {"id": "42"}

def test_insert_with_wildcard():
    router = PyRouter()
    router.insert("/static/{*path}", "static_handler")
    result = router.at("/static/css/style.css")
    assert result
    handler, params = result
    assert handler == "static_handler"
    assert params == {"path": "css/style.css"}

def test_remove_route():
    router = PyRouter()
    router.insert("/to-remove", "handler")
    assert router.remove("/to-remove") is True
    assert router.at("/to-remove") is None
    assert router.remove("/to-remove") is False

def test_clear_routes():
    router = PyRouter()
    router.insert("/a", "A")
    router.insert("/b", "B")
    router.clear()
    assert router.at("/a") is None
    assert router.at("/b") is None

def test_conflicting_insert_raises():
    router = PyRouter()
    router.insert("/conflict", "A")
    with pytest.raises(ValueError):
        router.insert("/conflict", "B")

def test_insert_function_handler():
    router = PyRouter()
    def handler_fn(x):
        return x + 1
    router.insert("/inc", handler_fn)
    result = router.at("/inc")
    assert result
    handler, params = result
    # The handler returned should be the same function object
    assert callable(handler)
    assert handler(10) == 11
    assert params == {}

def test_route_not_found():
    router = PyRouter()
    result = router.at("/notfound")
    assert result is None
