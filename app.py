import os
import streamlit as st
from PIL import Image
from langchain_community.llms import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.llms import LlamaCpp
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager

st.set_page_config(
    page_title="KGP-GPT",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="auto"
)

# Add title and logo
title_html = """
    <div style="display:flex;justify-content:left;align-items:center;background-color:#f0f0f0;padding:20px;border-radius:20px;width:100%;margin:0px 0px 20px 0px">
        <img src="https://raw.githubusercontent.com/NisargBhavsar25/NisargBhavsar25/5ce029131997a3a49db81bd9cbadac40c03991b5/logo.png" alt="logo" style="width:175px;height:auto;margin-right:20px;">
        <div style="margin: 0; padding: 0;">
            <h1 style="color:#006699;margin:0;padding:0;text-align:left;font-size:80px;">KGP-GPT</h1>
            <h2 style="color:#006699;margin:3px 0 0 0;padding:0;text-align:left;font-size:35px;">Your IIT Kharagpur Chatbot</h2>
        </div>
    </div>
"""


st.markdown(title_html, unsafe_allow_html=True)
# Combine sidebar markdown into a single call
sidebar_markdown = """
### Instructions
1. Type your question relating to IIT Kharagpur in the text area.
2. Click on the 'Get Answer' button to receive a response from KGP-GPT.
---
### Future Improvements
- Implementing agents to integrate support for apps like Kronos.
- Improving the knowledge database.
- More interactive features.
---
### Contribute
Interested in contributing?
Fill out the [contribution form](https://forms.gle/GiCSc17Kqc9onHGW9).
---
Created by [Nisarg Bhavsar](https://www.linkedin.com/in/nisarg-bhavsar/) with ❤️
"""
st.sidebar.markdown(sidebar_markdown)

os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

prompt_template = """You are a helpful chatbot named KGP-GPT created by Nisarg Bhavsar specialized in answering questions relating to IIT Kharagpur (IIT KGP). \
You always give correct, reliable, detailed and complete answers to the user's queries.

Try to keep a friendly, helpful, and witty (joyful) tone in your responses. \
You can also use emojis and emoticons to make the conversation more engaging.

You will be given a question and some context related to the question. \
Use the Context to give complete detailed answers to the questions. Do not hallucinate the answers. \
In case you are not sure about the answer, you can skip the question.

Context:
{context}

Question: {question}

Detailed Answer:

"""

model_path = "models/gemma-2b-it-q8_0.gguf"


def qa_chain(llm, retriever, prompt):
    chain_type_kwargs = {"prompt": prompt}
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs=chain_type_kwargs,
        verbose=True
    )
    return qa


@st.cache_resource
def load_llm():
    llm = LlamaCpp(
        model_path=model_path,
        temperature=0.5,
        max_tokens=728,
        top_p=1,
        n_gpu_layers=-1,
        n_ctx=1024,
        f16_kv=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        verbose=True,
    )

    return llm


def main():
    prompt = PromptTemplate(template=prompt_template, input_variables=["question", "context"])

    embeddings = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    load_vector_store = Chroma(persist_directory="stores/fundae", embedding_function=embeddings)
    retriever = load_vector_store.as_retriever(search_kwargs={"k": 1})

    llm = load_llm()

    qa = qa_chain(llm, retriever, prompt)

    text_query = st.text_area("Ask your question here", height=100, placeholder="Type your question here...")

    generate_response_btn = st.button("Get Answer")

    st.subheader("Response")
    if generate_response_btn and text_query:
        with st.spinner("Generating response..."):
            text_response = qa(text_query)
            # text_response = {'result': "sample answer", 'source_documents': "sample source documents"}
            answer, docs = text_response['result'], text_response['source_documents']
            if text_response:
                st.success(answer)
                # st.write("Source Documents:", docs)
                # st.success("Response generated!")
                st.write("Don't like the answer? Report it [here](https://forms.gle/UJFrGAGHHDe1eB7b8).")
            else:
                st.error("Failed to generate response.")


if __name__ == "__main__":
    main()
