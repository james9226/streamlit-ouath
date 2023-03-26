from datetime import datetime, timedelta
import jwt
import streamlit as st
import asyncio
from httpx_oauth.clients.okta import OktaOAuth2
from streamlit_oauth.authenticator.login_page import login_page
import extra_streamlit_components as stx


class AuthManager:
    def __init__(self, client_config: dict, redirect_uri: str, page_name : str,
                 cookies_enabled: bool=False,
                 cookie_name: str = "",
                 cookie_signing_key : str = "",
                 cookie_expiry_seconds : int = 0,
                 ):
        self.client_config = client_config
        self.redirect_uri = redirect_uri
        self.page_name = page_name
        self.cookies_enabled = cookies_enabled
        self.cookie_name = cookie_name
        self.cookie_signing_key = cookie_signing_key
        self.cookie_expiry_seconds = cookie_expiry_seconds
        self.cookie_manager = stx.CookieManager()

        self.state_manager(["token", "user_email", "user_id", "authenticated"])
        self.client = OktaOAuth2(**client_config)

    def cookie_encode(self):
        """
        Encodes the contents of the reauthentication cookie.
        Returns
        -------
        str
            The JWT cookie for passwordless reauthentication.
        """
        return jwt.encode(
            {
                "user_email": st.session_state["user_email"],
                "user_id": st.session_state["user_id"],
                "exp_date": str(
            (
                datetime.utcnow() + timedelta(seconds=self.cookie_expiry_seconds)
            ).timestamp()
        ),  # type: ignore
            },
            self.cookie_signing_key,
            algorithm="HS256",
        )
    
    def cookie_decode(self, cookie):
        """
        Decodes the contents of the reauthentication cookie.
        Returns
        -------
        str
            The decoded JWT cookie for passwordless reauthentication.
        """
        try:
            return jwt.decode(cookie, self.cookie_signing_key, algorithms=["HS256"])
        except:
            return False
    

    def _check_cookie(self) -> None:
        """
        Checks the validity of the reauthentication cookie.
        """
        cookie = self.cookie_manager.get(self.cookie_name)
        if cookie is not None:
            cookie = self.cookie_decode(cookie)
            if cookie is not False:
                if cookie["exp_date"] > str(datetime.utcnow().timestamp()):
                    if "name" and "username" in cookie:
                        st.session_state["user_email"] = cookie["user_email"]
                        st.session_state["user_id"] = cookie["user_id"]
                        st.session_state["authenticated"] = True
        return None

    @staticmethod
    def state_manager(states):
        for state in states:
            if state not in st.session_state:
                st.session_state[state] = None
            else:
                # Hacky thing you do to stop state descoping
                st.session_state[state] = st.session_state[state]

    async def get_authorization_url(self):
        authorization_url = await self.client.get_authorization_url(
            self.redirect_uri,
            scope=["profile", "email"],
            extras_params={"access_type": "offline"},
        )
        return authorization_url

    async def get_access_token(self, code):
        token = await self.client.get_access_token(code, self.redirect_uri)
        return token

    async def get_user_info(self, token):
        user_id, user_email = await self.client.get_id_email(token)
        st.session_state["user_id"] = user_id
        st.session_state["user_email"] = user_email


    def verify_code(self, code, authorization_url):
        try:
            token = asyncio.run(self.get_access_token(code=code))
            self.verify_token(token, authorization_url)
        except:
            st.session_state["authenticated"] = False
            login_page(self.page_name, authorization_url, error_state=True)

    def verify_token(self, token, authorization_url): 
        # Check if token has expired:
        if token.is_expired():
            if token.is_expired():
                st.session_state["authenticated"] = False
                login_page(self.page_name, authorization_url, error_state=True)
        else:
            st.session_state["token"] = token
            user_id, user_email = "test", "test@gmail.com"
            st.session_state["user_id"] = user_id
            st.session_state["user_id"] = user_email
            st.session_state["authenticated"] = True
            self.cookie_manager.set(
                self.cookie_name,
                self.cookie_encode(),
                expires_at=datetime.now()
                + timedelta(seconds=self.cookie_expiry_seconds),
            )

    def authenticate(self):
        authorization_url = asyncio.run(self.get_authorization_url())
        if st.session_state["token"] is None and not self._check_cookie():
            try:
                code = st.experimental_get_query_params()["code"]
            except:
                login_page(self.page_name, authorization_url, error_state=False)
            else:
                self.verify_code(code, authorization_url)
        else:
            self.verify_token(st.session_state["token"], authorization_url)

    def authenticated(self, page, *args, **kwargs):
        if st.session_state["authenticated"]:
            page(*args, **kwargs)

