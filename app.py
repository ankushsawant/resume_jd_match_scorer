import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_txt, clean_text, compute_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title="Resume ↔ JD Match Scorer", page_icon="🤖")

st.title("🤖 Resume ↔ JD Match Scorer")
st.write("Instruction: Upload a **resume** (PDF) and a **job description** (TXT) to get a semantic match score.")

# File size limit (in bytes) - 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# File uploaders
resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_file = st.file_uploader("Upload Job Description (TXT)", type=["txt"])

# Validate and process files
if resume_file and jd_file:
    try:
        # Validate file sizes
        if resume_file.size > MAX_FILE_SIZE:
            st.error(f"❌ Resume file is too large ({resume_file.size / (1024*1024):.2f} MB). Maximum allowed size is 10 MB.")
            logger.warning(f"Resume file too large: {resume_file.size} bytes")
            st.stop()

        if jd_file.size > MAX_FILE_SIZE:
            st.error(f"❌ Job description file is too large ({jd_file.size / (1024*1024):.2f} MB). Maximum allowed size is 10 MB.")
            logger.warning(f"JD file too large: {jd_file.size} bytes")
            st.stop()

        if resume_file.size == 0:
            st.error("❌ Resume file is empty. Please upload a valid PDF file.")
            st.stop()

        if jd_file.size == 0:
            st.error("❌ Job description file is empty. Please upload a valid TXT file.")
            st.stop()

        with st.spinner("Processing files..."):
            # Extract text from resume
            try:
                resume_text_raw = extract_text_from_pdf(resume_file)
                logger.info("Resume text extracted successfully")
            except ValueError as ve:
                st.error(f"❌ Resume Error: {str(ve)}")
                st.info("💡 Tip: Ensure your PDF contains selectable text (not just scanned images).")
                logger.error(f"Resume extraction failed: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Failed to process resume: {str(e)}")
                st.info("💡 Tip: Try re-saving your PDF or converting it to a different format.")
                logger.error(f"Resume processing error: {str(e)}")
                st.stop()

            # Extract text from job description
            try:
                jd_text_raw = extract_text_from_txt(jd_file)
                logger.info("JD text extracted successfully")
            except ValueError as ve:
                st.error(f"❌ Job Description Error: {str(ve)}")
                logger.error(f"JD extraction failed: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Failed to process job description: {str(e)}")
                st.info("💡 Tip: Ensure your file is a valid text file with UTF-8 or standard encoding.")
                logger.error(f"JD processing error: {str(e)}")
                st.stop()

            # Clean texts
            try:
                resume_text = clean_text(resume_text_raw)
                jd_text = clean_text(jd_text_raw)
                logger.info("Text cleaning completed")
            except ValueError as ve:
                st.error(f"❌ Text Processing Error: {str(ve)}")
                logger.error(f"Text cleaning failed: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Failed to clean text: {str(e)}")
                logger.error(f"Text cleaning error: {str(e)}")
                st.stop()

            # Compute similarity
            try:
                score = compute_similarity(resume_text, jd_text)
                logger.info(f"Similarity score computed: {score}")
            except RuntimeError as re:
                st.error(f"❌ Model Error: {str(re)}")
                st.info("💡 Please restart the application. If the problem persists, check your internet connection and try reinstalling dependencies.")
                logger.error(f"Model error: {str(re)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Failed to compute similarity: {str(e)}")
                logger.error(f"Similarity computation error: {str(e)}")
                st.stop()

        # Display results
        st.success(f"✅ Match Score: **{score}%**")

        # Provide contextual feedback
        if score >= 70:
            st.balloons()
            st.info("🎉 Strong match! The resume aligns well with the JD.")
        elif score >= 50:
            st.warning("⚠️ Moderate match — some skills may be missing.")
        else:
            st.error("⚡ Low match — significant gaps with the JD.")

        # Show text preview in expanders
        with st.expander("📄 View Extracted Resume Text (Preview)"):
            st.text_area(
                "Resume Content",
                resume_text_raw[:1000] + ("..." if len(resume_text_raw) > 1000 else ""),
                height=200,
                disabled=True
            )

        with st.expander("📋 View Extracted Job Description Text (Preview)"):
            st.text_area(
                "Job Description Content",
                jd_text_raw[:1000] + ("..." if len(jd_text_raw) > 1000 else ""),
                height=200,
                disabled=True
            )

        # Additional stats
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Resume Length", f"{len(resume_text.split())} words")
        with col2:
            st.metric("JD Length", f"{len(jd_text.split())} words")

    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        st.info("💡 Please try again. If the problem persists, contact support.")
        logger.error(f"Unexpected error in main app: {str(e)}")

else:
    # Show helpful information when files aren't uploaded
    if not resume_file and not jd_file:
        st.info("👆 Please upload both a resume (PDF) and a job description (TXT) to begin.")
    elif not resume_file:
        st.info("👆 Please upload a resume (PDF) to continue.")
    elif not jd_file:
        st.info("👆 Please upload a job description (TXT) to continue.")

# Footer
st.divider()
st.caption("💡 Tip: For best results, ensure your resume PDF contains selectable text and your job description is clearly formatted.")
