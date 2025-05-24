import os
import streamlit as st

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

from mental_health_screening import (
    PHQ9_QUESTIONS, GAD7_QUESTIONS, RESPONSE_OPTIONS,
    calculate_phq9_score, calculate_gad7_score
)
from mood_tracking import log_mood

# ---- THIS MUST BE THE FIRST STREAMLIT COMMAND ----
st.set_page_config(page_title="MediBot: Medical Q&A Chatbot", page_icon="🩺")

# --- Custom CSS for modern look ---
st.markdown(
    """
    <style>
    .stButton>button {
        border-radius: 20px;
        box-shadow: 1px 1px 4px #e0e0e0;
        font-size: 1.1em;
    }
    .stRadio>div {
        background: #f0f4ff;
        border-radius: 15px;
        padding: 10px;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    .sidebar-title {
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DB_FAISS_PATH = "vectorstore/db_faiss"

@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    return db

def set_custom_prompt(custom_prompt_template):
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])
    return prompt

def load_llm(huggingface_repo_id, HF_TOKEN):
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.5,
        max_new_tokens=512,
        huggingfacehub_api_token=HF_TOKEN
    )
    return llm

def run_screening(questions, screening_name):
    st.markdown(f"## {screening_name} Screening")
    responses = []
    for idx, question in enumerate(questions):
        response = st.radio(
            f"{idx+1}. {question}",
            [opt[0] for opt in RESPONSE_OPTIONS],
            key=f"{screening_name}_{idx}"
        )
        score = dict(RESPONSE_OPTIONS)[response]
        responses.append(score)
    return responses

def main():
    st.markdown("# 🩺 MediBot: Medical Q&A Chatbot")

    # --- Sidebar Layout ---
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🧠 Mental Health Tools</div>', unsafe_allow_html=True)
        mental_tool = st.radio(
            "Choose a screening:",
            ["None", "PHQ-9 (Depression Screening)", "GAD-7 (Anxiety Screening)"],
            key="mental_tool"
        )
        with st.expander("ℹ️ About Screenings"):
            st.write(
                "These tools help you understand your mental health. "
                "Your answers are private and not stored."
            )

        st.markdown("---")
        st.markdown('<div class="sidebar-title">😊 Mood Tracker</div>', unsafe_allow_html=True)
        mood_tracker_selected = st.checkbox("Open Mood Tracker", key="mood_tracker")
        with st.expander("Why track your mood?"):
            st.write(
                "Tracking your mood helps you spot patterns and triggers, empowering self-care."
            )

        st.markdown("---")
        st.markdown(
            "<center><small>Made with ❤️ for your well-being</small></center>",
            unsafe_allow_html=True
        )

    # --- Main Area Logic ---
    if mood_tracker_selected:
        log_mood()
        st.stop()

    if mental_tool == "PHQ-9 (Depression Screening)":
        responses = run_screening(PHQ9_QUESTIONS, "PHQ-9")
        if st.button("Submit PHQ-9"):
            score, severity = calculate_phq9_score(responses)
            st.success(f"Your PHQ-9 Score: {score} ({severity})")
            if responses[8] >= 1:
                st.error(
                    "If you are having thoughts of self-harm, please seek help immediately: "
                    "https://www.opencounseling.com/suicide-hotlines"
                )
            st.info("For more mental health resources, visit: https://www.mentalhealth.gov/get-help")
        st.stop()

    elif mental_tool == "GAD-7 (Anxiety Screening)":
        responses = run_screening(GAD7_QUESTIONS, "GAD-7")
        if st.button("Submit GAD-7"):
            score, severity = calculate_gad7_score(responses)
            st.success(f"Your GAD-7 Score: {score} ({severity})")
            st.info("For more mental health resources, visit: https://adaa.org/find-help")
        st.stop()

    # --- Default: Medical Chatbot ---
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        st.session_state.messages.append({
            'role': 'assistant',
            'content': "👋 Hello! I'm **MediBot**. Ask me any medical question based on my knowledge base."
        })

    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.chat_message('user').markdown(f"**You:** {message['content']}")
        else:
            st.chat_message('assistant').markdown(f"**MediBot:** {message['content']}")

    prompt = st.chat_input("Type your medical question here...")

    if prompt:
        st.chat_message('user').markdown(f"**You:** {prompt}")
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        CUSTOM_PROMPT_TEMPLATE = """
        Use the pieces of information provided in the context to answer user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        Don't provide anything out of the given context.

        Context: {context}
        Question: {question}

        Start the answer directly. No small talk please.
        """

        HUGGINGFACE_REPO_ID = "mistralai/Mistral-7B-Instruct-v0.3"
        HF_TOKEN = os.environ.get("HF_TOKEN")
        if not HF_TOKEN:
            st.error("HuggingFace API token not found. Please set HF_TOKEN in your environment or .env file.")
            return

        try:
            vectorstore = get_vectorstore()
            if vectorstore is None:
                st.error("Failed to load the vector store")
                return

            qa_chain = RetrievalQA.from_chain_type(
                llm=load_llm(huggingface_repo_id=HUGGINGFACE_REPO_ID, HF_TOKEN=HF_TOKEN),
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
                return_source_documents=True,
                chain_type_kwargs={'prompt': set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
            )

            response = qa_chain.invoke({'query': prompt})

            result = response["result"]
            st.chat_message('assistant').markdown(f"**MediBot:** {result}")
            st.session_state.messages.append({'role': 'assistant', 'content': result})

        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
