# EquityLens AI

EquityLens AI is a document-grounded equity research assistant. It reads a user-provided company document pack and creates a concise Markdown research note with a financial-signal table, risk register, diligence questions, and an evidence ledger.

## What makes this version distinct
- A clean white-and-blue Streamlit interface with a research-lens selector.
- Gemini API integration (`gemini-2.5-flash` by default), separate from the Groq-backed version.
- Page/sheet-aware document extraction where supported.
- Evidence ledger and risk register instead of a simple bull/bear summary.
- Explicit handling of conflicts, unsupported claims, and incomplete extraction.

## Requirements
- Python 3.10 or newer
- A Google Gemini API key
- Internet access for API requests

## Run locally

### 1. Create and activate a virtual environment

Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Git Bash:
```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 2. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Configure the API key
Copy `.env.example` to `.env`, then add your own key from Google AI Studio:
```env
GEMINI_API_KEY=your_actual_key_here
GEMINI_MODEL=gemini-2.5-flash
```
Never commit `.env` or share your API key. The model name can be changed using `GEMINI_MODEL` if availability changes.

### 4. Start the app
```bash
streamlit run app.py
```
Open the local URL printed by Streamlit.

## Deploy to Streamlit Community Cloud
1. Push the project to a GitHub repository without `.env`, private source documents, or virtual environments.
2. Create a Streamlit Community Cloud app from the repository.
3. In app Settings → Secrets, add:
```toml
GEMINI_API_KEY = "your_actual_key_here"
GEMINI_MODEL = "gemini-2.5-flash"
```
4. The application reads the key from `st.secrets` only if the environment variable is not already set. Add this snippet near the top of `app.py`, after `load_dotenv()`, if deploying to Streamlit Cloud:
```python
if not os.getenv("GEMINI_API_KEY") and "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
```
Do not add the actual secret to source files.

## Supported document formats
PDF, DOCX, TXT, Markdown, CSV, and XLSX. Scanned PDFs may require OCR and can return no text. Extraction coverage can vary by file format.

## Architecture
- `app.py`: Streamlit interface and user interaction.
- `document_parser.py`: extracts text and location hints from supported files.
- `research_engine.py`: prepares source-labeled evidence and calls Gemini.
- `system_prompt.md`: evidence rules and report schema.
- `tests/`: lightweight local tests and a blank run log template.

## Evidence and safety notes
The model is instructed to use only uploaded documents, cite source IDs and available locations, disclose conflicts, and avoid fabricated citations. These are safeguards, not a guarantee: verify key claims against the original files. This is not investment advice and does not fetch live prices or market filings.

## Testing
Run:
```bash
python -m pytest
```
The tests check local parsing/source-ID utilities and do not call the paid/limited external model API. Record actual end-to-end tests in `tests/test_log.md`; do not fill in results until each run has been performed.
