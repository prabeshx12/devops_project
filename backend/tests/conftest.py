import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from backend.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def sample_item():
    return {
        "name": "HDMI Cable",
        "category": "Electronics",
        "quantity": 12,
        "low_stock_threshold": 5,
        "location": "Lab A",
        "status": "active",
        "notes": "For projector setup",
    }

