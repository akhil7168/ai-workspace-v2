def test_profile_endpoints_require_authentication(client):
    assert client.get("/users/me").status_code == 401
    assert client.get("/users/profile").status_code == 401
    assert client.put(
        "/users/profile",
        json={"full_name": "Updated Name"},
    ).status_code == 401
    assert client.patch(
        "/users/password",
        json={
            "current_password": "Password123",
            "new_password": "Replacement123",
        },
    ).status_code == 401


def test_user_can_read_and_update_profile(client, authenticated_user):
    account = authenticated_user()

    profile = client.get("/users/profile", headers=account["headers"])
    assert profile.status_code == 200
    assert profile.json()["email"] == account["credentials"]["email"]

    update = client.put(
        "/users/profile",
        headers=account["headers"],
        json={"full_name": "Updated Integration User"},
    )
    assert update.status_code == 200
    assert update.json()["full_name"] == "Updated Integration User"


def test_password_change_validates_old_password_and_updates_credentials(
    client,
    authenticated_user,
):
    account = authenticated_user()
    wrong_password = client.patch(
        "/users/password",
        headers=account["headers"],
        json={
            "current_password": "WrongPassword123",
            "new_password": "Replacement123",
        },
    )
    assert wrong_password.status_code == 400

    changed = client.patch(
        "/users/password",
        headers=account["headers"],
        json={
            "current_password": account["credentials"]["password"],
            "new_password": "Replacement123",
        },
    )
    assert changed.status_code == 200
    assert changed.json() == {"message": "Password updated successfully"}

    old_login = client.post(
        "/auth/login",
        json={
            "email": account["credentials"]["email"],
            "password": account["credentials"]["password"],
        },
    )
    new_login = client.post(
        "/auth/login",
        json={
            "email": account["credentials"]["email"],
            "password": "Replacement123",
        },
    )
    assert old_login.status_code == 401
    assert new_login.status_code == 200


def test_profile_and_password_payload_validation(client, authenticated_user):
    account = authenticated_user()
    bad_profile = client.put(
        "/users/profile",
        headers=account["headers"],
        json={"full_name": "X"},
    )
    bad_password = client.patch(
        "/users/password",
        headers=account["headers"],
        json={
            "current_password": "Password123",
            "new_password": "short",
        },
    )

    assert bad_profile.status_code == 422
    assert bad_password.status_code == 422
