import datetime
import streamlit as st
import numpy as np
from streamlit_oauth.services.db.s3_connector import load_data
from streamlit_oauth.services.ml_model.model import expensive_model
from streamlit_oauth.utils.formattor import number_format
import extra_streamlit_components as stx


def dashboard():

    DATE_COLUMN: str = "date/time"

    if "key" not in st.session_state:
        st.session_state["load_model"] = False

    # All layout of the page comes below

    st.title("Uber pickups in NYC")

    data = load_data(100000)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Weekly Ridership", number_format(1259), "+12%")

    with col2:
        st.metric(
            "Marketshare", f"{number_format(55.6, 1)}%", f"{number_format(-1.2, 1)}%"
        )

    with col3:
        st.metric(
            "Weekly Revenue", f"${number_format(25160)}", f"{number_format(6.8, 1)}%"
        )

    st.subheader("Raw data")
    st.dataframe(data, use_container_width=True)

    with st.echo():
        # This is all it takes to do a simple bar chart!
        st.subheader("Number of pickups by hour")
        hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
        st.bar_chart(hist_values)

    hour_to_filter = st.slider("hour", 0, 23, 17)  # min: 0h, max: 23h, default: 17h
    filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
    st.subheader(f"Map of all pickups at {hour_to_filter}:00")
    st.map(filtered_data)

    option = st.selectbox("Select delay:", (1, 2, 3))
    st.session_state.load_model = False

    with st.spinner("Please wait"):
        _ = expensive_model(option)
        st.session_state.load_model = True

    if st.session_state.load_model:
        st.success("Done!")


    def set_test_cookie():
        cookie_manager = stx.CookieManager()
        cookie_manager.set(
        'test123',
        'ThisIsATest',
        expires_at=datetime.now()
        + datetime.timedelta(seconds=60 * 60),
    )


    if st.button('Press to set a cookie!', key=2151):
        set_test_cookie()

