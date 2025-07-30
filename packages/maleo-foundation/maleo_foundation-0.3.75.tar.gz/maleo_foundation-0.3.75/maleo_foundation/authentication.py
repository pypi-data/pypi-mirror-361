from starlette.authentication import AuthCredentials, BaseUser
from typing import Optional, Sequence
from maleo_foundation.models.transfers.general.authentication import Token


class Credentials(AuthCredentials):
    def __init__(
        self, token: Optional[Token] = None, scopes: Optional[Sequence[str]] = None
    ) -> None:
        self._token = token
        super().__init__(scopes)

    @property
    def token(self) -> Optional[Token]:
        return self._token


class User(BaseUser):
    def __init__(
        self, authenticated: bool = False, username: str = "", email: str = ""
    ) -> None:
        self._authenticated = authenticated
        self._username = username
        self._email = email

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def display_name(self) -> str:
        return self._username

    @property
    def identity(self) -> str:
        return self._email
