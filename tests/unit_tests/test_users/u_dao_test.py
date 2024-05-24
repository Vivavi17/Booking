import pytest

from users.dao import UsersDAO


@pytest.mark.parametrize(
    "id,email,is_exist",
    [(1, "test@test.com", True), (2, "artem@example.com", True), (3, "none", False)],
)
async def test_find_by_id(id, email, is_exist):
    user = await UsersDAO.find_by_id(id)
    if is_exist:
        assert user
        assert user.id == id
        assert user.email == email
    else:
        assert not user
