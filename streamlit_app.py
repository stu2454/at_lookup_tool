import streamlit as st
import pandas as pd
from openai import OpenAI
from io import BytesIO
from docx import Document
import os

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

# Retrieve OpenAI credentials from Streamlit secrets
if "openai" in st.secrets:
    api_key = st.secrets["openai"].get("api_key")
    project_id = st.secrets["openai"].get("project_id", None)
else:
    api_key = st.secrets.get("OPENAI_API_KEY")
    project_id = st.secrets.get("OPENAI_PROJECT_ID")

if not api_key:
    st.error(
        "Missing OpenAI API key. In Streamlit Secrets, set either:\n\n"
        "`OPENAI_API_KEY = \"sk-...\"`\n\n"
        "or under `[openai]`:\n\n"
        "```toml\n[openai]\napi_key = \"sk-...\"\nproject_id = \"...\"\n```"
    )
    st.stop()

# Initialise OpenAI client
client = OpenAI(api_key=api_key, project=project_id)

# App title
st.title("Assistive Tech Market Analysis (NDIS)")

# Load default support-items document from /data
default_path = os.path.join("data", "support_items.docx")
if os.path.exists(default_path):
    with open(default_path, 'rb') as f:
        sf = BytesIO(f.read())
    sf.name = os.path.basename(default_path)
else:
    st.error(f"Default document not found at {default_path}")
    st.stop()

# Sidebar input
st.sidebar.header("Configuration")
ref_no = st.sidebar.text_input("Support Item Ref No.")
if not ref_no:
    st.sidebar.info("Please enter a Ref No. to begin.")
    st.stop()

# Helper to load DataFrame
def load_df(file):
    if file.name.lower().endswith(('xlsx','xls')):
        return pd.read_excel(file)
    if file.name.lower().endswith('.csv'):
        return pd.read_csv(file)
    if file.name.lower().endswith('.docx'):
        doc = Document(BytesIO(file.read()))
        tables = []
        for tbl in doc.tables:
            headers = [cell.text.strip() for cell in tbl.rows[0].cells]
            if 'Support Item Ref No.' in headers and 'Description' in headers and 'Support Item' in headers:
                rows = []
                for row in tbl.rows[1:]:
                    rows.append({
                        hdr: row.cells[idx].text.strip()
                        for idx, hdr in enumerate(headers)
                    })
                tables.append(pd.DataFrame(rows))
        if tables:
            return pd.concat(tables, ignore_index=True)
    return None

# Load and parse
try:
    df = load_df(sf)
    if df is None:
        raise ValueError("Could not parse default document. Check format.")
except Exception as e:
    st.error(f"Error loading document: {e}")
    st.stop()

# Lookup row
df.columns = [c.strip() for c in df.columns]
match = df[df['Support Item Ref No.'].astype(str) == ref_no.strip()]
if match.empty:
    st.error(f"Ref No. '{ref_no}' not found.")
    st.stop()

# Extract fields
support_item_text = match.iloc[0].get('Support Item', '').strip()
description = match.iloc[0]['Description'].strip()

st.subheader("Support Item Details")
st.markdown(f"**Support Item:** {support_item_text}")
st.info(f"**Description:** {description}")

# Build prompts
system_prompt = (
    "You are an allied health clinician with extensive experience in assessment and "
    "prescription of assistive technology funded through the NDIS for people living with disability. "
    "I will provide a concise support-item name and description. Your task:\n"
    "1. Interpret the core function, clinical need & key use-cases for NDIS participants.\n"
    "2. Identify the full range of device types & form factors available/emerging.\n"
    "3. For each device type, list feature sets, AUD price bands, brands/models & regulatory notes.\n"
    "4. Highlight innovative/forward-looking technologies.\n"
    "5. Critically question assumptions & adjacent solutions.\n"
    "6. Suggest three authoritative sources for NDIS pricing/specifications.\n"
    "Present as six distinct, numbered sections."
)
user_prompt = (
    f"Support Item: '{support_item_text}'\n"
    f"Description: '{description}'"
)

# Call LLM
with st.spinner("Generating market analysis..."):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        report = resp.choices[0].message.content
    except Exception as e:
        st.error(f"API error: {e}")
        st.stop()

# Split into 6 sections
positions = {i: report.find(f"{i}.") for i in range(1, 7)}
sections = []
for i in range(1, 7):
    start = positions[i]
    if start == -1:
        sections.append(f"No content for section {i}.")
        continue
    next_idxs = [pos for num, pos in positions.items() if num > i and pos != -1]
    end = min(next_idxs) if next_idxs else len(report)
    sections.append(report[start + len(f"{i}."):end].strip())

# Render tabs
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

