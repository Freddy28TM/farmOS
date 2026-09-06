from backend.app.security import hash_password, verify_password


def test_password_is_hashed():
    password = "FarmOS-test-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert isinstance(hashed_password, str)


def test_correct_password_verifies():
    password = "FarmOS-test-password"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)


def test_incorrect_password_fails():
    password = "FarmOS-test-password"
    wrong_password = "Wrong-password"

    hashed_password = hash_password(password)

    assert not verify_password(
        wrong_password,
        hashed_password,
    )


def test_same_password_generates_different_hashes():
    password = "FarmOS-test-password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_hash_can_be_verified_after_multiple_hashes():
    password = "FarmOS-test-password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)
