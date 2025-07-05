---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Self Building Ai Functions for self_building_ai_functions.md
title: Self Building Ai Functions
updated_at: '2025-07-04'
version: 1.0.0
---

# Self-Building AI: Core Functions & Usage Guide

## 1. Error Detection & AI-Powered Fix Suggestions

### Overview
Detect code errors and suggest fixes using either:
- Internal AI processing (local models, e.g., transformers, CodeBERT, etc.)
- Optional: OpenAI/ChatGPT or alternative AI APIs (configurable)

### Example Python Script
```python
# self_building_ai/error_fixer.py
import os as import openai
from dotenv import load_dotenv

# Optional: Import internal AI model (pseudo-code)
# from internal_ai import suggest_fix_internal as load_dotenv()

USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() == "true"
openai.api_key = os.getenv("OPENAI_API_KEY")

ERROR_LOG = "./private/logs/error.log"
CODE_FILE = "./private/code/main.py"

# Example stub for internal AI (replace with actual model integration):
def suggest_fix_internal(error_message):
    return f"[Internal AI] Suggested fix for: {error_message}"

def analyze_logs():
    if os.path.exists(ERROR_LOG):
        with open(ERROR_LOG, "r") as f:
            logs = f.readlines()
            return [log.strip() for log in logs if "ERROR" in log]
    return []:
:
def generate_fix(error_message):
    if USE_OPENAI:
        prompt = f"Fix the following error: {error_message}"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    else:
        return suggest_fix_internal(error_message)

def apply_fix(file_path, fix_message):
    with open(file_path, "a") as f:
        f.write("\n# Fix applied:\n")
        f.write(fix_message + "\n")

def self_iterate():
    errors = analyze_logs()
    if errors:
        for error in errors:
            print(f"Found error: {error}")
            fix = generate_fix(error)
            print(f"Suggested fix: {fix}")
            apply_fix(CODE_FILE, fix)
    else:
        print("No errors found. System is up to date.")

if __name__ == "__main__":
    self_iterate()
``````python
# self_building_ai/streamlit_app.py
import streamlit as st
import openai
from dotenv import load_dotenv
import os
import streamlit.components.v1 as components

load_dotenv()
USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() == "true"
openai.api_key = os.getenv("OPENAI_API_KEY")

def suggest_fix_internal(error_message):
    return f"[Internal AI] Suggested fix for: {error_message}"

st.title("Self-Building AI Interface")
st.sidebar.header("Navigation")
options = ["Home", "Code Fixer", "Preview"]
choice = st.sidebar.selectbox("Choose a feature", options)

if choice == "Home":
    st.write("Welcome to the Self-Building AI Interface!")
    st.write("Use the sidebar to navigate.")
elif choice == "Code Fixer":
    st.header("Code Fixer")
    user_input = st.text_area("Enter the error message here:")
    if st.button("Fix Error"):
        if user_input:
            if USE_OPENAI:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"Fix the following error: {user_input}",
                    max_tokens=100
                )
                fix = response.choices[0].text.strip()
            else:
                fix = suggest_fix_internal(user_input)
            st.write("Suggested Fix:")
            st.code(fix)
        else:
            st.warning("Please enter an error message.")
elif choice == "Preview":
    st.header("Preview Area")
    html_code = st.text_area("Enter HTML/CSS code to preview:")
    if st.button("Render Preview"):
        components.html(html_code, height=400)
``````python
# NOTE: The following code had issues and was commented out
#   pip install openai streamlit python-dotenv
#   ``````python
OPENAI_API_KEY=your_openai_api_key
USE_OPENAI=true  # or false for internal AI:
```