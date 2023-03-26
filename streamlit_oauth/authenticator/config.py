import streamlit as st 

okta_client_config = {
        "client_id": st.secrets["okta"]["client_id"],
        "client_secret": st.secrets["okta"]["client_secret"],
        "okta_domain": st.secrets["okta"]["okta_domain"],
}

redirect_uri = st.secrets["redirect_uri"]