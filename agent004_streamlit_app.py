# agent004_streamlit_app.py

import streamlit as st
import os
import tempfile
from io import StringIO
import openai
from datetime import datetime

# === Set your OpenAI API key here or via environment variable ===
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.warning("Please set your OpenAI API key in environment variable OPENAI_API_KEY or Streamlit secrets.")
    st.stop()

openai.api_key = OPENAI_API_KEY

# === Helper functions ===

def call_openai_chat(messages, model="gpt-4o-mini", temperature=0.3):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI API error: {str(e)}"

def generate_report_from_inspection(data):
    system_msg = {
        "role": "system",
        "content": "You are an expert safety inspector. Generate a concise inspection report based on the provided data."
    }
    user_msg = {
        "role": "user",
        "content": f"Generate a detailed safety inspection report from the following data:\n{data}"
    }
    return call_openai_chat([system_msg, user_msg])

def analyze_uploaded_file(file_bytes, filename):
    # For simplicity, just extract text from small text files or PDFs (basic)
    # Real implementation would require pdfminer or similar, here simplified to txt and csv
    if filename.endswith(".txt") or filename.endswith(".csv"):
        text = file_bytes.decode("utf-8")
        return text
    else:
        return "File type not supported for text extraction (only .txt or .csv)."

# === Streamlit App ===

st.set_page_config(page_title="Agent 004 Safety AI", layout="wide")

st.title("Agent 004: AI Safety Inspection Assistant")

# Sidebar navigation
pages = ["Home", "Upload Inspection Data", "Enter Inspection Details", "AI Report Generator", "Chat with Agent 004"]
page = st.sidebar.radio("Navigate", pages)

if page == "Home":
    st.markdown("""
    ## Welcome to Agent 004 Safety Inspection AI
    This app helps you:
    - Upload and analyze inspection data files (.txt, .csv)
    - Enter inspection data manually
    - Generate AI-powered safety inspection reports
    - Chat with the AI assistant about safety and inspection topics
    
    Run this app locally using your OpenAI API key.
    """)
    st.info("Make sure your OPENAI_API_KEY environment variable or Streamlit secrets are set.")

elif page == "Upload Inspection Data":
    st.header("Upload your inspection data file")
    uploaded_file = st.file_uploader("Choose a .txt or .csv file", type=["txt", "csv"])
    if uploaded_file:
        file_bytes = uploaded_file.read()
        extracted_text = analyze_uploaded_file(file_bytes, uploaded_file.name)
        st.subheader("Extracted Data Preview:")
        st.text_area("Data", extracted_text, height=300)
        if st.button("Generate AI Report from Uploaded Data"):
            with st.spinner("Generating report..."):
                report = generate_report_from_inspection(extracted_text)
                st.subheader("AI Generated Inspection Report")
                st.write(report)

elif page == "Enter Inspection Details":
    st.header("Manual Inspection Data Entry")

    inspector_name = st.text_input("Inspector Name")
    location = st.text_input("Inspection Location")
    date = st.date_input("Inspection Date", datetime.today())
    notes = st.text_area("Inspection Notes")
    hazards_found = st.text_area("Hazards Found")
    recommendations = st.text_area("Recommendations")

    if st.button("Generate AI Report from Entered Data"):
        if not inspector_name or not location:
            st.error("Please fill at least Inspector Name and Inspection Location.")
        else:
            input_data = (
                f"Inspector: {inspector_name}\n"
                f"Location: {location}\n"
                f"Date: {date}\n"
                f"Notes: {notes}\n"
                f"Hazards Found: {hazards_found}\n"
                f"Recommendations: {recommendations}"
            )
            with st.spinner("Generating report..."):
                report = generate_report_from_inspection(input_data)
                st.subheader("AI Generated Inspection Report")
                st.write(report)

elif page == "AI Report Generator":
    st.header("Generate a Safety Inspection Report from Text")

    raw_text = st.text_area("Paste your inspection text here", height=300)
    if st.button("Generate Report"):
        if not raw_text.strip():
            st.error("Please enter some text to generate a report.")
        else:
            with st.spinner("Generating report..."):
                report = generate_report_from_inspection(raw_text)
                st.subheader("AI Generated Report")
                st.write(report)

elif page == "Chat with Agent 004":
    st.header("Chat with Agent 004 - Your AI Safety Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def submit_chat():
        user_msg = st.session_state.user_input
        st.session_state.chat_history.append({"role": "user", "content": user_msg})

        messages = [{"role": "system", "content": "You are a helpful safety inspection AI assistant."}]
        messages.extend(st.session_state.chat_history)

        response = call_openai_chat(messages)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.user_input = ""

    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"**You:** {chat['content']}")
        else:
            st.markdown(f"**Agent 004:** {chat['content']}")

    st.text_input("Enter your message:", key="user_input", on_change=submit_chat)

# Footer
st.markdown("---")
st.markdown("Agent 004 - AI Safety Inspection Assistant | Built for local use with OpenAI GPT")
