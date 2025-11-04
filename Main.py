from bs4 import BeautifulSoup
import os
import numpy as np
import openai
from transformers import GPT2TokenizerFast
import json
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
import weaviate
from openai import OpenAI

# ---------------------------- All cofig ----------------------------
load_dotenv()  # Load the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
WEAVIATE_API = os.getenv("WEAVIATE_API")
EMBEDDING_MODEL = "text-embedding-ada-002"
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
model = "gpt-4o"

client = weaviate.Client(
# client = WeaviateClient(
    url="http://localhost:8080",  # test1
    # url=WEAVIATE_API,  # test2
)

prompts_folder = os.path.join(os.getcwd(), "prompts")

meta = client.schema.get()
print(meta)

class Query(BaseModel):
    user_question: str
    user_model: str
    user_auth: str

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------- All functions ----------------------------

def process_answer(model, messages):
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.3,
            presence_penalty=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in process_answer: {str(e)}")
        return "Error generating answer"

def process_reasoning(model, reasoning):
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=reasoning,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.3,
            presence_penalty=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in process_reasoning: {str(e)}")
        return "Error generating reasoning"

def return_answer_and_context_for_queries(user_question, model):
    try:
        filtered_user_question = user_question.replace('"', "'")

        result = (
            client.query
            .get("AI_v1", ["data", "case_name", "_additional {score} "])
            .with_hybrid(filtered_user_question)
            .do()
        )

        if 'data' not in result or 'Get' not in result['data'] or 'AI_v1' not in result['data']['Get']:
            raise ValueError("Unexpected response structure from Weaviate")

        ai_v1 = result['data']['Get']['AI_v1']

        if not ai_v1:
            return "No relevant information found", "", "No reasoning available", "No case name"

        highest_score = max(ai_v1, key=lambda x: float(x['_additional']['score']))
        case_name = highest_score['case_name']
        data = highest_score['data']

        with open(os.path.join(prompts_folder, 'prompt.txt'), 'r') as f:
            API_prompt_text = f.read()
        with open(os.path.join(prompts_folder, 'reasoning_prompt.txt'), 'r') as f:
            API_reasoning_prompt_text = f.read()

        ans_header = API_prompt_text
        reasoning_header = API_reasoning_prompt_text

        ans_prompt = "Questions: " + user_question + "\n\n" + data.replace('\n', ' ')

        messages = [
            {"role": "system", "content": ans_header if ans_header else "You are a helpful assistant"},
            {"role": "user", "content": ans_prompt}
        ]

        answer = process_answer(model, messages)

        reasoning_prompt = "Questions: " + user_question + "\n\nAnswer: " + answer.replace('\n', ' ') + "\nContext: " + data.replace('\n', ' ')

        reasoning_messages = [
            {"role": "system", "content": reasoning_header if reasoning_header else "You are a helpful assistant"},
            {"role": "user", "content": reasoning_prompt}
        ]

        reasoning = process_reasoning(model, reasoning_messages)

        return answer, data, reasoning, case_name

    except openai.Error as e:
        return "An error occurred: " + str(e), "error", "error", "error"


    except Exception as e:
        print(f"Error in return_answer_and_context_for_queries: {str(e)}")
        return str(e), "", "", ""

    except Exception as e:
        print(f"Error in return_answer_and_context_for_queries: {str(e)}")
        return str(e), "", "", ""

# ---------------------------- All routes ----------------------------

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "This is v1 on weaviate API"}

@app.post("/generate_answers/")
async def generate_answers(payload: dict):
    """
    THis API is used to generate answers for the user question.
    args:
        * payload: The payload is a dictionary containing the user question.search
        ** user_question: The user question is a string, which is the question asked by the user.
        ** user_auth: The user auth is a string, which is the auth code to access the API.
    """
    if 'user_question' not in payload:
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_question' not found."
        )
    elif not isinstance(payload['user_question'], str):
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_question' should be a string."
        )
    elif len(payload['user_question']) == 0:
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_question' should not be empty."
        )
    elif 'user_model' not in payload:
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_model' not found."
        )
    elif not isinstance(payload['user_model'], str):
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_model' should be a string."
        )
    elif len(payload['user_model']) == 0:
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_question' should not be empty."
        )
    elif 'user_auth' not in payload:
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_auth' not found."
        )
    elif not isinstance(payload['user_auth'], str):
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_auth' should be a string."
        )
    elif len(payload['user_auth']) == 0:
        raise HTTPException(
            status_code=400,
            detail="Parameter 'user_auth' should not be empty."
        )

    # Set the user question
    user_question = payload['user_question']
    model = payload['user_model']
    user_auth = payload['user_auth']

    if user_auth != "ntel101919":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    
    try:
        ans, context, reasoning, case_name = return_answer_and_context_for_queries(
            user_question,
            model
        )
        return {
            "answer": ans,
            "context": context,
            "reasoning": reasoning,
            "case_name": case_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
