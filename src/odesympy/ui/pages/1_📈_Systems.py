import streamlit as st
import pandas as pd

from google.oauth2 import service_account
from google.cloud import bigquery

from odesympy.utils import *
from odesympy.data import queries

from datetime import datetime

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
_client = bigquery.Client(credentials=credentials)


st.set_page_config(page_title="Systems", page_icon="📈", layout="wide")

st.markdown("# Select or Create a new ODE System")

systems = queries.get_systems()

st.subheader("Systems in Database")

grid_response = get_AgGrid(systems[['system_name', 'description']], multi_selection=False, use_checkbox=True)

selected = grid_response['selected_rows']
selected_df = pd.DataFrame(selected)

st.sidebar.success("Systems")

st.subheader("Create New Systems")

with st.expander("See explanation"):
    st.write("\n In ODESym the information is organized hierarchically and Systems are the main objects. Each system (e.g. physical or biological) \
             can be modeling by many mathematical models.")

system_name = st.text_input('System Name', 'e.g. Lotka-Volterra')

system_description = st.text_area('Description of the System', '''e.g. The Lotka–Volterra equations, also known as the predator–prey equations, are a pair of first-order nonlinear differential equations, frequently used to describe the dynamics of biological systems in which two species interact, one as a predator and the other as prey. The populations change through time according to the pair of equations:
    ''', max_chars=500)

if selected_df.shape[0] > 0:
    st.session_state.system_name = selected_df.system_name.unique()
    st.session_state.system_description = selected_df.description.unique()


if st.button('Save System'):
    now = datetime.now()
    unique_id = int((now - datetime(1970, 1, 1)).total_seconds())

    df = []
    data = {
        'system_id': unique_id,
        'system_name': system_name,
        'description': system_description
    }
    df.append(data)
    df = pd.DataFrame.from_dict(df)
    try:
        job = queries.save_system(_client, df)
        
        st.write('The **' + system_name + '** system was saved.')
    except:
        st.write('There was an error, please try again latter.')