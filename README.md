# Personalized Tax Regime Recommendation System

An intelligent income tax advisory system powered by Deep Learning and Large Language Models (LLMs) to deliver accurate, personalized, and explainable tax recommendations.

## Features

- **OCR-based Form-16 Extraction**: Automatically extracts structured data from Form-16 documents
- **Tax Regime Comparison**: Compares Old vs New tax regimes
- **Deduction Analysis**: Identifies claimed and unclaimed deductions (80C, 80D, 80CCD(1B), HRA)
- **AI-Powered Recommendations**: LLM-generated explanations with legal references
- **User-Friendly Interface**: Seamless web interface for document upload and results

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **OCR**: EasyOCR
- **LLM**: OpenAI API (configurable for local models)
- **Database**: SQLite (local), PostgreSQL (cloud-ready)

## Project Structure

```
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── requirements.txt  # Python dependencies
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional for local models)
```

5. Run the server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

## Usage

1. Start the backend server (runs on http://localhost:8000)
2. Start the frontend (runs on http://localhost:3000)
3. Upload Form-16 document
4. View personalized tax recommendations

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

