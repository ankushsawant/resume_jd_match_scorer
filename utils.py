from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
import re

# Load model once globally
model = SentenceTransformer('all-MiniLM-L6-v2')


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_text_from_txt(file):
    return file.read().decode("utf-8")

def get_embedding(text):
    return model.encode([text])

def compute_similarity(text1, text2):
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    sim = cosine_similarity(emb1, emb2)[0][0]
    return round(sim * 100, 2)  # score in 0–100