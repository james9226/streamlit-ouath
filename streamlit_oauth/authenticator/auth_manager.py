import streamlit as st
import asyncio
from httpx_oauth.clients.okta import OktaOAuth2
import webbrowser

from streamlit_oauth.authenticator.login_page import login_page


class AuthManager:
    def __init__(self, client_config: dict, redirect_uri: str, page_name : str):
        self.client_config = client_config
        self.redirect_uri = redirect_uri
        self.page_name = page_name

        self.state_manager(["token", "user_email", "user_id", "authenticated"])
        self.client = OktaOAuth2(**client_config)

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

    def authenticate(self):
        authorization_url = asyncio.run(self.get_authorization_url())
        if st.session_state["token"] is None:
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
