import streamlit as st
from helpers.watsonx_helper import generate_suggestion

st.title("💬 AI Code Assistant (Granite 13B)")

code_input = st.text_area("Enter your code or question:", height=300)

if st.button("Ask Watsonx"):
    if code_input.strip():
        with st.spinner("Generating response from Granite..."):
            response = generate_suggestion(code_input)
        # response is a string, so no key indexing
        st.code(response, language='python')
    else:
        st.warning("Please enter a prompt or code snippet.")
