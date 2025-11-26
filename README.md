# 📄 Resume ↔ Job Match Scorer (MVP)

A simple Streamlit app that compares a **resume (PDF)** to a **job description (TXT)** and scores how well they match using NLP embeddings.

---

## 🚀 Features
- Upload resume + JD  
- Extract and clean text  
- Generate embeddings (MiniLM)  
- Compute cosine similarity  
- Output a 0–100% match score

---
## 🧠 Tech Stack
- Streamlit  
- sentence-transformers (`all-MiniLM-L6-v2`)  
- scikit-learn  
- pdfplumber  

---

## ▶️ Run the App
```bash
pip install -r requirements.txt
streamlit run app.py