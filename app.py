import streamlit as st
from pypdf import PdfReader
from io import BytesIO
import re
import html

st.set_page_config(
    page_title="Proof Keeper(NYAAY AI)",
    page_icon="⚖️",
    layout="wide"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: #f8fbff;
    color: #14264b;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1250px;
}
.hero {
    background: linear-gradient(115deg, #10264b, #247bb8);
    color: white;
    text-align: center;
    padding: 35px 15px;
    border-radius: 15px;
    margin-bottom: 25px;
}
.hero h1 {
    color: white !important;
    font-size: 44px !important;
    margin-bottom: 8px;
}
.hero p {
    color: white !important;
    font-size: 18px;
}
.welcome h2 {
    color: #10264b;
}
.feature {
    text-align: center;
    background: white;
    border: 1px solid #e3ebf7;
    border-radius: 12px;
    padding: 18px 8px;
    min-height: 145px;
}
.feature-icon {
    font-size: 32px;
}
.feature h4 {
    color: #10264b;
    font-size: 16px;
}
.feature p {
    color: #60789c;
    font-size: 14px;
}
.upload-box {
    background: #f3f8ff;
    border: 2px dashed #b9d1f3;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.footer {
    text-align: center;
    padding: 30px 10px;
    color: #60789c;
    border-top: 1px solid #dce6f4;
    margin-top: 35px;
}
div[data-testid="stFileUploader"] {
    background: #f3f8ff;
    border: 1px dashed #b9d1f3;
    border-radius: 12px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------- FRONT PAGE ----------
st.markdown("""
<div class="hero">
    <h1>⚖️ Proof Keeper(NYAAY AI)</h1>
    <p style="font-size:24px;">
        Court Document Review &amp; Organization
    </p>
    <p>Upload &nbsp; • &nbsp; Analyze &nbsp; • &nbsp;
    Organize &nbsp; • &nbsp; Download</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="welcome">
    <h2>Welcome to Proof Keeper</h2>
    <p style="font-size:17px; color:#344968;">
    A simple tool to extract readable text from court documents,
    find possible case details and important dates, and prepare
    a downloadable review report.
    </p>
</div>
""", unsafe_allow_html=True)

st.info("Start by uploading a PDF or TXT court document below.")

# ---------- FEATURE CARDS ----------
c1, c2, c3, c4 = st.columns(4)

features = [
    (c1, "📄", "Extract Key Details",
     "Find possible case information"),
    (c2, "📅", "Find Important Dates",
     "See detected dates at a glance"),
    (c3, "🔎", "Detect Legal Keywords",
     "Highlight selected legal terms"),
    (c4, "📥", "Download Report",
     "Save a review report")
]

for col, icon, heading, description in features:
    with col:
        st.markdown(f"""
        <div class="feature">
            <div class="feature-icon">{icon}</div>
            <h4>{heading}</h4>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ---------- DOCUMENT UPLOAD ----------
st.markdown("""
<div class="upload-box">
    <div style="font-size:36px;">☁️</div>
    <h3 style="color:#17365f;">Choose a document</h3>
    <p>Upload a court judgment, order, or petition</p>
    <p style="color:#60789c;">Supported formats: PDF, TXT</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload File",
    type=["pdf", "txt"],
    label_visibility="collapsed"
)

# ---------- HELPER FUNCTIONS ----------
def find_first(pattern, text, default="Not detected"):
    match = re.search(
        pattern, text, re.IGNORECASE | re.MULTILINE
    )
    return match.group(1).strip() if match else default


def make_summary(text, limit=5):
    sentences = re.split(
        r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text)
    )
    useful = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 45 and sentence not in useful:
            useful.append(sentence)
        if len(useful) >= limit:
            break
    return useful


# ---------- DOCUMENT REVIEW ----------
if uploaded_file:
    try:
        if uploaded_file.name.lower().endswith(".pdf"):
            reader = PdfReader(BytesIO(uploaded_file.getvalue()))
            text = "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        else:
            text = uploaded_file.getvalue().decode(
                "utf-8", errors="replace"
            )
    except Exception as e:
        st.error(f"Could not read document: {e}")
        st.stop()

    if not text.strip():
        st.warning(
            "No readable text found. Scanned PDFs may need OCR."
        )
        st.stop()

    st.success(f"Text extracted from: {uploaded_file.name}")

    st.header("1. Case Details")

    case_number = find_first(
        r"((?:CRIMINAL|CIVIL|WRIT|SPECIAL LEAVE)?\s*"
        r"(?:APPEAL|PETITION|CASE)\s*NO\.?\s*[\w /().-]+)",
        text
    )

    appellant = find_first(
        r"^\s*([A-Z][A-Z .'-]+?)\s*[.…]*\s*APPELLANT",
        text
    )

    respondent = find_first(
        r"^\s*(?:VERSUS|VS\.?)\s*\n?\s*"
        r"([A-Z][A-Z .,'()-]+)",
        text
    )

    court = (
        "Supreme Court of India"
        if re.search(r"SUPREME COURT OF INDIA", text, re.I)
        else "Not detected"
    )

    judgment_date = find_first(
        r"\b(?:DATED?\s*[:\-]?\s*)?"
        r"(\d{1,2}(?:st|nd|rd|th)?\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December),?\s+\d{4})",
        text
    )

    outcome = find_first(
        r"\b(the appeal is dismissed|the appeal is allowed|"
        r"appeal stands dismissed|appeal stands allowed)\b",
        text
    )

    st.write("**Court:**", court)
    st.write("**Case / Appeal Number:**", case_number)
    st.write("**Appellant:**", appellant)
    st.write("**Respondent:**", respondent)
    st.write("**Judgment Date:**", judgment_date)
    st.write("**Possible Outcome:**", outcome)

    st.caption(
        "Automatically detected fields may be incomplete or "
        "incorrect. Verify against the original judgment."
    )

    st.header("2. Basic Text Summary")
    summary = make_summary(text)

    if summary:
        for sentence in summary:
            st.write("- " + sentence)
    else:
        st.write("No summary sentences could be extracted.")

    st.caption(
        "Basic extractive summary, not AI-generated legal advice."
    )

    st.header("3. Important Dates")

    date_pattern = (
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        r"|\b\d{1,2}(?:st|nd|rd|th)?\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December),?\s+\d{4}\b"
    )

    dates = sorted(set(re.findall(date_pattern, text, re.I)))

    if dates:
        for date in dates:
            st.write("- " + date)
    else:
        st.write("No matching dates found.")

    st.header("4. Legal Keywords")

    keywords = [
        "petition", "judgment", "order", "plaintiff", "defendant",
        "hearing", "appeal", "evidence", "court", "application",
        "conviction", "acquitted", "dismissed", "appellant",
        "respondent"
    ]

    found = [
        word for word in keywords
        if re.search(r"\b" + re.escape(word) + r"\b", text, re.I)
    ]

    st.write(", ".join(found) if found else "No listed keywords found.")

    st.header("5. Full Extracted Text")

    terms = [
        "judgment", "court", "appeal", "petition", "evidence",
        "order", "conviction", "acquitted", "appellant",
        "respondent", "dismissed", "allowed"
    ]

    pattern = r"\b(" + "|".join(
        re.escape(word) for word in terms
    ) + r")\b"

    safe_text = html.escape(text)

    highlighted = re.sub(
        pattern,
        lambda m: (
            '<mark style="background:#ffe58a; color:#14264b;">'
            + m.group(0) + "</mark>"
        ),
        safe_text,
        flags=re.IGNORECASE
    )

    st.markdown(
        '<div style="background:white; padding:18px; '
        'border:1px solid #dce6f4; border-radius:10px; '
        'white-space:pre-wrap; overflow-wrap:anywhere;">'
        + highlighted + "</div>",
        unsafe_allow_html=True
    )

    report = (
        "PROOF KEEPER - DOCUMENT REVIEW\n\n"
        f"Court: {court}\n"
        f"Case Number: {case_number}\n"
        f"Appellant: {appellant}\n"
        f"Respondent: {respondent}\n"
        f"Judgment Date: {judgment_date}\n"
        f"Possible Outcome: {outcome}\n\n"
        "BASIC SUMMARY:\n"
        + "\n".join("- " + s for s in summary)
        + "\n\nDATES:\n"
        + "\n".join(dates)
        + "\n\nKEYWORDS:\n"
        + ", ".join(found)
        + "\n\nFULL TEXT:\n"
        + text
    )

    st.download_button(
        "📥 Download Review Report",
        data=report,
        file_name="proof_keeper_report.txt",
        mime="text/plain"
    )

# ---------- BACK PAGE / FOOTER ----------
st.markdown("""
<div class="footer">
    <h3 style="color:#17365f;">About Proof Keeper</h3>
    <p>Making court documents easier to review and organize.</p>
    <p><b>Built with:</b> Python • Streamlit • pypdf</p>
    <p>Created as a prototype for faster document review.</p>
    <h3>Thank You ⚖️</h3>
    <p><b>Created by:</b> ALPHA CODERS </p>
<p>Hackathon Project | Proof Keeper</p>
    <p style="font-size:12px;">
    Automatically detected information may be incomplete or inaccurate.
    Always verify against the original court document.
    </p>
</div>
""", unsafe_allow_html=True)