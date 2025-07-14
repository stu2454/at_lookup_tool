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
st.title("Capa-BillyT-BOT: AT Support Item Lookup Tool")

st.sidebar.image("data/BillyTBot.png", caption="Billy the AT guide", use_container_width=True)

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
    "You are an expert NDIS Assistive Technology (AT) market analyst and an experienced allied-health clinician. Your task is to generate a comprehensive, six-part market analysis for a given NDIS Support Item.\n\n"
    "You will be provided with the Support Item's name, its official description, and optional clinical context. You MUST structure your response into exactly six sections, each starting with the delimiter ===SECTION N===.\n\n"
    "<instructions>\n"
    "1.  **Adhere strictly to the six-section format.** Do not merge, omit, or add sections.\n"
    "2.  **Use clear, professional language.** Write for an audience of clinicians, support coordinators, and NDIS planners.\n"
    "3.  **Provide concrete examples.** Use bullet points for lists of features, models, and questions.\n"
    "4.  **Reference Australian market conditions.** All pricing should be in AUD. Mention TGA regulations where applicable.\n"
    "5.  **Be objective and comprehensive.** Cover a range of brands and price points.\n"
    "6.  **Only include sub-types and device types that are clinically and commercially recognised for the given Support Item in Australia.**\n"
    "</instructions>\n\n"
    "Here is the structure and an example of the desired output for each section:\n\n"
    "---\n\n"
    "===SECTION 1===\n"
    "**Core Function, Clinical Need & Key Use-Cases for NDIS participants.**\n"
    "*   **Core Function:** [Succinctly state the primary purpose of this AT category. What problem does it solve?]\n"
    "*   **Clinical Need:** [Describe the specific functional impairments or disabilities this AT addresses.]\n"
    "*   **Key NDIS Use-Cases:**\n"
    "    *   [Example Use-Case 1: e.g., \"Enabling independent community access for a participant with limited mobility.\"]\n"
    "    *   [Example Use-Case 2: e.g., \"Providing postural support during mealtimes for a child with cerebral palsy.\"]\n"
    "    *   [Example Use-Case 3: e.g., \"Reducing carer strain during transfers for a participant with high physical support needs.\"]\n\n"
    "===SECTION 2===\n"
    "**Full Taxonomy of Device Types & Form Factors.**\n"
    "*   **Primary Category:** [e.g., Manual Wheelchairs]\n"
    "    *   List all clinically and commercially relevant sub-types for this category, based on Australian market conventions. Do not include sub-types that are not commonly recognised or appropriate for this Support Item. For each sub-type, specify the form factor. For example:\n"
    "        *   **Sub-type:** [e.g., Rigid Frame Wheelchairs]\n"
    "            *   **Form Factor:** [e.g., Ultra-lightweight, folding/non-folding]\n"
    "        *   **Sub-type:** [e.g., Folding Frame Wheelchairs]\n"
    "            *   **Form Factor:** [e.g., Standard, bariatric]\n"
    "        *   **Sub-type:** [e.g., Tilt-in-Space Wheelchairs]\n"
    "            *   **Form Factor:** [e.g., Manual tilt, attendant-propelled]\n"
    "===SECTION 3===\n"
    "**For each Device Type: Feature Sets, AUD Price Bands, Brands/Models, and Regulatory Notes.**\n"
    "*   **Device Type:** [e.g., Rigid Frame Wheelchairs]\n"
    "    *   **Key Feature Sets:** [e.g., Custom-scripted frame geometry, quick-release axles, adjustable centre of gravity, side guards (carbon fibre vs. aluminium).]\n"
    "    *   **AUD Price Band (Supply Only):** [e.g., \"$4,000 - $9,500\"]\n"
    "    *   **Example Brands/Models:** [e.g., \"Quickie (Nitrum, GPV), TiLite (TRA, ZRA), Panthera (X, S3)\"]\n"
    "    *   **Regulatory Notes:** [e.g., \"Must meet AS/NZS 3695.1. TGA registration may be required for certain medical claims.\"]\n"
    "*   **Device Type:** [e.g., Tilt-in-Space Wheelchairs]\n"
    "    *   **Key Feature Sets:** [e.g., Gas-strut or cable-activated tilt mechanism (0-55 degrees), elevating leg rests, transit tie-down points.]\n"
    "    *   **AUD Price Band (Supply Only):** [e.g., \"$5,500 - $12,000\"]\n"
    "    *   **Example Brands/Models:** [e.g., \"Glide (Series 4, G2), Sunrise Medical (Iris), Ki Mobility (Focus CR)\"]\n"
    "    *   **Regulatory Notes:** [e.g., \"Often prescribed as part of a complex seating system. Requires a thorough clinical assessment.\"]\n\n"
    "===SECTION 4===\n"
    "**Innovative or Forward-Looking Technologies.**\n"
    "*   **Materials Science:** [e.g., \"Use of 3D-printed titanium or carbon fibre composites for custom frame components, reducing weight while maintaining strength.\"]\n"
    "*   **Smart Features & IoT:** [e.g., \"Integration of power-assist wheels (e.g., SmartDrive, Twion) with companion apps for tracking distance, battery life, and push efficiency.\"]\n"
    "*   **Ergonomics & Design:** [e.g., \"Dynamic backrests that move with the user, and novel suspension systems (e.g., Frog Legs) to reduce whole-body vibration.\"]\n\n"
    "===SECTION 5===\n"
    "**Critical Questions & Adjacent Solutions.**\n"
    "*   **Critical Questions for Assessment:**\n"
    "    *   [e.g., \"What are the participant's key environments (home, work, community)? Are there ramps, tight corners, or uneven surfaces?\"]\n"
    "    *   [e.g., \"How will the device be transported? Does it need to fit in a specific vehicle?\"]\n"
    "    *   [e.g., \"What is the participant's projected functional change over the next 5 years?\"]\n"
    "*   **Adjacent or Complementary Solutions:**\n"
    "    *   [e.g., \"Pressure care cushions (Roho, Jay) are almost always required.\"]\n"
    "    *   [e.g., \"Vehicle modifications for transport.\"]\n"
    "    *   [e.g., \"Specialised wheelchair bags and accessories.\"]\n\n"
    "===SECTION 6===\n"
    "**Three Authoritative Sources for NDIS Pricing, Specs & Market Data.**\n"
    "*   **1. Supplier Catalogues:** [e.g., \"Aidacare (aidacare.com.au) or Independent Living Specialists (ilsau.com.au) - for retail pricing and technical specifications.\"]\n"
    "*   **2. Professional Associations:** [e.g., \"Assistive Technology Suppliers Australasia (ATSA) - their annual expo and member directory provide a broad market overview.\"]\n"
    "*   **3. NDIS-Specific Databases:** [e.g., \"Seating and Wheeled Mobility technical resources from state-based bodies like EnableNSW or Indigo (WA).\"]\n"
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

