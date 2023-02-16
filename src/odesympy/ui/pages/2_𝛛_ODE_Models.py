import streamlit as st
from streamlit_ace import st_ace

st.set_page_config(page_title="Models", page_icon="🗠")

st.markdown("# Select or Create a new Model")

st.sidebar.success("Models")

# Spawn a new Ace editor
content = st_ace(language="python",  theme="dracula",
    keybinding="vscode", font_size=16, min_lines=15, show_print_margin=False)