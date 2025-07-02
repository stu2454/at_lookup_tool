import os
import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from io import BytesIO
from docx import Document
import re

# Page configuration
st.set_page_config(
    page_title="AT Support Item Market Analysis",
    layout="wide"
)

# Global CSS for readability
st.markdown(
    """
    <style>
    html, body, [class*="css"], .block-container {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    .stTextInput label, .stSelectbox label {
        font-size: 22px !important;
    }
    .stTabs [role="tab"] {
        font-size: 22px !important;
        padding: 0.75rem 1.5rem !important;
    }
    .block-container {
        padding: 3rem 5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
if not api_key:
    st.error("Missing OPENAI_API_KEY in .env")
    st.stop()
client = OpenAI(api_key=api_key, project=project_id)

# App title
st.title("Assistive Tech Market Analysis (NDIS)")

# Load default support-items document from /data
default_path = os.path.join("data", "support_items.docx")
if os.path.exists(default_path):
    with open(default_path, 'rb') as f:
        sf = BytesIO(f.read())
    sf.name = os.path.basename(default_path)
    support_file = sf
else:
    st.error(f"Default document not found at {default_path}")
    st.stop()

# Sidebar input for Support Item Ref No.
st.sidebar.header("Enter Reference")
ref_no = st.sidebar.text_input("Support Item Ref No.")
if not ref_no:
    st.sidebar.info("Please enter a Ref No. to begin.")
    st.stop()

# Helper to load DataFrame
def load_df(file):
    if file.name.endswith(('xlsx','xls')):
        return pd.read_excel(file)
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    if file.name.endswith('.docx'):
        doc = Document(BytesIO(file.read()))
        dfs = []
        for tbl in doc.tables:
            cols = [c.text.strip() for c in tbl.rows[0].cells]
            if 'Support Item Ref No.' in cols and 'Description' in cols:
                rows = [dict(zip(cols, [cell.text.strip() for cell in row.cells]))
                        for row in tbl.rows[1:]]
                dfs.append(pd.DataFrame(rows))
        if dfs:
            return pd.concat(dfs, ignore_index=True)
    return None

# Main logic
try:
    df = load_df(support_file)
    if df is None:
        raise ValueError("Could not parse default document. Check format.")
except Exception as e:
    st.error(f"Error loading document: {e}")
    st.stop()

df.columns = [c.strip() for c in df.columns]
match = df[df['Support Item Ref No.'].astype(str) == ref_no.strip()]
if match.empty:
    st.error(f"Ref No. '{ref_no}' not found in default document.")
    st.stop()

description = match.iloc[0]['Description']
st.subheader("Support Item Description")
st.info(description)

# Build prompts
system_prompt = (
    "You are an allied health clinician with extensive experience in assessment and prescription of assistive technology funded through the National Disability Insurance Scheme (NDIS) for people living with disability. "
    "I will provide a concise description of a support-item category. Your task is to:\n"
    "1. Interpret the core function, clinical need and key use-cases for NDIS-funded participants.\n"
    "2. Identify the full range of device types and form factors available or emerging.\n"
    "3. For each device type, list typical feature sets, price bands in AUD, leading brands/models and regulatory considerations.\n"
    "4. Highlight any innovative or forward-looking technologies.\n"
    "5. Critically question assumptions and adjacent solutions.\n"
    "6. Suggest three authoritative sources for NDIS pricing and specifications.\n"
    "Present as six distinct sections labelled 1 to 6."
)
user_prompt = f"Description: '{description}'"

# Call LLM
data = None
with st.spinner("Generating market analysis..."):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        report = response.choices[0].message.content
    except Exception as e:
        st.error(f"API error: {e}")
        st.stop()

# Extract sections by number
positions = {i: report.find(f"{i}.") for i in range(1,7)}
sections = []
for i in range(1,7):
    start = positions[i]
    if start == -1:
        sections.append(f"No content returned for section {i}.")
        continue
    next_starts = [pos for num,pos in positions.items() if num>i and pos!=-1]
    end = min(next_starts) if next_starts else len(report)
    content = report[start + len(f"{i}."): end]
    sections.append(content.strip())

# Tab labels and rendering
tab_labels = [
    "1. Core Function & Need",
    "2. Device Types & Forms",
    "3. Features, Pricing & Brands",
    "4. Innovations",
    "5. Critical Questions",
    "6. Authoritative Sources"
]
tabs = st.tabs(tab_labels)
for tab, content in zip(tabs, sections):
    with tab:
        st.write(content)

