import glob
import pandas as pd
import textwrap
import numpy as np
import streamlit as st
import re
import openai
import time
import pdfplumber
import json
import os
import weaviate
from io import StringIO
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tqdm import tqdm
from scipy.spatial.distance import cosine
from transformers import GPT2TokenizerFast

st.set_page_config(
    layout="wide",
    page_title="AI v1-Weaviate",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

# ---------------------------- All cofig ----------------------------
load_dotenv()  # Load the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
weaviate_API = os.getenv("WEAVIATE_API")
openai_api_key = os.getenv("OPENAI_API_KEY")
COMPLETIONS_MODEL = "text-davinci-003"
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
EMBEDDING_MODEL = "text-embedding-ada-002"

# All configs and settings
client = weaviate.Client(
    url=weaviate_API,
    # Or "X-Cohere-Api-Key" or "X-HuggingFace-Api-Key"
    additional_headers={"X-OpenAI-Api-Key": openai_api_key}
)

# create index_files directory if not exists

INDEX_FILE_PATH = 'final_data.json'

# ---------------------------------- ALL Helper functions ----------------------------------

# Get embedding for a text


def get_embedding(text, model):
    result = openai.Embedding.create(
        model=model,
        input=text
    )
    return result["data"][0]["embedding"]

# Get similarity between two vectors


def vector_similarity(x, y):
    """
    Returns the similarity between two vectors.

    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))


def clean_html(text):
    soup = BeautifulSoup(text, features='lxml')
    return soup.get_text("\n")


def read_clean_text(text_path):
    with open(text_path, 'r', encoding='utf-8') as f:
        texts = f.read()
    # the first line of text is the case name
    case_name = texts.splitlines()[0]
    # remove first 56 lines
    texts = texts.splitlines()[56:]
    texts = "\n".join(texts)
    textsx = texts.split("I certify")
    texts = textsx[0]
    return texts, case_name


def index_textfiles_main(raw_text, file_name):

    st.info(f"Generating embedding for context of file name: {file_name}")

    case_name = raw_text.splitlines()[0]
    # remove first 56 lines
    raw_text = raw_text.splitlines()[56:]
    raw_text = "\n".join(raw_text)
    raw_text = raw_text.split("I certify")
    raw_text = raw_text[0]

    # Remove all lines which start with (cid:
    text = re.sub(r'\(cid:[0-9]+\)', '', raw_text)

    # Remove all lines containing consecutive dots
    text = re.sub(r'\.*\.*', '', text)

    # Remove all new line characters
    text = re.sub(r'\n', '', text)

    # Remove all extra spaces between words
    text = re.sub(r' +', ' ', text)

    # Remove all remaining consecutive spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove leading and trailing spaces
    text = text.strip()

    total_tokenized = 0
    total_character_count = 0
    data_ids = []
    token_limit = 6000

    with client.batch as batch:
        batch.batch_size = token_limit
        tokens = tokenizer.tokenize(text)
        chunks = [
            tokens[i:i + token_limit] for i in range(0, len(tokens), token_limit)
        ]

        for chunk in chunks:
            chunk_text = tokenizer.convert_tokens_to_string(chunk)

            tokenized_chunk = len(chunk)
            total_tokenized += tokenized_chunk

            character_count = len(chunk_text)
            total_character_count += character_count

            file_data = {
                'data': chunk_text,
                'case_name': case_name
            }

            properties = {
                "data":  f"(case_name: {file_data['case_name']}) " + file_data["data"],
                "case_name": file_data["case_name"]
            }

            try:
                res = client.batch.add_data_object(properties, "AI_v1")
                # data_ids.append(str(res))
            except openai.Error as e:
                print(f"An error occurred: {e}")

    st.success("File uploaded successfully")


def parse_pdf(feed):
    print("went to parse pdf")
    # Read the pdf file
    # pdf = pdfplumber.open(pdf_file_path)
    with pdfplumber.open(feed) as pdf:
        # Extract all pages text
        pages = pdf.pages

    # Extract all text from all pages
    text = ""

    for page in pages:
        text += page.extract_text()

    print(text)

    # Remove all lines which startes with (cid:
    text = re.sub(r'\(cid:[0-9]+\)', '', text)

    # remove all extra space between words, but dont touch the new line caharcter
    text = re.sub(r' +', ' ', text)

    # replace " \n" with "\n"
    text = re.sub(r' \n', '\n', text)

    # Remove all extra new line characters
    text = re.sub(r'\n+', '\n', text)

    text = text.strip()

    # case_name is 2nd line of the text
    case_name = text.split('\n')[1]

    chunks = textwrap.wrap(text, 2500)

    for chunk in chunks:
        # first check if index_files/index.json exists
        if os.path.exists(INDEX_FILE_PATH):
            with open(INDEX_FILE_PATH, 'r') as infile:
                result = json.load(infile)
        else:
            result = dict()

        # Check if the chunk is already in index.json
        if chunk in result:
            st.info(" -> Chunk already in index.json, skipping embedding generation")
        else:
            st.info("     -> Generating embedding for chunk")
            # get embedding using gpt3_embedding function
            embedding = get_embedding(chunk.encode(
                encoding='ASCII', errors='ignore').decode(), EMBEDDING_MODEL)

            # create a dictionary with content as key and embedding, case_name as a sub dictionary
            result[chunk] = {'embedding': embedding, 'case_name': case_name}

            # save the dictionary to index.json file
            with open(INDEX_FILE_PATH, 'w') as outfile:
                json.dump(result, outfile, indent=2)

            time.sleep(5)

    st.success(f"Completed embedding for contexts of uploaded file name\n")


# ============================================================================================================================================
# ----------------------------------------------------------------- UI ---------------------------------------------------------------------#

left_column, right_column = st.columns(2)

with left_column:
    # st.info("Upload the cases data in .txt/.pdf/.html format")
    # st.info("Upload the cases data in .txt format")

    # uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "html"])
    uploaded_file = st.file_uploader("Choose a file", type="txt")

    if uploaded_file is not None:
        st.write("File name: ", uploaded_file.name)
        st.write("File type: ", uploaded_file.type)
        st.write("File size: ", uploaded_file.size)

        if uploaded_file.type == "text/plain":
            # To convert to a string based IO:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

            # To read file as string:
            string_data = stringio.readlines()

            string_data = "\n".join(string_data)

            # st.write("File content: ", string_data)
            with right_column:
                index_textfiles_main(string_data, uploaded_file.name)
        else:
            st.error("Invaid file not supported.")

        # if (uploaded_file.type == "image/pdf") or (uploaded_file.type == "application/pdf"):
        #     parse_pdf(feed=uploaded_file)
        # elif uploaded_file.type == "text/plain":
        #     # To convert to a string based IO:
        #     stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

        #     # To read file as string:
        #     string_data = stringio.readlines()

        #     string_data = "\n".join(string_data)

        #     # st.write("File content: ", string_data)

        #     index_textfiles_main(string_data, uploaded_file.name)
        # elif uploaded_file.type == "text/html":
        #     # To convert to a string based IO:
        #     stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

        #     # To read file as string:
        #     string_data = stringio.read()

        #     text = clean_html(string_data)
        #     text = text.strip()
        #     text = text.strip()
        #     # st.info(text)
        #     index_textfiles_main(text, uploaded_file.name)
