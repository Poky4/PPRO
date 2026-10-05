from fastapi import status


def test_login_success(client, admin_user):
    """Test úspěšného přihlášení a obdržení JWT tokenu."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "adminpass123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, admin_user):
    """Test přihlášení se špatným heslem."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Nesprávné přihlašovací jméno nebo heslo" in response.json()["detail"]


def test_login_nonexistent_user(client, db_session):
    """Test přihlášení s neexistujícím uživatelem."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent", "password": "somepassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_profile(client, admin_user, admin_token_headers):
    """Test získání vlastního profilu z endpointu /auth/me s tokenem."""
    response = client.get("/api/v1/auth/me", headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == admin_user.username
    assert data["email"] == admin_user.email
    assert data["role"] == "ADMIN"


def test_get_current_user_profile_unauthorized(client):
    """Test přístupu k /auth/me bez autorizačního tokenu."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
