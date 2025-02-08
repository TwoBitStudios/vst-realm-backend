from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from core.constants import Provider
from core.models import Account, User
from core.routers.auth.utils import get_current_user

router = APIRouter(tags=['Auth'])


@router.get('/user/')
async def retrieve_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """ Retrieves the current authenticated user. """
    return current_user


@router.get('/account/')
async def retrieve_active_account(
    current_user: Annotated[User, Depends(get_current_user)], provider: Provider = Provider.LOCAL
) -> Account:
    """ Retrieves the active account associated with the current authenticated user. """
    account = await Account.find_one(Account.user_id == current_user.id, Account.provider == provider.value)

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='There is no active account associated with the current user',
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )

    return account
