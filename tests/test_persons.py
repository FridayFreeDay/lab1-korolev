"""Unit-тесты операций над сущностью Person."""


def test_create_person_returns_201_and_location_header(client, person_payload):
    # Arrange / Act
    response = client.post("/api/v1/persons", json=person_payload)

    # Assert
    assert response.status_code == 201
    assert response.content == b""
    location = response.headers["Location"]
    person_id = location.split("/")[-1]
    assert location == f"/api/v1/persons/{person_id}"
    assert person_id.isdigit()


def test_get_person_returns_created_data(client, person_payload, created_person_id):
    # Act
    response = client.get(f"/api/v1/persons/{created_person_id}")

    # Assert
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    assert response.json() == {"id": created_person_id, **person_payload}


def test_get_unknown_person_returns_404(client):
    # Act
    response = client.get("/api/v1/persons/9999")

    # Assert
    assert response.status_code == 404
    assert response.json()["message"]


def test_list_persons_returns_array_with_created_person(
    client, person_payload, created_person_id
):
    # Act
    response = client.get("/api/v1/persons")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert {"id": created_person_id, **person_payload} in body


def test_patch_updates_only_passed_fields(client, person_payload, created_person_id):
    # Arrange
    patch = {"name": "Petr Petrov", "address": "Lefortovo 1"}

    # Act
    response = client.patch(f"/api/v1/persons/{created_person_id}", json=patch)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == patch["name"]
    assert body["address"] == patch["address"]
    assert body["work"] == person_payload["work"]
    assert body["age"] == person_payload["age"]


def test_patch_unknown_person_returns_404(client):
    # Act
    response = client.patch("/api/v1/persons/9999", json={"name": "Nobody"})

    # Assert
    assert response.status_code == 404


def test_delete_person_returns_204_and_removes_record(client, created_person_id):
    # Act
    delete_response = client.delete(f"/api/v1/persons/{created_person_id}")

    # Assert
    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert client.get(f"/api/v1/persons/{created_person_id}").status_code == 404


def test_create_person_without_name_returns_400(client):
    # Act
    response = client.post("/api/v1/persons", json={"age": 20})

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body["message"]
    assert "name" in body["errors"]


def test_health_returns_status_up(client):
    # Act
    response = client.get("/manage/health")

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "UP"
