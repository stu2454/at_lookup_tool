import os
import re
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from openai import OpenAI
from io import BytesIO
from docx import Document

# Load local .env when running locally
load_dotenv()

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
    .stTextInput label, .stSelectbox label, .stTextArea label {
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

# Retrieve OpenAI credentials (local .env or Streamlit secrets)
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
try:
    secrets = st.secrets
    api_key     = api_key     or secrets.get("OPENAI_API_KEY")
    project_id  = project_id  or secrets.get("OPENAI_PROJECT_ID")
    if "openai" in secrets:
        api_key     = api_key     or secrets["openai"].get("api_key")
        project_id  = project_id  or secrets["openai"].get("project_id")
except Exception:
    pass

if not api_key:
    st.error(
        "🚨 Missing OpenAI API key!\n\n"
        "Provide it in a local `.env`:\n\n"
        "```bash\nexport OPENAI_API_KEY=\"sk-...\"\n```\n\n"
        "or via Streamlit Secrets (TOML):\n\n"
        "```toml\nOPENAI_API_KEY = \"sk-...\"\n[openai]\napi_key = \"sk-...\"\nproject_id = \"...\"\n```"
    )
    st.stop()

# Initialise OpenAI client
client = OpenAI(api_key=api_key, project=project_id)

# App title
st.title("Assistive-Tech Market Analysis (NDIS)")

# Sidebar inputs
st.sidebar.header("Configuration")
ref_no = st.sidebar.text_input("Support Item Ref No.")
extra_ctx = st.sidebar.text_area(
    "Additional Context (optional)",
    help=(
        "• Specify key functional activities (e.g. 'seated feeding support').\n"
        "• Note any special user groups/settings (e.g. 'paediatric', 'wheelchair transfers').\n\n"
        "Be succinct but include enough detail to guide the analysis."
    )
)
run_search = st.sidebar.button("Search")

if not run_search:
    st.sidebar.write("Enter a Ref No. (and optional context), then click **Search**.")
    st.stop()

if not ref_no.strip():
    st.sidebar.error("Please enter a valid Support Item Ref No.")
    st.stop()

# Load support-items document
default_path = os.path.join("data", "support_items.docx")
if not os.path.exists(default_path):
    st.error(f"Default document not found at `{default_path}`")
    st.stop()

with open(default_path, "rb") as f:
    sf = BytesIO(f.read())
sf.name = os.path.basename(default_path)

# Helper: load DataFrame from docx/csv/xlsx
def load_df(file):
    name = file.name.lower()
    if name.endswith((".xlsx", "xls")):
        return pd.read_excel(file)
    if name.endswith(".csv"):
        return pd.read_csv(file)
    if name.endswith(".docx"):
        doc = Document(BytesIO(file.read()))
        tables = []
        for tbl in doc.tables:
            headers = [c.text.strip() for c in tbl.rows[0].cells]
            required = {"Support Item Ref No.", "Support Item", "Description"}
            if required.issubset(headers):
                rows = []
                for row in tbl.rows[1:]:
                    rows.append({hdr: row.cells[idx].text.strip()
                                 for idx, hdr in enumerate(headers)})
                tables.append(pd.DataFrame(rows))
        if tables:
            return pd.concat(tables, ignore_index=True)
    return None

# Parse the support-items document
try:
    df = load_df(sf)
    if df is None:
        raise ValueError("Could not parse the document. Check its format.")
except Exception as e:
    st.error(f"Error loading document: {e}")
    st.stop()

# Lookup by Ref No.
df.columns = [c.strip() for c in df.columns]
match = df[df["Support Item Ref No."].astype(str).str.strip() == ref_no.strip()]
if match.empty:
    st.error(f"Ref No. '{ref_no}' not found.")
    st.stop()

support_item_text = match.iloc[0]["Support Item"].strip()
description       = match.iloc[0]["Description"].strip()

# Display chosen item
st.subheader("Support Item Details")
st.markdown(f"**Support Item:** {support_item_text}")
st.info(f"**Description:** {description}")

# Build prompts with explicit section markers
system_prompt = (
    "You are an allied-health clinician with extensive experience in assessing, prescribing "
    "and fitting assistive technology funded through the NDIS for people living with disability. "
    "I will provide a Support Item name and description. Your task is to produce a six-part "
    "structured report. Please begin each section with a delimiter line:\n\n"
    "===SECTION 1===\n"
    "...content for section 1...\n"
    "===SECTION 2===\n"
    "...section 2...\n"
    "and so on up to ===SECTION 6===\n\n"
    "Sections:\n"
    "1. Core Function, Clinical Need & Key Use-Cases for NDIS participants.\n"
    "2. Full Taxonomy of Device Types & Form Factors.\n"
    "3. For each Device Type: feature sets; AUD price bands; brands/models; regulatory notes.\n"
    "4. Innovative or Forward-Looking Technologies.\n"
    "5. Critical Questions & Adjacent Solutions.\n"
    "6. Three Authoritative Sources for NDIS pricing, specs & market data.\n"
    "Label each section accordingly."
)
user_prompt = (
    f"Support Item: '{support_item_text}'\n"
    f"Description: '{description}'"
)
if extra_ctx.strip():
    user_prompt += f"\n\nAdditional context: {extra_ctx.strip()}"

# Call the LLM
with st.spinner("Generating market analysis…"):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ]
        )
        report = resp.choices[0].message.content
    except Exception as e:
        st.error(f"API error: {e}")
        st.stop()

# Split on explicit markers
parts = re.split(r"^===SECTION (\d+)===\s*$", report, flags=re.MULTILINE)
sections = {str(i): "No content returned." for i in range(1, 7)}
for idx in range(1, len(parts), 2):
    num = parts[idx]
    body = parts[idx+1].strip()
    if num in sections:
        sections[num] = body

# Render as tabs
tab_labels = [
    "1. Core Function & Need",
    "2. Device Types & Forms",
    "3. Features, Pricing & Brands",
    "4. Innovations",
    "5. Critical Questions",
    "6. Authoritative Sources"
]
tabs = st.tabs(tab_labels)
for i, tab in enumerate(tabs, start=1):
    with tab:
        st.write(sections.get(str(i)))

