import streamlit as st
from streamlit_ace import st_ace
from pygom import DeterministicOde
from pygom import Transition, TransitionType, common_models
import yaml
import sympy
import numpy as np
import pandas as pd

st.set_page_config(page_title="Models", page_icon="🗠")

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

    A = model.get_ode_eqn()
    B = sympy.zeros(A.rows,2)
    for i in range(A.shape[0]):
        B[i,0] = sympy.symbols('d' + str(stateList[i]) + '/dt=')
        B[i,1] = A[i]

    st.subheader('Model Equations in Latex')

    st.latex(sympy.latex(B, mat_str="array", mat_delim=None,
                            inv_trig_style='full'))
    
    st.subheader('Simulate the Model')
    

    # Solve the model
    x0 = [1, 1.27e-6, 0]
    t = np.linspace(0, 150, 100)

    model.parameters = [0.5, 1.0/3.0]

    model.initial_values = (x0, t[0])

    solutionReference = model.integrate(t[1::], full_output=False)
    chart_data = pd.DataFrame(
        solutionReference,
        columns=stateList)

    st.subheader('Simulation Result')
    st.line_chart(chart_data)