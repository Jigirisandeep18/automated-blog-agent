# Automated Blog Generation Agent

## 🚀 Project Overview

This project automates the process of generating SEO-friendly and LLM-optimized blog posts from structured inputs in an Excel file.  
It supports data ingestion, blog generation, and output storage to Google Sheets, using **mock mode** for local development and testing.

---

## ✅ Features

- Read structured input from Excel sheets
- Clean and flatten data (SEO keywords, LLM keywords, deeplinks, topics)
- Generate blog content in Markdown format (mock mode by default)
- Save blog files and metadata locally
- Append blogs to Google Sheets via API
- Docker-ready (containerization steps pending)
- CI/CD workflow (GitHub Actions)

---

## ⚡ Prerequisites

- Python 3.9+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
