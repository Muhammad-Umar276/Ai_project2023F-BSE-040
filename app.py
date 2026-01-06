import pytesseract
from PIL import Image
import cv2
import numpy as np
import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from grading import grade_answer
import io
import os

if os.name == "nt":  # only for Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---------- TESSERACT PATH ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="EDU SCORE | AI Evaluation Platform",
    page_icon="🎓",
    layout="wide"
)

# ---------- OCR HELPERS ----------
def ocr_image(pil_image):
    gray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)
    return pytesseract.image_to_string(
        gray,
        config="--oem 3 --psm 6"
    ).strip()

def extract_text_from_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")

    for page in pdf:
        page_text = page.get_text().strip()

        # 🧠 If PDF is scanned → OCR fallback
        if len(page_text) < 20:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            page_text = ocr_image(img)

        text += page_text + "\n"

    return text.strip()

def extract_text(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(file)

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    return ""

def extract_text_from_image(image_file):
    image = Image.open(image_file).convert("RGB")
    return ocr_image(image)

# ---------- HERO ----------
st.markdown("""
<div class="hero">
  <h1>EDU <span>SCORE</span></h1>
  <p>
    AI-powered subjective answer evaluation platform delivering
    examiner-level grading, semantic intelligence and transparent feedback
    for modern education.
  </p>
</div>
""", unsafe_allow_html=True)

# ================= TEACHER =================
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📘 Teacher / Ideal Answer Sheet</div>", unsafe_allow_html=True)

ideal_file = st.file_uploader(
    "Teacher Answer (PDF / DOCX / Scanned PDF)",
    type=["pdf", "docx"]
)

ideal_image = st.file_uploader(
    "Teacher Handwritten (Image)",
    type=["jpg", "jpeg", "png"]
)

st.markdown("</div>", unsafe_allow_html=True)

# ================= STUDENT =================
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📝 Student Answer Sheet</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    student_file = st.file_uploader(
        "Student Answer (PDF / DOCX / Scanned PDF)",
        type=["pdf", "docx"]
    )
with c2:
    student_image = st.file_uploader(
        "Student Handwritten (Image)",
        type=["jpg", "png", "jpeg"]
    )

grade_btn = st.button("⚡ Evaluate with EDU SCORE AI", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================= RESULTS =================
if grade_btn:
    if (ideal_file or ideal_image) and (student_file or student_image):

        with st.spinner("🧠 EDU SCORE AI is evaluating..."):

            # ---- TEACHER ----
            ideal_answer = (
                extract_text(ideal_file)
                if ideal_file
                else extract_text_from_image(ideal_image)
            )

            # ---- STUDENT ----
            student_answer = (
                extract_text(student_file)
                if student_file
                else extract_text_from_image(student_image)
            )

        if ideal_answer and student_answer:

            teacher_concepts = [
                c.strip() for c in ideal_answer.split(".") if len(c.strip()) > 25
            ]

            results, marks, confidence = grade_answer(
                teacher_concepts,
                student_answer
            )

            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader("📊 Concept-Wise Evaluation")

                for cid, status, concept, student_sentence, feedback in results:
                    st.markdown("<div class='glass'>", unsafe_allow_html=True)

                    if status:
                        st.success(f"✔ Concept {cid} Covered")
                        st.code(student_sentence)
                    else:
                        st.error(f"✖ Concept {cid} Missing")
                        st.info("Expected Concept:")
                        st.code(concept)
                        st.warning(feedback)

                    st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.subheader("🎯 Final Score")
                st.metric("Marks", f"{marks} / 10")
                st.metric("Coverage", f"{confidence}%")
                st.progress(confidence / 100)

        else:
            st.error("❌ OCR/Text extraction failed.")

    else:
        st.warning("⚠ Upload both Teacher & Student answers.")

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
  <strong>EDU SCORE</strong> — AI-Driven Academic Evaluation Platform<br>
  Fair • Transparent • Intelligent
</div>
""", unsafe_allow_html=True)
