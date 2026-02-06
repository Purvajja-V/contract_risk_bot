# Contract Risk Analysis Bot

## Problem Statement
Manual contract review is time-consuming and error-prone. Organizations often miss risky clauses such as indemnity, liability, termination, and compliance issues.

## Solution
This project is a Streamlit-based AI application that analyzes uploaded contract PDFs and identifies potential risky clauses using Natural Language Processing (NLP).

## Features
- Upload contract PDF documents
- Sentence tokenization using NLTK
- Named Entity Recognition (NER)
- Detection of risky clauses (Indemnity, Liability, Termination, etc.)
- Risk scoring and categorization
- PDF report generation

## Tech Stack
- Python
- Streamlit
- NLTK
- spaCy
- PyPDF2
- python-docx
- FPDF

## How to Run
```bash
pip install -r requirements.txt
streamlit run main.py
