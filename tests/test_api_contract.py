from fastapi.testclient import TestClient
from app.api import app


def test_api_schema_is_exposed_and_post_bodies_are_validated():
    with TestClient(app) as client:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert schema["paths"]
        for path, methods in schema["paths"].items():
            operation = methods.get("post", {})
            if operation.get("requestBody", {}).get("required") and "{" not in path:
                response = client.post(path, json={})
                assert response.status_code == 422, (path, response.text)
