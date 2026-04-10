# tests/conftest.py
import pytest
import asyncio
from db import seed_database
from vectorstore import seed_vectors
from graph import create_workflow

_initialized = False


def _init_once():
    global _initialized
    if _initialized:
        return
    asyncio.run(seed_database())
    seed_vectors()
    _initialized = True
    print("\n✅ Test environment initialized")


_init_once()


@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    _init_once()
    yield


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def workflow():
    return create_workflow()


def pytest_sessionfinish(session, exitstatus):
    print("\nRunning teardown with pytest sessionfinish...")
