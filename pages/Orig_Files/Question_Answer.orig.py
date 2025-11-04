import streamlit as st
import requests
import json
import numpy as np
import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()
API_endpoint = os.getenv("API_ENDPOINT")

st.set_page_config(
    layout="wide",
    page_title="AI v1-Weaviate",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)
st.title("FLAST-AI V1 on Weaviate")

prompts_folder = "prompts"


def get_answer_from_api(user_question, model):

    payload = {
        "user_question": user_question,
        "user_model": model,
        "user_auth": "ntel101919"
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(API_endpoint, headers=headers, json=payload)

    return response.text


left_column, right_column = st.columns(2)

with left_column:

    with open(os.path.join(prompts_folder, 'prompt.txt'), 'r') as f:
        prompt = f.read()
    with open(os.path.join(prompts_folder, 'reasoning_prompt.txt'), 'r') as f:
        reasoning_prompt = f.read()

    with st.expander("Answer Prompt Configuration"):
        form = st.form(key='form_prompts')
        prompt_view = form.text_area(
            label="Prompt",
            placeholder="Prompt",
            value=prompt
        )
        if form.form_submit_button(label="Save Prompt", use_container_width=True):
            with open(os.path.join(prompts_folder, 'prompt.txt'), 'w') as f:
                f.write(prompt_view)
            st.success("Prompts has been saved successfully.")

    with st.expander("Reasoning Prompt Configuration"):
        form = st.form(key='form_reasoning_prompts')
        prompt_reasoning_view = form.text_area(
            label="Reasoning Prompt",
            placeholder="Reasoning Prompt",
            value=reasoning_prompt
        )
        if form.form_submit_button(label="Save Prompt", use_container_width=True):
            with open(os.path.join(prompts_folder, 'reasoning_prompt.txt'), 'w') as f:
                f.write(prompt_reasoning_view)
            st.success("Reasoning Prompts has been saved successfully.")

    form = st.form(key='my_form')
    user_question = form.text_area(label='Enter your question')
    submit_button = form.form_submit_button(label='Submit')

if submit_button:
    with right_column:
        ans_dict = get_answer_from_api(user_question, "gpt-4")
        ans_dict = json.loads(ans_dict)
        st.success("Answer : \n\n  " + ans_dict['answer'])
        st.success("Reasoning : \n\n  " + ans_dict['reasoning'])
        st.info("Context : \n\n  " + ans_dict['context'])
        st.warning("Reference case name : \n\n " + ans_dict['case_name'])
