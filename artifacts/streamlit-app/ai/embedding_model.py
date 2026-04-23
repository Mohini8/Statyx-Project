import streamlit as st
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_model():

    return SentenceTransformer("intfloat/e5-base")

model = load_model()