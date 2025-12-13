from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model once globally
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    model = None


def extract_text_from_pdf(file):
    """
    Extract text from a PDF file.

    Args:
        file: File-like object (uploaded PDF)

    Returns:
        str: Extracted text from the PDF

    Raises:
        ValueError: If PDF is empty or corrupted
        Exception: For other PDF processing errors
    """
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            if len(pdf.pages) == 0:
                raise ValueError("PDF file is empty (no pages found)")

            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "

        if not text.strip():
            raise ValueError("PDF file contains no readable text")

        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text

    except ValueError as ve:
        logger.error(f"PDF validation error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to process PDF file: {str(e)}")


def clean_text(text):
    """
    Clean and normalize text.

    Args:
        text: Raw text string

    Returns:
        str: Cleaned text

    Raises:
        ValueError: If text is empty or invalid
    """
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        if not text:
            raise ValueError("Text is empty after cleaning")

        return text

    except ValueError as ve:
        logger.error(f"Text cleaning error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during text cleaning: {str(e)}")
        raise Exception(f"Failed to clean text: {str(e)}")


def extract_text_from_txt(file):
    """
    Extract text from a TXT file.

    Args:
        file: File-like object (uploaded TXT)

    Returns:
        str: Decoded text from the file

    Raises:
        ValueError: If file is empty
        UnicodeDecodeError: If file encoding is invalid
        Exception: For other file processing errors
    """
    try:
        content = file.read()

        if not content:
            raise ValueError("TXT file is empty")

        # Try UTF-8 first, fallback to other encodings
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 decoding failed, trying latin-1")
            try:
                text = content.decode("latin-1")
            except UnicodeDecodeError:
                logger.warning("latin-1 decoding failed, trying cp1252")
                text = content.decode("cp1252", errors='ignore')

        if not text.strip():
            raise ValueError("TXT file contains no readable text")

        logger.info(f"Successfully extracted {len(text)} characters from TXT")
        return text

    except ValueError as ve:
        logger.error(f"TXT validation error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {str(e)}")
        raise Exception(f"Failed to process TXT file: {str(e)}")


def get_embedding(text):
    """
    Generate embedding for text using the sentence transformer model.

    Args:
        text: Text string to encode

    Returns:
        numpy.ndarray: Text embedding

    Raises:
        RuntimeError: If model is not loaded
        ValueError: If text is empty
        Exception: For other encoding errors
    """
    try:
        if model is None:
            raise RuntimeError("Model not loaded. Please restart the application.")

        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        if len(text.strip()) == 0:
            raise ValueError("Text is empty after stripping whitespace")

        embedding = model.encode([text])
        logger.info(f"Generated embedding with shape {embedding.shape}")
        return embedding

    except (RuntimeError, ValueError) as e:
        logger.error(f"Embedding generation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during embedding generation: {str(e)}")
        raise Exception(f"Failed to generate embedding: {str(e)}")


def compute_similarity(text1, text2):
    """
    Compute semantic similarity between two texts.

    Args:
        text1: First text string
        text2: Second text string

    Returns:
        float: Similarity score between 0-100

    Raises:
        ValueError: If texts are invalid
        Exception: For other computation errors
    """
    try:
        if not text1 or not text2:
            raise ValueError("Both texts must be non-empty")

        emb1 = get_embedding(text1)
        emb2 = get_embedding(text2)

        sim = cosine_similarity(emb1, emb2)[0][0]
        score = round(sim * 100, 2)

        logger.info(f"Computed similarity score: {score}")
        return score

    except ValueError as ve:
        logger.error(f"Similarity computation error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during similarity computation: {str(e)}")
        raise Exception(f"Failed to compute similarity: {str(e)}")