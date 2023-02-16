import streamlit as st

st.set_page_config(page_title="Systems", page_icon="📈")

st.markdown("# Select or Create a new ODE System")

st.sidebar.success("Systems")

system_name = st.text_input('System Name', 'e.g. Lotka-Volterra')

system_description = st.text_area('Description of the System', '''e.g. The Lotka–Volterra equations, also known as the predator–prey equations, are a pair of first-order nonlinear differential equations, frequently used to describe the dynamics of biological systems in which two species interact, one as a predator and the other as prey. The populations change through time according to the pair of equations:
    ''', max_chars=500)


if st.button('Save System'):
    st.write('The **' + system_name + '** system was saved.')