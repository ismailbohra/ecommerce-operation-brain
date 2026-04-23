# tests/conftest.py
import asyncio

import pytest

from db import seed_database
from graph import create_workflow
from vectorstore import seed_vectors

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
    from langgraph.checkpoint.memory import MemorySaver

    return create_workflow(MemorySaver())


def pytest_sessionfinish(session, exitstatus):
    print("\nRunning teardown with pytest sessionfinish...")
