from datetime import datetime, timedelta
import time
import jwt
import streamlit as st
import asyncio
from httpx_oauth.clients.okta import OktaOAuth2
from streamlit_oauth.authenticator.login_page import login_page
# import extra_streamlit_components as stx
from streamlit_cookies_manager import EncryptedCookieManager


class AuthManager:
    def __init__(self, 
                 client_config: dict, 
                 redirect_uri: str, 
                 page_name : str,
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

        self.cookie_manager = EncryptedCookieManager(
            prefix='streamlit/auth/cookies/',
            password=cookie_signing_key
        )      


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
    

    def _check_cookie(self) -> bool:
        """
        Checks the validity of the reauthentication cookie.
        """
        if not self.cookies_enabled:
            return False 

        # st.write(self.cookie_manager)
        if 'token' not in self.cookie_manager:
            return False

        cookie = self.cookie_manager['token']
        if cookie is not None:
            cookie = self.cookie_decode(cookie)
            if cookie is not False:
                if cookie["exp_date"] > str(datetime.utcnow().timestamp()):
                    if "user_email" and "user_id" in cookie:
                        st.session_state["user_email"] = cookie["user_email"]
                        st.session_state["user_id"] = cookie["user_id"]
                        st.session_state["authenticated"] = True
                        return True
        return False

    def state_manager(self, states):
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

            if self.cookies_enabled:
                self.cookie_manager["token"] = self.cookie_encode()
                self.cookie_manager.save()

                # self.cookie_manager.set(
                #     self.cookie_name,
                #     self.cookie_encode(),
                #     expires_at=datetime.now()
                #     + timedelta(seconds=self.cookie_expiry_seconds),
                # )

            
            st.session_state["authenticated"] = True

    def logout(self, button_name: str, location: str = "main"):
        """
        Creates a logout button.
        Parameters
        ----------
        button_name: str
            The rendered name of the logout button.
        location: str
            The location of the logout button i.e. main or sidebar.
        """
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            if st.button(button_name):
                self.cookie_manager["token"] = 'Logged Out'
                self.cookie_manager.save()                
                st.session_state["token"] = None
                st.session_state["user_id"] = None
                st.session_state["user_email"] = None        
                st.session_state["authenticated"] = False

                # st.session_state["login_failure"] = None
        elif location == "sidebar":
            if st.sidebar.button(button_name):
                self.cookie_manager["token"] = 'Logged Out'
                self.cookie_manager.save()                
                st.session_state["token"] = None
                st.session_state["user_id"] = None
                st.session_state["user_email"] = None        
                st.session_state["authenticated"] = False

    def authenticate(self):

        if not self.cookie_manager.ready():
    # Wait for the component to load and send us current cookies.
            st.stop()

        authorization_url = asyncio.run(self.get_authorization_url())

        if self._check_cookie():
            pass
        elif st.session_state["token"] is None:
            try:
                code = st.experimental_get_query_params()["code"]
                self.verify_code(code, authorization_url)
            except:
                login_page(self.page_name, authorization_url, error_state=False)
        else:
            self.verify_token(st.session_state["token"], authorization_url)


    # def authenticate(self):
    #     authorization_url = asyncio.run(self.get_authorization_url())

    #     self.state_manager(["token", "user_email", "user_id", "authenticated"])
    #     time.sleep(1)

    #     st.session_state['token'] = None

    #     # if self._check_cookie():
    #     #     pass
    #     # if "token" not in st.session_state:
    #     #     self.state_manager(["token", "user_email", "user_id", "authenticated"])
    #     if st.session_state["token"] is None:
    #         try:
    #             code = st.experimental_get_query_params()["code"]
    #         except:
    #             login_page(self.page_name, authorization_url, error_state=False)
    #     else:
            # self.verify_code(code, authorization_url)

        # if st.session_state["token"] is None and not self._check_cookie():
        #     try:
        #         code = st.experimental_get_query_params()["code"]
        #     except:
        #         login_page(self.page_name, authorization_url, error_state=False)
        #     else:
        #         self.verify_code(code, authorization_url)
        # else:
        #     self.verify_token(st.session_state["token"], authorization_url)

    def authenticated(self, page, *args, **kwargs):
        if st.session_state["authenticated"]:
            page(*args, **kwargs)

