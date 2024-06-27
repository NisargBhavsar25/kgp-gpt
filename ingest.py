import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma

embeddings = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

loader = DirectoryLoader('data/', glob="**/*.txt", show_progress=True, loader_cls=TextLoader, use_multithreading=True)
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=1000)
texts = text_splitter.split_documents(documents)

vector_store = Chroma.from_documents(texts, embeddings, collection_metadata={"hnsw:space": "cosine"}, persist_directory="stores/fundae")

print("Vector DB Successfully Created!")