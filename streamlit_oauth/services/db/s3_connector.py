import streamlit as st
import pandas as pd

DATE_COLUMN: str = "date/time"
DATA_URL: str = (
    "https://s3-us-west-2.amazonaws.com/"
    "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)


@st.cache_data(show_spinner="Fetching data from DB...", ttl=86400)
def load_data(nrows: int) -> pd.DataFrame:
    """
    Fetches a set number of rows of data from the streamlit raw uber data and returns it as a pandas DataFrame.
    Production deployment caches the data using the streamlit decorator.

    Parameters
    ----------
    nrows : int
        Number of rows of data to fetch

    Returns
    -------
    pd.DataFrame
        Containing the first ``nrows`` rows of data.
    """

    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data