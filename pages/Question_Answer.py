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
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")  # Information: Read auth token from environment

st.set_page_config(
    layout="wide",
    page_title="FLAST-AI v1-Vector",
    page_icon="🤖",
    initial_sidebar_state="collapsed",
)
st.title("FLAST-AI V1-Vector")

prompts_folder = "prompts"

# Load prompts without displaying them
with open(os.path.join(prompts_folder, 'prompt.txt'), 'r') as f:
    prompt = f.read()
with open(os.path.join(prompts_folder, 'reasoning_prompt.txt'), 'r') as f:
    reasoning_prompt = f.read()

def get_answer_from_api(user_question, model):
    # Information: Use auth token from environment instead of hardcoded value
    if not API_AUTH_TOKEN:
        return json.dumps({"error": "API_AUTH_TOKEN not configured in .env"})
    
    # Information: Use X-API-Key header (preferred) with payload fallback for backward compatibility
    payload = {
        "user_question": user_question,
        "user_model": model,
        "user_auth": API_AUTH_TOKEN  # Keep for backward compatibility
    }
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_AUTH_TOKEN  # Information: Header-based auth (preferred)
    }
    try:
        response = requests.post(API_endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"API request failed: {str(e)}")
        return json.dumps({"error": str(e)})

# Comment out or remove the left_column code block if not needed
# left_column, right_column = st.columns(2)
# with left_column:
#     # This block was responsible for displaying and editing prompts
#     # Now commented out to make prompts not visible while remaining active

right_column = st.columns(1)[0]  # Adjusted to use only one column

form = st.form(key='my_form')
user_question = form.text_area(label='Enter your question')
submit_button = form.form_submit_button(label='Submit')

if submit_button:
    with right_column:
        ans_dict = get_answer_from_api(user_question, "gpt-4o")
        # st.write("Raw API response:", ans_dict)  # Debug: Print raw response
        
        if not ans_dict:
            st.error("Received an empty response from the API.")
        else:
            try:
                ans_dict = json.loads(ans_dict)
                st.success("Answer : \n\n  " + ans_dict.get('answer', 'No answer provided'))
                st.success("Reasoning : \n\n  " + ans_dict.get('reasoning', 'No reasoning provided'))
                st.info("Context : \n\n  " + ans_dict.get('context', 'No context provided'))
                st.warning("Reference case name : \n\n " + ans_dict.get('case_name', 'No case name provided'))
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON: {e}")
                st.error(f"Raw response: {ans_dict}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error(f"Raw response: {ans_dict}")

