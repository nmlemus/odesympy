import streamlit as st
from streamlit_ace import st_ace
from pygom import DeterministicOde
from pygom import Transition, TransitionType, common_models
import yaml
import sympy
import numpy as np
import pandas as pd

st.set_page_config(page_title="Models", page_icon="🗠", layout="wide")

st.markdown("# Select or Create a new Model")

st.sidebar.success("Models")

# Spawn a new Ace editor
content = st_ace(language="yaml",  theme="dracula",
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
    
    st.subheader('Simulate the Model')

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