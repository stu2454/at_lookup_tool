# AT Support Item Market Analysis

A **Streamlit** application that analyses assistive-technology support items funded through the National Disability Insurance Scheme (NDIS). Given a reference number, the app extracts the item description from a default Word document and generates a structured market analysis report—covering device types, feature sets, pricing, clinical need, innovations, critical questions and authoritative sources—via the OpenAI API.

---

## Features

* **Automatic document loading**: Parses `data/support_items.docx` containing tables of support items.
* **Reference lookup**: User enters a Support Item Ref No. in the sidebar to retrieve its description.
* **LLM-driven analysis**: Uses OpenAI’s GPT-4 to generate six distinct report sections aligned to clinical assessment and NDIS funding context.
* **Tabbed interface**: Displays each section in its own tab for easy navigation.
* **Customisable styling**: Enlarged fonts and spacing for readability.

---

## Prerequisites

* Python 3.9+
* Docker (optional, for containerised deployment)
* A valid OpenAI API key

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/at-market-analysis.git
   cd at-market-analysis
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Add your OpenAI key**
   Create a file named `.env` in the project root:

   ```ini
   OPENAI_API_KEY=sk-…your-key…
   OPENAI_PROJECT_ID=<optional>
   ```

5. **Prepare data**

   * Place your `support_items.docx` in the `data/` folder. The app expects this file by default.

---

## Running Locally

```bash
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Docker Deployment

1. **Build the image**

   ```bash
   ```

docker build -t at-market-analysis .

````

2. **Run the container**
   ```bash
docker run -d -p 8501:8501 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/data:/app/data:ro \
  at-market-analysis
````

3. Visit [http://localhost:8501](http://localhost:8501).

Alternatively, use **docker-compose**:

```bash
docker-compose up --build
```

---

## Deployment on Streamlit Cloud

1. Push your repo to GitHub.
2. Create a new app on Streamlit Cloud, linking to your GitHub repository.
3. In the app settings, add your `OPENAI_API_KEY` (and `OPENAI_PROJECT_ID`) under **Secrets**.
4. Deploy. The service will auto-install and run your app.

---

## Contributing

1. Fork this repository.
2. Create a new branch: `git checkout -b feature/my-feature`.
3. Commit your changes and push: `git push origin feature/my-feature`.
4. Open a pull request.

---

## Licence

This project is licensed under the MIT Licence. See `LICENSE` for details.

