contact_info = {
    "first_name": "Test",
    "last_name": "Contact",
    "email": "test@example.com",
    "phone": "+1234567890",
    "birthday": "1990-01-01",
    "additional_info": "Test contact info",
}


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json=contact_info,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Contact"
    assert data["email"] == "test@example.com"
    assert data["phone"] == "+1234567890"
    assert data["birthday"] == "1990-01-01"
    assert data["additional_info"] == "Test contact info"
    assert "id" in data


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Test"
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == "Test"
    assert "id" in data[0]


def test_update_contact(client, get_token):
    contact_info["first_name"] = "new_test_contact"
    response = client.put(
        "/api/contacts/1",
        json=contact_info,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "new_test_contact"
    assert "id" in data


def test_update_contact_not_found(client, get_token):
    contact_info["first_name"] = "new_test_contact"
    response = client.put(
        "/api/contacts/2",
        json=contact_info,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "new_test_contact"
    assert "id" in data


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_create_contact_missing_fields(client, get_token):
    incomplete_contact_info = {
        "first_name": "Test",
        "last_name": "Contact",
        "email": "test@example.com",  # missing phone, birthday, etc.
    }
    response = client.post(
        "/api/contacts",
        json=incomplete_contact_info,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_create_contact_invalid_birthday(client, get_token):
    invalid_contact_info = contact_info.copy()
    invalid_contact_info["birthday"] = "invalid-date-format"
    response = client.post(
        "/api/contacts",
        json=invalid_contact_info,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_get_contacts_empty(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == []


def test_update_contact_invalid_email(client, get_token):
    contact_info["email"] = "invalid-email"
    response = client.put(
        "/api/contacts/1",
        json=contact_info,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_delete_contact_not_found(client, get_token):
    response = client.delete(
        "/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contact_unauthorized(client):
    response = client.get("/api/contacts/1")
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not authenticated"
