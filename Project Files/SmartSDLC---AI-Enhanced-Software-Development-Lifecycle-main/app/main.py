import streamlit as st
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Sidebar to select module, AI Assistant last
selected_module = st.sidebar.selectbox(
    "📌 Choose Module",
    ["Code Review", "Auto Documentation", "Bug Detection", "AI Code Assistant (Granite 13B)"]
)

if selected_module == "Code Review":
    st.title("🧠 SmartSDLC: AI Code Review Assistant")
    from code_review.code_review import analyze_code

    uploaded_file = st.file_uploader("Upload a Python (.py) file", type=["py"], key="code_review_uploader")
    if uploaded_file:
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.info("✅ File uploaded successfully! Analyzing...")
        results = analyze_code(file_path)
        for issue in results:
            if "error" in issue:
                st.error(issue["error"])
            else:
                severity_color = {
                    "High": "🔴",
                    "Medium": "🟡",
                    "Low": "🟢"
                }
                with st.expander(f"{severity_color[issue['severity']]} Line {issue['line']}: {issue['code']}"):
                    st.write(f"**Issue Type:** `{issue['label']}`")
                    st.write(f"**Confidence:** `{issue['confidence']}`")
                    st.write(f"**Severity:** `{issue['severity']}`")
                    st.caption(f"Checked On: {issue['timestamp']}")

elif selected_module == "Auto Documentation":
    st.title("📝 SmartSDLC: Auto Documentation Generator")
    from doc_generator.doc_generator import generate_doc

    uploaded_file = st.file_uploader("Upload a Python (.py) file", type=["py"], key="auto_doc_uploader")
    if uploaded_file:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success("✅ File uploaded successfully! Generating docs...")

        docs = generate_doc(file_path)

        for doc in docs:
            with st.expander(f"{doc['type']} `{doc['name']}` (Line {doc['line']})"):
                st.write(f"**Summary:** {doc['summary']}")
                st.caption(f"Generated on: {doc['timestamp']}")

        st.success("📄 Documentation generated successfully!")

        md_content = "# Generated Documentation\n\n"
        for doc in docs:
            md_content += f"### {doc['type']} `{doc['name']}` (Line {doc['line']})\n"
            md_content += f"**Summary:** {doc['summary']}\n\n"
            md_content += f"*Generated on: {doc['timestamp']}*\n\n"

        st.download_button(
            label="📥 Download Documentation as Markdown",
            data=md_content,
            file_name=f"{uploaded_file.name}_documentation.md",
            mime="text/markdown"
        )

elif selected_module == "Bug Detection":
    st.title("🐞 SmartSDLC: Early Bug Detection")
    from bug_detector.bug_detector import predict_bug


    code_input = st.text_area("Paste a code snippet to analyze", height=300)
    if st.button("Detect Bugs", key="detect_bugs_button"):
        if code_input.strip() != "":
            result = predict_bug(code_input)

            if "error" in result:
                st.error(result["error"])
            else:
                if result["is_buggy"]:
                    st.error(f"⚠️ Buggy code detected! (Confidence: {result['probability']})")
                    st.write(f"💡 Suggestion: {result['suggestion']}")
                else:
                    st.success(f"✅ Clean code! (Confidence: {result['probability']})")
                    st.write("🚀 No issues found.")
                st.caption(f"Analyzed on: {result['timestamp']}")
        else:
            st.warning("Please paste some code.")

elif selected_module == "AI Code Assistant (Granite 13B)":
    st.title("💬 AI Code Assistant (Granite 13B)")
    from helpers.watsonx_helper import generate_suggestion
    code_input = st.text_area("Enter your code or question:", height=300)
    if st.button("Ask Watsonx", key="ask_watsonx_button"):
        if code_input.strip():
            with st.spinner("Generating response from Granite..."):
                response = generate_suggestion(code_input)
            st.code(response, language='python')
        else:
            st.warning("Please enter a prompt or code snippet.")
