# 📄 Resume ↔ Job Match Scorer

A Streamlit app that compares a **resume (PDF)** to a **job description (TXT)** and scores how well they match using NLP embeddings.

---

## 🚀 Features
- Upload resume (PDF) + job description (TXT)
- Extract and clean text with robust error handling
- Generate semantic embeddings using MiniLM
- Compute cosine similarity score (0–100%)
- Visual feedback with match quality indicators
- Text preview, word count metrics, and easy reset functionality
- File validation (size limits, encoding detection)

---

## 🧠 Tech Stack
- **Streamlit** — UI framework
- **sentence-transformers** (`all-MiniLM-L6-v2`) — semantic embeddings
- **scikit-learn** — cosine similarity computation
- **pdfplumber** — PDF text extraction
- **logging** — comprehensive error tracking

---

## ▶️ Run the App

### Option 1: Local Installation
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Option 2: Docker
**Build the image:**
```bash
docker build -t resume-jd-matcher .
```

**Run the container:**
```bash
docker run -p 8501:8501 resume-jd-matcher
```

**Access the app:**
Open your browser to `http://localhost:8501`

**Stop the container:**
```bash
docker ps  # Find container ID
docker stop <container-id>
```