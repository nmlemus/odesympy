import streamlit as st

from google.oauth2 import service_account
from google.cloud import bigquery

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
_client = bigquery.Client(credentials=credentials)

from odesympy.utils import *


def get_systems():
    query = "SELECT * FROM `uqsim-371323.uqsim.system` LIMIT 1000"
    
    return _client.query(query).to_arrow(_client).to_pandas()


def get_system_id_from_system_name(system_name):
    query = """SELECT DISTINCT system_id FROM `uqsim-371323.uqsim.system` WHERE system_name="{system_name}" LIMIT 1"""
    query = query.format(system_name=system_name)
    return _client.query(query).to_arrow(_client).to_pandas()


def save_system(_client, system):

    job = _client.load_table_from_dataframe(system, system_table)
    
    return job

def save_model(_client, model):
    print(model)
    job = _client.load_table_from_dataframe(model, model_table)
    
    return job


def get_models_from_system(system_name):
    query = "SELECT * FROM `uqsim-371323.uqsim.model` WHERE system_id IN \
        (SELECT DISTINCT system_id FROM `uqsim-371323.uqsim.system` WHERE system_name=" + system_name + " LIMIT 1)"
    
    return _client.query(query).to_arrow(_client).to_pandas()