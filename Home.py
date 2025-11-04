import streamlit as st
import os
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="AI v1-Weaviate",
    page_icon="🤖",
    initial_sidebar_state="collapsed",
)

# if cache_dir is not available, create it
if not os.path.exists("cache_dir"):
    os.makedirs("cache_dir")

st.title('Legal QA application V1')
st.markdown("---")

# Apply Jobs
if st.button(f"Question answering", key="question_answering", help="Ask questions"):
    # apply_values(_data)
    switch_page("Question_Answer")
st.markdown("---")
