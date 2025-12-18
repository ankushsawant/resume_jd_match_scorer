import logging

import streamlit as st

from utils import extract_text_from_pdf, extract_text_from_txt, clean_text, compute_similarity
from config import (
    PAGE_TITLE,
    PAGE_ICON,
    APP_TITLE,
    APP_INSTRUCTION,
    MAX_FILE_SIZE,
    TEXT_PREVIEW_CHAR_LIMIT,
    STRONG_MATCH_THRESHOLD,
    MODERATE_MATCH_THRESHOLD,
    ALLOWED_RESUME_TYPES,
    ALLOWED_JD_TYPES,
    MIN_WORD_COUNT,
    MIN_CHAR_COUNT,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

st.title(APP_TITLE)
st.write(APP_INSTRUCTION)

# Initialize session state for uploader key
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# File uploaders
resume_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=ALLOWED_RESUME_TYPES,
    key=f"resume_{st.session_state.uploader_key}"
)
jd_file = st.file_uploader(
    "Upload Job Description (TXT)",
    type=ALLOWED_JD_TYPES,
    key=f"jd_{st.session_state.uploader_key}"
)

# Validate and process files
if resume_file and jd_file:
    try:
        # Validate file sizes
        if resume_file.size > MAX_FILE_SIZE:
            st.error(f"❌ Resume file is too large ({resume_file.size / (1024*1024):.2f} MB). Maximum allowed size is {MAX_FILE_SIZE / (1024*1024):.0f} MB.")
            st.info("💡 **Suggestions:**\n"
                   "- Compress your PDF using online tools like [Smallpdf](https://smallpdf.com/compress-pdf) or Adobe Acrobat\n"
                   "- Remove unnecessary images or pages from the PDF\n"
                   "- Convert the PDF to a simpler format and re-export")
            logger.warning(f"Resume file too large: {resume_file.size} bytes")
            st.stop()

        if jd_file.size > MAX_FILE_SIZE:
            st.error(f"❌ Job description file is too large ({jd_file.size / (1024*1024):.2f} MB). Maximum allowed size is {MAX_FILE_SIZE / (1024*1024):.0f} MB.")
            st.info("💡 **Suggestion:** Reduce the file size by removing unnecessary content or formatting.")
            logger.warning(f"JD file too large: {jd_file.size} bytes")
            st.stop()

        if resume_file.size == 0:
            st.error("❌ Resume file is empty. Please upload a valid PDF file.")
            st.info("💡 **Suggestion:** Ensure your file was saved correctly before uploading.")
            st.stop()

        if jd_file.size == 0:
            st.error("❌ Job description file is empty. Please upload a valid TXT file.")
            st.info("💡 **Suggestion:** Ensure your file contains text and was saved correctly.")
            st.stop()

        with st.spinner("Processing files..."):
            # Extract text from resume
            try:
                resume_text_raw = extract_text_from_pdf(resume_file)
                logger.info("Resume text extracted successfully")

                # Check if PDF might be scanned (very low character count)
                if len(resume_text_raw.strip()) < MIN_CHAR_COUNT:
                    st.warning(f"⚠️ Your resume appears to contain very little text ({len(resume_text_raw.strip())} characters). It may be a scanned image.")
                    st.info("💡 **Suggestions:**\n"
                           "- Use OCR (Optical Character Recognition) to convert scanned images to text\n"
                           "- Try online tools like [Adobe Acrobat OCR](https://www.adobe.com/acrobat/online/pdf-to-text.html) or [OnlineOCR](https://www.onlineocr.net/)\n"
                           "- Re-create the resume as a native PDF with selectable text")
                    logger.warning(f"Resume has very few characters: {len(resume_text_raw.strip())}")
                    st.stop()

            except ValueError as ve:
                st.error(f"❌ Resume Error: {str(ve)}")
                st.info("💡 **Suggestions:**\n"
                       "- Ensure your PDF contains selectable text (not just scanned images)\n"
                       "- Try opening and re-saving the PDF in a PDF reader\n"
                       "- Convert the PDF using [Zamzar](https://www.zamzar.com/) or similar tools\n"
                       "- Check if the PDF is password-protected or corrupted")
                logger.error(f"Resume extraction failed: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Failed to process resume: {str(e)}")
                st.info("💡 **Suggestions:**\n"
                       "- Try re-saving your PDF using a different PDF editor\n"
                       "- Convert to PDF from the original document format\n"
                       "- Ensure the file is not corrupted by opening it in a PDF reader first")
                logger.error(f"Resume processing error: {str(e)}")
                st.stop()

            # Extract text from job description
            try:
                jd_text_raw = extract_text_from_txt(jd_file)
                logger.info("JD text extracted successfully")
            except ValueError as ve:
                st.error(f"❌ Job Description Error: {str(ve)}")
                st.info("💡 **Suggestions:**\n"
                       "- Ensure your file is saved as plain text (.txt)\n"
                       "- Copy the content and create a new text file\n"
                       "- Check that the file actually contains the job description text")
                logger.error(f"JD extraction failed: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Failed to process job description: {str(e)}")
                st.info("💡 **Suggestions:**\n"
                       "- Ensure your file is a valid text file with UTF-8 or standard encoding\n"
                       "- Try re-saving the file with UTF-8 encoding\n"
                       "- Copy the text into a new .txt file created in Notepad or TextEdit")
                logger.error(f"JD processing error: {str(e)}")
                st.stop()

            # Clean texts
            try:
                resume_text = clean_text(resume_text_raw)
                jd_text = clean_text(jd_text_raw)
                logger.info("Text cleaning completed")

                # Validate minimum word count for meaningful analysis
                resume_word_count = len(resume_text.split())
                jd_word_count = len(jd_text.split())

                if resume_word_count < MIN_WORD_COUNT:
                    st.warning(f"⚠️ Resume contains very few words ({resume_word_count} words). Minimum recommended: {MIN_WORD_COUNT} words.")
                    st.info("💡 **Suggestion:** Ensure your resume has sufficient content for accurate matching. A typical resume should have at least 100-200 words.")
                    logger.warning(f"Resume word count too low: {resume_word_count}")

                if jd_word_count < MIN_WORD_COUNT:
                    st.warning(f"⚠️ Job description contains very few words ({jd_word_count} words). Minimum recommended: {MIN_WORD_COUNT} words.")
                    st.info("💡 **Suggestion:** Ensure the job description has sufficient detail for accurate matching.")
                    logger.warning(f"JD word count too low: {jd_word_count}")

            except ValueError as ve:
                st.error(f"❌ Text Processing Error: {str(ve)}")
                st.info("💡 **Suggestion:** The extracted text may be empty or contain only special characters. Please check your source files.")
                logger.error(f"Text cleaning failed: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Failed to clean text: {str(e)}")
                st.info("💡 **Suggestion:** There was an unexpected error processing the text. Please try again or contact support.")
                logger.error(f"Text cleaning error: {str(e)}")
                st.stop()

            # Compute similarity
            try:
                score = compute_similarity(resume_text, jd_text)
                logger.info(f"Similarity score computed: {score}")
            except RuntimeError as re:
                st.error(f"❌ Model Error: {str(re)}")
                st.info("💡 **Troubleshooting Steps:**\n"
                       "1. Restart the application\n"
                       "2. Check your internet connection (model may need to download)\n"
                       "3. Clear the Hugging Face cache: `~/.cache/huggingface/`\n"
                       "4. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`")
                logger.error(f"Model error: {str(re)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Failed to compute similarity: {str(e)}")
                st.info("💡 **Suggestion:** An unexpected error occurred during similarity computation. Please try again or check the logs for details.")
                logger.error(f"Similarity computation error: {str(e)}")
                st.stop()

        # Display results
        st.success(f"✅ Match Score: **{score}%**")

        # Provide contextual feedback
        if score >= STRONG_MATCH_THRESHOLD:
            st.balloons()
            st.info("🎉 Strong match! The resume aligns well with the JD.")
        elif score >= MODERATE_MATCH_THRESHOLD:
            st.warning("⚠️ Moderate match — some skills may be missing.")
        else:
            st.error("⚡ Low match — significant gaps with the JD.")

        # Show text preview in expanders
        with st.expander("📄 View Extracted Resume Text (Preview)"):
            st.text_area(
                "Resume Content",
                resume_text_raw[:TEXT_PREVIEW_CHAR_LIMIT] + ("..." if len(resume_text_raw) > TEXT_PREVIEW_CHAR_LIMIT else ""),
                height=200,
                disabled=True
            )

        with st.expander("📋 View Extracted Job Description Text (Preview)"):
            st.text_area(
                "Job Description Content",
                jd_text_raw[:TEXT_PREVIEW_CHAR_LIMIT] + ("..." if len(jd_text_raw) > TEXT_PREVIEW_CHAR_LIMIT else ""),
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

        # Reset button - allows users to start a new comparison
        st.divider()
        if st.button("🔄 Reset & Start New Comparison", type="primary", use_container_width=True):
            # Increment uploader key to force file uploaders to clear
            st.session_state.uploader_key += 1
            # Rerun the app
            st.rerun()

    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        st.info("💡 **Troubleshooting:**\n"
               "- Try uploading your files again\n"
               "- Restart the application\n"
               "- Check that your files are not corrupted\n"
               "- If the issue persists, please report it with the error details above")
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
