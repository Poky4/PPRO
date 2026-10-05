from fastapi import status


def test_create_user_by_admin(client, admin_token_headers):
    """Test vytvoření nového lékaře administrátorem."""
    user_data = {
        "username": "mudr_novak",
        "email": "novak@ordinace.cz",
        "full_name": "MUDr. Jan Novák",
        "role": "LEKAR",
        "password": "securepassword123",
        "is_active": True,
    }
    response = client.post("/api/v1/users/", json=user_data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "mudr_novak"
    assert data["full_name"] == "MUDr. Jan Novák"
    assert data["role"] == "LEKAR"
    assert "hashed_password" not in data


def test_create_user_forbidden_for_receptionist(client, normal_token_headers):
    """Běžný uživatel (recepční) nesmí mít právo zakládat nové účty."""
    user_data = {
        "username": "hacker",
        "email": "hacker@test.cz",
        "full_name": "Hacker",
        "role": "ADMIN",
        "password": "password123",
    }
    response = client.post("/api/v1/users/", json=user_data, headers=normal_token_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_duplicate_username(client, admin_token_headers, admin_user):
    """Test pokusu o registraci již existujícího uživatelského jména."""
    user_data = {
        "username": admin_user.username,
        "email": "different@test.cz",
        "full_name": "Jiný Admin",
        "role": "ADMIN",
        "password": "password123",
    }
    response = client.post("/api/v1/users/", json=user_data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "již existuje" in response.json()["detail"]


def test_list_users_as_admin(client, admin_token_headers, admin_user, normal_user):
    """Test získání seznamu uživatelů administrátorem."""
    response = client.get("/api/v1/users/", headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) >= 2


def test_list_users_forbidden_for_receptionist(client, normal_token_headers):
    """Recepční nesmí vidět kompletní seznam všech uživatelů."""
    response = client.get("/api/v1/users/", headers=normal_token_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user(client, admin_token_headers, normal_user):
    """Test editace uživatelského účtu administrátorem."""
    update_data = {
        "full_name": "Paní Věra Upravená",
        "email": "nova_vera@ordinace.cz",
    }
    response = client.put(
        f"/api/v1/users/{normal_user.id}",
        json=update_data,
        headers=admin_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Paní Věra Upravená"
    assert data["email"] == "nova_vera@ordinace.cz"


def test_deactivate_user(client, admin_token_headers, normal_user):
    """Test soft-delete deaktivace uživatele."""
    response = client.delete(
        f"/api/v1/users/{normal_user.id}",
        headers=admin_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] is False


def test_admin_cannot_deactivate_self(client, admin_token_headers, admin_user):
    """Administrátor nesmí mít možnost deaktivovat svůj vlastní běžící účet."""
    response = client.delete(
        f"/api/v1/users/{admin_user.id}",
        headers=admin_token_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nemůže deaktivovat svůj vlastní" in response.json()["detail"]
