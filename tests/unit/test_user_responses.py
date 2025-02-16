from app.responses.user import (
    PaginatedUserResponse,
    Pagination,
    SingleUserResponse,
    UserCreateResponse,
    UserResponse,
    UserUpdateResponse,
)


def test_user_response(test_user):
    user_response = UserResponse(
        id=test_user.id,
        username=test_user.username,
        email=test_user.email,
        created_at=test_user.created_at,
        updated_at=test_user.updated_at,
    )
    assert user_response.id == test_user.id
    assert user_response.username == test_user.username
    assert user_response.email == test_user.email


def test_single_user_response(test_user):
    single_user_response = SingleUserResponse(
        data=UserResponse(
            id=test_user.id,
            username=test_user.username,
            email=test_user.email,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        ),
        status_code=200,
    )
    assert single_user_response.data.id == test_user.id
    assert single_user_response.status_code == 200


def test_paginated_user_response(test_user):
    paginated_user_response = PaginatedUserResponse(
        data=[
            UserResponse(
                id=test_user.id,
                username=test_user.username,
                email=test_user.email,
                created_at=test_user.created_at,
                updated_at=test_user.updated_at,
            )
        ],
        meta=Pagination(
            current_page=1,
            last_page=1,
            first_item=1,
            last_item=1,
            items_per_page=10,
            total=1,
        ),
        status_code=200,
    )
    assert len(paginated_user_response.data) == 1
    assert paginated_user_response.meta.total == 1


def test_user_create_response(test_user):
    user_create_response = UserCreateResponse(
        id=test_user.id,
        username=test_user.username,
        email=test_user.email,
        created_at=test_user.created_at,
        updated_at=test_user.updated_at,
    )
    assert user_create_response.id == test_user.id
    assert user_create_response.username == test_user.username


def test_user_update_response(test_user):
    user_update_response = UserUpdateResponse(
        id=test_user.id,
        username=test_user.username,
        email=test_user.email,
        created_at=test_user.created_at,
        updated_at=test_user.updated_at,
    )
    assert user_update_response.id == test_user.id
    assert user_update_response.username == test_user.username
