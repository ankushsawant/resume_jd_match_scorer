import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_txt, clean_text, compute_similarity

st.set_page_config(page_title="Resume ↔ JD Match Scorer", page_icon="🤖")

st.title("🤖 Resume ↔ JD Match Scorer")
st.write("Instruction: Upload a **resume** (PDF) and a **job description** (TXT) to get a semantic match score.")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_file = st.file_uploader("Upload Job Description (TXT)", type=["txt"])

if resume_file and jd_file:
    with st.spinner("Processing..."):
        resume_text = clean_text(extract_text_from_pdf(resume_file))
        jd_text = clean_text(extract_text_from_txt(jd_file))

        score = compute_similarity(resume_text, jd_text)

    st.success(f"✅ Match Score: **{score}%**")
    if score >= 70:
        st.balloons()
        st.info("Strong match! The resume aligns well with the JD.")
    elif score >= 50:
        st.warning("Moderate match — some skills may be missing.")
    else:
        st.error("Low match — significant gaps with the JD.")
