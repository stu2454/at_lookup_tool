<!-- Badges -->
![Build Status](https://img.shields.io/github/actions/workflow/status/your-username/at-market-analysis/ci.yml)
![Python Version](https://img.shields.io/badge/python-3.11-blue)
![Streamlit](https://img.shields.io/badge/streamlit-%3E%3D1.24.0-ff69b4)
![License](https://img.shields.io/github/license/your-username/at-market-analysis)

# NDIS Dynamic Scraper & Market Analysis App

A Streamlit-based tool to centralise NDIS support-item data, dynamically scrape assistive-technology product information, and leverage an LLM to produce structured market analyses for allied-health clinicians, planners and policy teams.

---

## 📋 Table of Contents

1. [Introduction](#1-introduction)  
2. [Project Structure](#2-project-structure)  
3. [Problem Statement & Objectives](#3-problem-statement--objectives)  
4. [Development Approach](#4-development-approach)  
5. [Usage](#5-usage)  
   - [Local (no Docker)](#local-no-docker)  
   - [With Docker Compose](#with-docker-compose)  
   - [Streamlit Community Cloud](#streamlit-community-cloud)  
6. [Forward-Thinking Enhancements](#6-forward-thinking-enhancements)  
7. [Conclusion](#7-conclusion)  

---

## 1. Introduction

People with low vision or other disabilities frequently rely on specialised devices to maintain independence. Yet finding up-to-date information on available assistive-technology, NDIS pricing and clinical considerations can be fragmented and time-consuming. This app:

- **Dynamically scrapes** product details for any NDIS support-item category.  
- **Parses** your code-guide Word document (`.docx`) into a searchable DataFrame.  
- **Leverages** an LLM (GPT-4o-mini) to generate a structured, six-part market analysis.  
- **Delivers** a polished Streamlit UI for quick lookup and comparison.

> 🚀 **Tip:** See screenshots below to preview the app experience.

![App Home Screen](assets/screenshot_home.png)

---

## 2. Project Structure

```
│   README.md                ← This file  
│   Dockerfile               ← Container definition  
│   docker-compose.yml       ← Local orchestration  
│   requirements.txt         ← Python dependencies  
│   providers.json           ← (Optional) supplier list  
│   code_guide.docx          ← Your NDIS Code Guide document  
│   streamlit_app.py         ← Streamlit frontend  
└───modules/                 ← Python modules for scraping & parsing  
```

- **`providers.json`**  
  Can be populated with external supplier data for more granular price lookups.  
- **`modules/`**  
  Contains reusable functions (e.g. scraping routines, document parsing helpers).

---

## 3. Problem Statement & Objectives

- **Fragmented data sources**:  
  Support-item catalogues in Word, Excel or PDF; NDIS Price Guides update frequently.  
- **Manual lookup burden**:  
  Clinicians cross-reference spreadsheets, websites and PDFs to verify specs and costs.  
- **Limited market visibility**:  
  Emerging solutions (AI-driven, AR wearables) are hard to surface in static lists.  
- **Scalability & sharing**:  
  Without a central tool, knowledge remains siloed on local drives.

### Objectives

1. **Centralise** the NDIS support-item catalogue (`code_guide.docx`) into a searchable DataFrame.  
2. **Automate** extraction of “Support Item”, “Ref No.”, and “Description” fields.  
3. **Dynamically scrape** product specifications and pricing for any category (via `modules/`).  
4. **Leverage LLM** to generate a six-section market analysis:
   1. Core function & clinical need  
   2. Device types & form factors  
   3. Feature sets, AUD price bands, brands & regulatory notes  
   4. Innovative/forward-looking technologies  
   5. Critical questions & adjacent solutions  
   6. Authoritative sources  
5. **Protect API keys** with Streamlit Secrets (TOML); never commit them to Git.  
6. **Enable rapid deployment** via Docker Compose and Streamlit Cloud.

---

## 4. Development Approach

- **Tech stack**  
  - **Frontend & server**: Streamlit (Python)  
  - **Document parsing**: `python-docx` for Word tables  
  - **Data handling**: pandas for lookups  
  - **Web scraping**: custom Python modules under `modules/`  
  - **LLM integration**: OpenAI’s `gpt-4o-mini`  
- **Security & configuration**  
  - `.streamlit/secrets.toml` (or Cloud UI) for `OPENAI_API_KEY` & `OPENAI_PROJECT_ID`  
  - `.gitignore` excludes `/data`, `.env` and other local files  
- **Layout & UX**  
  - Wide format (`st.set_page_config(layout="wide")`)  
  - Global CSS overrides for 24 px font size  
  - Six fixed tabs for each analysis section  

![Report Tabs](assets/screenshot_tabs.png)

---

## 5. Usage

### Local (no Docker)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

1. Place your `code_guide.docx` in `./data/`.  
2. Provide your OpenAI API key via `.streamlit/secrets.toml` or environment variable.  
3. Visit <http://localhost:8501>.

### With Docker Compose

```bash
export OPENAI_API_KEY="sk-…"
docker-compose up --build
```

- Mounts `./data` (read-only) into the container.  
- Exposes the app at <http://localhost:8501>.

### Streamlit Community Cloud

1. Push this repo to GitHub.  
2. In your app’s **Advanced settings → Secrets**, add your key in TOML:

   ```toml
   OPENAI_API_KEY = "sk-…"
   ```

3. Click **Deploy**. Colleagues can then access the live app immediately.

---

## 6. Forward-Thinking Enhancements

- **Automated catalogue updates**: Poll the NDIS Price Guide PDF/API monthly.  
- **Bulk analysis**: Upload many Ref Nos. at once; export to Excel/PDF.  
- **Interactive tables**: Use `streamlit-aggrid` for sortable feature/pricing matrices.  
- **Feedback loop**: Embed 👍/👎 on each section to refine prompts.  
- **Role-based access**: Add simple login (e.g. Auth0) for sensitive functions.

---

## 7. Conclusion

By merging dynamic scraping, document parsing, LLM-driven intelligence and a polished Streamlit UI, this tool transforms a manual, error-prone process into a scalable, user-friendly experience. It empowers allied-health clinicians and policy teams to make evidence-based assistive-technology decisions—ensuring NDIS participants receive the most appropriate, cost-effective solutions.

---

*Prepared by [Your Name], [Date]*
