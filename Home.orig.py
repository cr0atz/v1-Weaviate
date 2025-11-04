import streamlit as st
import streamlit_book as stb
import os
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="AI v1-Weaviate",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

# if cache_dir is not available, create it
if not os.path.exists("cache_dir"):
    os.makedirs("cache_dir")

st.title('Legal QA application V1')
st.markdown("---")

# Create a job post
if st.button(f"Upload Data", key="upload_data", help="Upload legal cases files"):
    # apply_values(_data)
    switch_page("Upload_Data")
st.markdown("---")

# Apply Jobs
if st.button(f"Question answering", key="question_answering", help="Ask questions"):
    # apply_values(_data)
    switch_page("Question_Answer")
