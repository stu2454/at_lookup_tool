# Capa-BillyT-BOT: AT Support Item Lookup Tool

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://atlookuptool.streamlit.app/)
![Python Version](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/github/license/stu2454/at_lookup_tool)

A Streamlit-based tool that helps NDIS planners, allied health professionals, and support coordinators quickly explore assistive technology support item details and generate comprehensive market analyses using AI.

## 🤖 Meet Billy the AT Guide

Billy is your friendly AI assistant that transforms complex NDIS support item codes into actionable market intelligence. With over 700,000 NDIS participants requiring tailored assistive technology solutions, Billy helps planners navigate the extensive AT support item catalogue efficiently.

## 🚀 Features

### Core Functionality
- **Support Item Lookup**: Enter any NDIS support item reference number for instant details
- **AI-Powered Market Analysis**: Generate comprehensive 6-section market reports using GPT-4
- **Clinical Context Integration**: Add specific functional activities or user groups for targeted analysis
- **Interactive Interface**: Clean, accessible UI with tabbed navigation

### Market Analysis Sections
1. **Core Function & Clinical Need**: Primary purpose and target disabilities
2. **Device Types & Form Factors**: Complete taxonomy of available options
3. **Features & Brands**: Detailed specifications, models, and regulatory notes
4. **Innovative Technologies**: Forward-looking features and emerging solutions
5. **Critical Assessment Questions**: Key considerations for clinical evaluation
6. **Authoritative Sources**: Trusted references for specifications and pricing

## 📁 Project Structure

```
├── streamlit_app.py           # Main Streamlit application
├── requirements.txt           # Python dependencies
├── data/
│   ├── support_items.docx     # NDIS Code Guide document
│   ├── BillyTBot.png         # Bot mascot image
│   └── billy_tea_icon.png    # Loading animation icon
├── README.md                 # This file
└── .streamlit/
    └── secrets.toml          # API keys (not committed)
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS for accessibility
- **Backend**: OpenAI GPT-4 API for market analysis generation
- **Document Processing**: python-docx for parsing NDIS Code Guide
- **Data Handling**: pandas for support item lookups
- **Deployment**: Streamlit Community Cloud
- **Feedback System**: Trubrics for user feedback collection

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- NDIS Assistive Technology Code Guide (`.docx` format)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/stu2454/at_lookup_tool.git
   cd at_lookup_tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "sk-your-api-key-here"
   OPENAI_PROJECT_ID = "your-project-id"
   TRUBRICS_API_KEY = "your-trubrics-key"  # Optional
   ```

4. **Add your data**
   Place your NDIS Code Guide as `data/support_items.docx`

5. **Run the app**
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Open in browser**
   Visit `http://localhost:8501`

### Using the Tool

1. **Navigate to the "Use Tool" tab**
2. **Enter a Support Item Reference Number** (e.g., `05_091203821_0103_1_2`)
3. **Add optional context** for specific clinical scenarios
4. **Click "Search"** to generate your market analysis
5. **Explore the 6-section report** via the tabbed interface

## 🎯 Use Cases

### For NDIS Planners
- Quickly understand support item specifications during planning meetings
- Generate evidence-based rationale for AT recommendations
- Access comprehensive market overview without manual research

### For Allied Health Professionals
- Explore device options for specific clinical presentations
- Understand regulatory requirements and compliance considerations
- Identify innovative solutions for complex needs

### For Support Coordinators
- Educate participants about available AT options
- Compare different device types and features
- Access authoritative sources for detailed specifications

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-...          # Required: OpenAI API access
OPENAI_PROJECT_ID=proj-...     # Optional: OpenAI project ID
TRUBRICS_API_KEY=...           # Optional: Feedback system
```

### Document Format
The tool expects the NDIS Code Guide in `.docx` format with tables containing:
- Support Item Ref No.
- Support Item (name)
- Description

## 🚀 Deployment

### Streamlit Community Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Add secrets via the Streamlit Cloud dashboard
4. Deploy automatically on commit

### Local Docker (Optional)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🎨 Customization

### Styling
The app uses custom CSS for:
- Increased font sizes for accessibility (24px base)
- Professional color scheme
- Responsive layout design
- Loading animations

### Prompt Engineering
The market analysis is generated using carefully crafted prompts that:
- Ensure consistent 6-section structure
- Include Australian market context
- Reference TGA regulations
- Provide concrete examples and brands

## 📊 Feedback & Analytics

The tool includes optional feedback collection via Trubrics:
- User satisfaction ratings
- Feature usage analytics
- Performance monitoring
- Continuous improvement insights

## 🔒 Security & Compliance

- **API Key Protection**: Secrets never committed to version control
- **Public Data Only**: Uses only publicly available NDIS documentation
- **APS Code of Conduct**: Fully compliant with government standards
- **AI Ethics Principles**: Responsible AI implementation

## 🤝 Contributing

This tool was developed for the "Build a Bureaucrat Bot" Innovation Month 2025 challenge. For improvements or bug reports, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- NDIA Assistive Technology Markets team for subject matter expertise
- OpenAI for GPT-4 API
- Streamlit team for the excellent framework
- Innovation Month 2025 challenge organizers

## 📞 Support

For questions or support, please contact:
- Stuart Smith, Assistant Director, Market Strategy Branch, NDIA
- Email: julia.paterson@ndis.gov.au

---

*Built with ❤️ for the NDIS community during Innovation Month 2025*