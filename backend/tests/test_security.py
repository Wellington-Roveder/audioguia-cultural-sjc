from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_store_plain_password():
    password = "senha-segura-123"

    hashed = hash_password(password)

    assert hashed != password


def test_verify_password_returns_true_for_correct_password():
    password = "senha-segura-123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_returns_false_for_wrong_password():
    hashed = hash_password("senha-correta-123")

    assert (
        verify_password(
            "senha-errada-123",
            hashed,
        )
        is False
    )


def test_create_and_decode_access_token():
    subject = "admin-user-id"

    token = create_access_token(subject)

    decoded_subject = decode_access_token(token)

    assert decoded_subject == subject


def test_decode_invalid_access_token_returns_none():
    decoded_subject = decode_access_token("invalid-token")

    assert decoded_subject is None
