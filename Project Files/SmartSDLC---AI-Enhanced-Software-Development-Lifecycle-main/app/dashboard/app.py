import streamlit as st
from code_review.review_api import review_code

st.title("🔍 SmartSDLC - Code Review Assistant")
code_input = st.text_area("Paste your code here:")

if st.button("Analyze Code"):
    with st.spinner("Analyzing..."):
        review = review_code(code_input)
        st.success("Analysis complete!")
        st.write(review)