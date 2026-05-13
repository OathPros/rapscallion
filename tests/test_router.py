import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_classification_from_fixture() -> None:
    fixture_path = Path("data/test_utterances.json")
    cases = json.loads(fixture_path.read_text(encoding="utf-8"))

    for case in cases:
        response = client.post("/api/classify", json={"message": case["message"]})
        assert response.status_code == 200
        body = response.json()
        assert body["route"] == case["expected_route"]
        assert "confidence" in body
        assert "next_action" in body


def test_response_schema_fields() -> None:
    response = client.post("/api/classify", json={"message": "Install SPSS on my staff laptop"})
    body = response.json()

    expected_keys = {
        "route",
        "confidence",
        "matched_service_id",
        "matched_name",
        "state_change_required",
        "knowledge_can_solve",
        "missing_fields",
        "next_action",
    }
    assert set(body.keys()) == expected_keys
