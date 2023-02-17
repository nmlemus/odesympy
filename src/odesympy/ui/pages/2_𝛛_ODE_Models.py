import streamlit as st
from streamlit_ace import st_ace
from pygom import DeterministicOde
from pygom import Transition, TransitionType, common_models
import yaml
import sympy
import numpy as np
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

st.set_page_config(page_title="Models", page_icon="🗠", layout="wide")

st.markdown("# Math Models")

systems = queries.get_systems()

system = st.selectbox(
    'Please select a System',
    list(systems.system_name.unique()))

system_id = queries.get_system_id_from_system_name(system)
system_id = system_id.system_id.unique()[0]

st.sidebar.success("Models")

st.subheader("ODE Equations in YAML Format")
# Spawn a new Ace editor
content = st_ace(value="""# Example 
# Model Variables
stateList: ['S', 'I', 'R']

# Model Parameters
paramList: ['beta', 'gamma']

# Model Transitions
transition1:
    origin: 'S'
    equation: '-beta*S*I'
    
transition2:
    origin: 'I'
    equation: 'beta*S*I - gamma*I'
    
transition3:
    origin: 'R'
    equation: 'gamma*I'
""", language="yaml",  theme="dracula",
    keybinding="vscode", font_size=16, min_lines=20, show_print_margin=False)

if len(content) > 0:
    model_yaml = yaml.unsafe_load(content)
    ode = []
    stateList = []
    paramList = []
    for key in model_yaml.keys():
        if 'stateList' == str(key):
            stateList = model_yaml.get(key)
        elif str(key) == 'paramList':
            paramList = model_yaml.get(key)
        else:
            ode.append(Transition(origin=model_yaml.get(key)['origin'], 
                                equation=model_yaml.get(key)['equation'], 
                                transition_type=TransitionType.ODE))

    model = DeterministicOde(stateList, paramList, ode=ode)

    # TODO: reorganize the symbols because the usual notation is params first, variables next (e.g. alpha*S)

    A = model.get_ode_eqn()
    
    B = sympy.zeros(A.rows,2)
    for i in range(A.shape[0]):
        B[i,0] = sympy.symbols('d' + str(stateList[i]) + '/dt=')
        B[i,1] = A[i]

    st.subheader('Model Equations in Latex')

    st.latex(sympy.latex(B, mat_str="array", mat_delim=None,
                            inv_trig_style='full'))

model_description = st.text_area('Description of the Model', ''' ''', max_chars=500)

if st.button('Save Model'):
    now = datetime.now()
    unique_id = int((now - datetime(1970, 1, 1)).total_seconds())

    df = []
    data = {
        'system_id': system_id,
        'model_id': unique_id,
        'model_ode_eqn': str(content),
        'model_description': model_description
    }
    df.append(data)
    
    df = pd.DataFrame.from_dict(df)
    print(df)
    try:
        job = queries.save_model(_client, df)
        
        st.write('The **' + "model" + '** was saved.')
    except:
        st.write('There was an error, please try again latter.')

    
    st.header('Simulate the Model')
    st.markdown('#### If you want to simulate this model, please specify the initial conditions, params values and time below, then clic simulate.')

with st.form("sim_form"):
    x0 = []
    model_params = []

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Initial Conditions')
        for state_var in stateList:
            x0.append(float(st.text_input(str(state_var), value=1)))

    with col2:
        st.subheader('Parameters')
        for param_var in paramList:
            model_params.append(float(st.text_input(str(param_var), value=1)))

        st.subheader('Time')

        t0 = int(st.text_input('Start Time', value=1))
        tf = int(st.text_input('End Time', value=10))
        dt = int(st.text_input('Time Steps', value=100))


    # Every form must have a submit button.
    submitted = st.form_submit_button("Simulate Model")
    if submitted:

        st.info('Simulating the model with initial conditions: ' + str(x0) + ' and params ' + \
                str(model_params) + ' from t0 = ' + str(t0) + ' to t = ' + str(tf))

        # Solve the model
        t = np.linspace(t0, dt, tf)

        model.parameters = model_params

        model.initial_values = (x0, t[0])

        solutionReference = model.integrate(t[1::], full_output=False)
        chart_data = pd.DataFrame(
            solutionReference,
            columns=stateList)

        st.subheader('Simulation Result')
        st.line_chart(chart_data)