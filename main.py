import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import spacy
import json
from fpdf import FPDF
import re
from datetime import datetime

# ---------------- SpaCy Load ----------------
nlp = spacy.load("en_core_web_sm")

# ---------------- UI Setup ----------------
st.set_page_config(page_title="Contract Risk Bot", layout="wide")
st.title("📑 Contract Risk Analysis Bot")

uploaded_file = st.file_uploader(
    "Upload Contract (PDF / DOCX)",
    type=["pdf", "docx"]
)

if uploaded_file:

    # ---------------- Text Extraction ----------------
    text = ""

    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        text = "\n".join(p.text for p in doc.paragraphs)

    st.subheader("📄 Extracted Text")
    st.text_area("Contract Text", text, height=220)

    # ---------------- Language Detection ----------------
    language = "Hindi" if re.search(r'[\u0900-\u097F]', text) else "English"
    st.info(f"Detected Language: {language}")

    # ---------------- Sentence Tokenization ----------------
    sentences = []
    if language == "English":
        doc_nlp = nlp(text)
        sentences = [s.text.strip() for s in doc_nlp.sents if s.text.strip()]
    else:
        sentences = re.split(r"[।.!?]", text)
        sentences = [s.strip() for s in sentences if s.strip()]

    st.subheader("✂️ Tokenized Sentences (First 10)")
    for i, s in enumerate(sentences[:10]):
        st.write(f"{i+1}. {s}")

    # ---------------- Named Entity Recognition ----------------
    st.subheader("🏷️ Named Entities Detected")
    entities = []

    if language == "English":
        for ent in doc_nlp.ents:
            entities.append({"text": ent.text, "label": ent.label_})
            st.write(f"Entity: {ent.text} | Label: {ent.label_}")

    # ---------------- Contract Type Classification ----------------
    st.subheader("📂 Contract Type")

    contract_types = {
        "Employment": ["employee", "salary", "employer"],
        "Service": ["service", "deliverables", "scope"],
        "Vendor": ["vendor", "invoice", "purchase"],
        "Lease": ["lease", "rent", "tenant"],
        "Partnership": ["partner", "profit sharing"]
    }

    text_lower = text.lower()
    scores = {k: sum(kw in text_lower for kw in v) for k, v in contract_types.items()}
    contract_type = max(scores, key=scores.get)
    if scores[contract_type] == 0:
        contract_type = "Unknown"

    st.success(f"Detected Contract Type: {contract_type}")

    # ---------------- Risk Detection ----------------
    risk_keywords = {
        "Indemnity": {"keywords": ["indemnify", "liability"], "level": "High"},
        "Termination": {"keywords": ["terminate without notice"], "level": "High"},
        "Penalty": {"keywords": ["penalty", "late fee"], "level": "Medium"},
        "IP Rights": {"keywords": ["intellectual property"], "level": "High"},
        "Auto Renewal": {"keywords": ["auto renew", "lock-in"], "level": "Low"}
    }

    risky_clauses = []

    for s in sentences:
        for risk, data in risk_keywords.items():
            if any(k in s.lower() for k in data["keywords"]):
                risky_clauses.append({
                    "sentence": s,
                    "risk_type": risk,
                    "level": data["level"]
                })

    st.subheader("⚠️ Risky Clauses")
    for r in risky_clauses:
        st.write(f"[{r['risk_type']} | {r['level']}] {r['sentence']}")

    # ---------------- Obligation / Right / Prohibition ----------------
    st.subheader("⚖️ Clause Intent")

    obligations = ["shall", "must", "required to"]
    rights = ["may", "entitled to"]
    prohibitions = ["shall not", "must not", "prohibited"]

    clause_intents = []

    for s in sentences:
        sl = s.lower()
        intent = "Neutral"
        if any(p in sl for p in prohibitions):
            intent = "Prohibition"
        elif any(o in sl for o in obligations):
            intent = "Obligation"
        elif any(r in sl for r in rights):
            intent = "Right"

        clause_intents.append({"sentence": s, "intent": intent})

    for c in clause_intents[:15]:
        st.write(f"[{c['intent']}] {c['sentence']}")

    # ---------------- Ambiguous Clause Detection ----------------
    st.subheader("❓ Ambiguous Clauses")

    ambiguous_words = ["reasonable", "as applicable", "from time to time", "may include"]
    ambiguous_clauses = [s for s in sentences if any(w in s.lower() for w in ambiguous_words)]

    for a in ambiguous_clauses:
        st.write(a)

    # ---------------- Risk Score ----------------
    total = len(sentences)
    high = sum(1 for r in risky_clauses if r["level"] == "High")
    medium = sum(1 for r in risky_clauses if r["level"] == "Medium")
    low = sum(1 for r in risky_clauses if r["level"] == "Low")

    score = ((high*3 + medium*2 + low) / (total*3))*100 if total else 0

    st.subheader("📊 Composite Risk Score")
    st.success(f"Risk Score: {score:.2f}%")

    # ---------------- Export JSON ----------------
    if st.button("📤 Export JSON"):
        data = {
            "timestamp": str(datetime.now()),
            "contract_type": contract_type,
            "risk_score": score,
            "risky_clauses": risky_clauses,
            "ambiguous_clauses": ambiguous_clauses,
            "clause_intents": clause_intents,
            "entities": entities
        }

        with open("contract_report.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        st.success("JSON file created")

    # ---------------- Export PDF ----------------
    if st.button("📄 Export PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)

        pdf.multi_cell(0, 6, f"Contract Type: {contract_type}\nRisk Score: {score:.2f}%\n\n")

        for r in risky_clauses:
            pdf.multi_cell(0, 6, f"[{r['risk_type']}] {r['sentence']}")

        pdf.output("contract_report.pdf")
        st.success("PDF report created")
