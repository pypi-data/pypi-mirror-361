import os

import pytest
from proxy import TestCase

from tastytrade import Account, OAuthSession, Session


def test_get_customer(session: Session):
    session.get_customer()


async def test_get_customer_async(session: Session):
    await session.a_get_customer()


def test_get_2fa_info(session: Session):
    session.get_2fa_info()


async def test_get_2fa_info_async(session: Session):
    await session.a_get_2fa_info()


def test_destroy(credentials: tuple[str, str]):
    session = Session(*credentials)
    session.destroy()


async def test_destroy_async(credentials: tuple[str, str]):
    session = Session(*credentials)
    await session.a_destroy()


def test_serialize_deserialize(session: Session):
    data = session.serialize()
    obj = Session.deserialize(data)
    assert set(obj.__dict__.keys()) == set(session.__dict__.keys())


@pytest.mark.usefixtures("inject_credentials")
class TestProxy(TestCase):
    def test_session_with_proxy(self):
        assert self.PROXY is not None
        session = Session(
            *self.credentials,  # type: ignore
            proxy=f"http://127.0.0.1:{self.PROXY.flags.port}",
        )
        assert session.validate()
        session.destroy()


def test_cert_session():
    username = os.getenv("TT_USERNAME_SANDBOX")
    password = os.getenv("TT_PASSWORD_SANDBOX")
    assert username and password
    session = Session(username, password, is_test=True)
    session.destroy()


@pytest.fixture(scope="module")
async def oauth(aiolib: str) -> OAuthSession:
    refresh = os.getenv("TT_REFRESH")
    secret = os.getenv("TT_SECRET")
    assert refresh and secret
    return OAuthSession(secret, refresh)


def test_oauth_refresh(oauth: OAuthSession):
    pass


def test_oauth_serialization(oauth: OAuthSession):
    session_str = oauth.serialize()
    session2 = OAuthSession.deserialize(session_str)
    print(oauth.session_token == session2.session_token)
    Account.get(session2)


async def test_oauth_refresh_async(oauth: OAuthSession):
    await oauth.a_refresh()
