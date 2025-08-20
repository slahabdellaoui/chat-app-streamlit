import os
import streamlit as st
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI

# --- Setup ---
load_dotenv()
project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT")

if not project_endpoint or not model_deployment:
    st.error("Please set the PROJECT_ENDPOINT and MODEL_DEPLOYMENT environment variables in the .env file.")
    st.stop()

project_client = AIProjectClient(
    credential=DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True
    ),
    endpoint=project_endpoint,
)
openai_client = project_client.get_openai_client(api_version="2024-10-21")

st.set_page_config(page_title="Stellar Winds Tutor Chat", page_icon="💬")
st.title("💬 Stellar Winds Tutor Chat")
st.caption("Ask anything about stellar winds of massive stars!")

# --- Chat State ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a Tutor helping graduate student to learn about stellar winds of massive stars."}
    ]

# --- Chat Display ---
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# --- Input at Bottom ---
if prompt := st.chat_input("Type your question and press Enter..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    try:
        response = openai_client.chat.completions.create(
            model=model_deployment,
            messages=st.session_state["messages"]
        )
        completion = response.choices[0].message.content
        st.session_state["messages"].append({"role": "assistant", "content": completion})
        #st.experimental_rerun()  # Rerun to show both user and assistant messages in order
    except Exception as ex:
        st.error(f"Error: {ex}")