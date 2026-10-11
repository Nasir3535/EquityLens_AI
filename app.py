import os
import streamlit as st
from dotenv import load_dotenv
from document_parser import parse_uploaded_file, assign_source_ids
from research_engine import generate_research

load_dotenv()
st.set_page_config(page_title="EquityLens AI", page_icon="📊", layout="wide")

# Streamlit Community Cloud secrets fallback; local development uses .env.
try:
    if not os.getenv("GEMINI_API_KEY") and "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    if not os.getenv("GEMINI_MODEL") and "GEMINI_MODEL" in st.secrets:
        os.environ["GEMINI_MODEL"] = st.secrets["GEMINI_MODEL"]
except Exception:
    # st.secrets may be unavailable in a local run without a secrets file.
    pass

st.markdown("""
<style>
:root { --blue:#2457D6; --ink:#14213D; --muted:#61708A; }
.stApp { background: #F5F8FF; color: var(--ink); }
.block-container { max-width: 1220px; padding-top: 1.6rem; }
.hero { background: linear-gradient(115deg,#173B8F,#3478F6); color:white; padding:1.6rem 1.8rem; border-radius:18px; margin-bottom:1.2rem; }
.hero h1 { color:white; margin:0; font-size:2.1rem; }
.hero p { color:#E6EEFF; margin:.45rem 0 0 0; }
.panel { background:white; border:1px solid #E0E8F8; border-radius:14px; padding:1rem 1.1rem; }
.small-muted { color:#61708A; font-size:.9rem; }
div.stButton > button[kind="primary"] { background:#2457D6; border-color:#2457D6; }
</style>
<div class="hero">
  <h1>EquityLens AI</h1>
  <p>Document-grounded company research · Evidence first, uncertainty visible</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Research setup")
    ticker = st.text_input("Company ticker", value="SRVCABLE").strip().upper()
    as_of = st.date_input("Analysis date")
    st.caption("Use only documents you are permitted to share. This app does not fetch live market data.")
    st.markdown("---")
    st.markdown("**Model**")
    st.caption(os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    st.markdown("**Provider**")
    st.caption("Google Gemini API")

st.markdown("### 1 · Add the evidence pack")
uploads = st.file_uploader(
    "Upload company documents",
    type=["pdf", "docx", "txt", "md", "csv", "xlsx"],
    accept_multiple_files=True,
    help="Each file receives a source ID. PDF pages and document sections are retained where available."
)
if uploads:
    st.success(f"{len(uploads)} file(s) selected")
    with st.expander("Review uploaded sources", expanded=True):
        for f in uploads:
            st.write(f"📄 **{f.name}** · {f.size:,} bytes")

focus = "Balanced diligence"
extra_context = st.text_area(
    "Optional question for the analyst",
    placeholder="Example: What should an investor verify before relying on the reported order book?",
    height=85
)

left, right = st.columns([1, 2])
with left:
    run = st.button("Generate evidence brief", type="primary", use_container_width=True)
with right:
    st.markdown('<p class="small-muted">The output separates reported facts from interpretation and keeps unresolved conflicts visible.</p>', unsafe_allow_html=True)

if run:
    if not ticker:
        st.error("Enter a company ticker.")
        st.stop()
    if not uploads:
        st.error("Upload at least one company document.")
        st.stop()
    if not os.getenv("GEMINI_API_KEY"):
        st.error("GEMINI_API_KEY is missing. Add it to your local .env file or Streamlit Cloud Secrets.")
        st.stop()

    parsed = []
    with st.spinner("Reading the evidence pack..."):
        for upload in uploads:
            try:
                parsed.extend(parse_uploaded_file(upload))
            except Exception as exc:
                st.warning(f"Could not read {upload.name}: {exc}")
    parsed = assign_source_ids(parsed)
    if not parsed:
        st.error("No readable text was found in the uploaded documents.")
        st.stop()

    with st.spinner("Building the research brief from the supplied evidence..."):
        try:
            result = generate_research(
                ticker=ticker,
                as_of=str(as_of),
                documents=parsed,
                focus=focus,
                extra_question=extra_context.strip()
            )
        except Exception as exc:
            st.error(f"Research generation failed: {exc}")
            st.info("Check your Gemini API key, model availability, network connection, and API quota.")
            st.stop()

    st.session_state["equitylens_result"] = result
    st.session_state["equitylens_ticker"] = ticker

if "equitylens_result" in st.session_state:
    result = st.session_state["equitylens_result"]
    st.markdown("---")
    st.markdown(f"## Research brief · {st.session_state.get('equitylens_ticker', '')}")
    st.warning("AI-generated research is not investment advice. Verify important claims against original documents.")
    st.markdown(result)
    st.download_button(
        "Download Markdown brief",
        data=result,
        file_name=f"{st.session_state.get('equitylens_ticker','company').lower()}_equitylens_brief.md",
        mime="text/markdown",
        use_container_width=False
    )
