from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import verify_password
from app.schemas.user import PasswordUpdate, UserProfileUpdate
from app.services.user_service import UserService


def test_profile_update_persists_name(db_session, user_factory):
    user = user_factory(full_name="Before")
    updated = UserService(db_session).update_profile(
        user.id,
        UserProfileUpdate(full_name="After"),
    )

    assert updated.id == user.id
    assert updated.full_name == "After"
    assert db_session.get(type(user), user.id).full_name == "After"


def test_password_change_rejects_incorrect_current_password(
    db_session,
    user_factory,
):
    user = user_factory(password="Original123")
    original_hash = user.password_hash

    with pytest.raises(HTTPException) as error:
        UserService(db_session).update_password(
            user.id,
            PasswordUpdate(
                current_password="Wrong123",
                new_password="Replacement123",
            ),
        )

    assert error.value.status_code == 400
    assert user.password_hash == original_hash


def test_password_change_hashes_new_password(db_session, user_factory):
    user = user_factory(password="Original123")

    result = UserService(db_session).update_password(
        user.id,
        PasswordUpdate(
            current_password="Original123",
            new_password="Replacement123",
        ),
    )

    db_session.refresh(user)
    assert result == {"message": "Password updated successfully"}
    assert verify_password("Replacement123", user.password_hash)
    assert not verify_password("Original123", user.password_hash)


def test_missing_user_profile_and_password_updates_return_404(db_session):
    service = UserService(db_session)
    missing_id = uuid4()

    with pytest.raises(HTTPException) as profile_error:
        service.update_profile(
            missing_id,
            UserProfileUpdate(full_name="Unknown"),
        )
    with pytest.raises(HTTPException) as password_error:
        service.update_password(
            missing_id,
            PasswordUpdate(
                current_password="Original123",
                new_password="Replacement123",
            ),
        )

    assert profile_error.value.status_code == 404
    assert password_error.value.status_code == 404
