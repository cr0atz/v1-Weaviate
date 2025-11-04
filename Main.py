from bs4 import BeautifulSoup
import os
import numpy as np
import openai
from transformers import GPT2TokenizerFast
import json
from fastapi import FastAPI, Body, HTTPException, Header, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
import weaviate
from openai import OpenAI

# ---------------------------- All cofig ----------------------------
load_dotenv()  # Load the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
WEAVIATE_API = os.getenv("WEAVIATE_API")
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")  # Information: Read auth token from environment
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

        # Information: Query Weaviate with new schema properties for richer context
        result = (
            client.query
            .get("AI_v1", [
                "data", 
                "case_name", 
                "citation", 
                "court", 
                "jurisdiction", 
                "decision_date",
                "paragraph_refs",
                "_additional {score}"
            ])
            .with_hybrid(filtered_user_question)
            .with_limit(5)  # Information: Get top 5 results for better context
            .do()
        )

        if 'data' not in result or 'Get' not in result['data'] or 'AI_v1' not in result['data']['Get']:
            raise ValueError("Unexpected response structure from Weaviate")

        ai_v1 = result['data']['Get']['AI_v1']

        if not ai_v1:
            return "No relevant information found", "", "No reasoning available", "No case name"

        # Information: Get highest scoring result
        highest_score = max(ai_v1, key=lambda x: float(x['_additional']['score']))
        case_name = highest_score['case_name']
        citation = highest_score.get('citation', '')
        court = highest_score.get('court', '')
        jurisdiction = highest_score.get('jurisdiction', '')
        decision_date = highest_score.get('decision_date', '')
        data = highest_score['data']
        
        # Information: Build enriched case reference for LLM context
        case_reference = f"{case_name}"
        if citation:
            case_reference += f" {citation}"
        if court:
            case_reference += f" ({court})"

        with open(os.path.join(prompts_folder, 'prompt.txt'), 'r') as f:
            API_prompt_text = f.read()
        with open(os.path.join(prompts_folder, 'reasoning_prompt.txt'), 'r') as f:
            API_reasoning_prompt_text = f.read()

        ans_header = API_prompt_text
        reasoning_header = API_reasoning_prompt_text

        # Information: Include case reference in prompt for proper citation
        ans_prompt = f"Questions: {user_question}\n\nCase: {case_reference}\n\nContext: {data.replace('\n', ' ')}"

        messages = [
            {"role": "system", "content": ans_header if ans_header else "You are a helpful assistant"},
            {"role": "user", "content": ans_prompt}
        ]

        answer = process_answer(model, messages)

        # Information: Include case reference in reasoning prompt as well
        reasoning_prompt = f"Questions: {user_question}\n\nCase: {case_reference}\n\nAnswer: {answer.replace('\n', ' ')}\n\nContext: {data.replace('\n', ' ')}"

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

# Information: Auth validation function
def validate_auth(x_api_key: str = None, payload_auth: str = None) -> bool:
    """
    Validate API key from header (preferred) or payload (backward compatible).
    
    Args:
        x_api_key: API key from X-API-Key header
        payload_auth: API key from payload user_auth field
    
    Returns:
        bool: True if valid
    
    Raises:
        HTTPException: If API key is invalid or missing
    """
    # Information: Check if API_AUTH_TOKEN is configured
    if not API_AUTH_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: API_AUTH_TOKEN not set"
        )
    
    # Information: Prefer header-based auth
    if x_api_key:
        if x_api_key != API_AUTH_TOKEN:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        return True
    
    # Information: Fall back to payload-based auth for backward compatibility
    if payload_auth:
        if payload_auth != API_AUTH_TOKEN:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )
        return True
    
    # Information: No auth provided
    raise HTTPException(
        status_code=401,
        detail="API key required. Provide X-API-Key header or user_auth in payload."
    )


@app.post("/generate_answers/")
async def generate_answers(
    payload: dict,
    x_api_key: str = Header(None, alias="X-API-Key")
):
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
    
    # Information: Validate API key (supports both header and payload auth)
    payload_auth = payload.get('user_auth', None)
    validate_auth(x_api_key=x_api_key, payload_auth=payload_auth)
    
    # Set the user question
    user_question = payload['user_question']
    model = payload['user_model']
    
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
