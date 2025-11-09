# Backend API

FastAPI-based backend for the Tax Regime Recommendation System.

## Features

- **OCR Service**: Extracts data from Form-16 documents using EasyOCR
- **Tax Calculator**: Calculates tax under Old and New regimes
- **Deduction Analyzer**: Identifies claimed and unclaimed deductions
- **LLM Service**: Generates personalized recommendations (OpenAI or rule-based)

## API Endpoints

### Health Check
```
GET /health
```

### Analyze Form-16
```
POST /api/analyze-form16
Content-Type: multipart/form-data

Body: file (PDF or image)
```

### Calculate Tax
```
POST /api/calculate-tax
Content-Type: application/json

Body: {
  "gross_salary": 1000000,
  "deductions": {
    "section_80c": 150000,
    "section_80d": 25000,
    ...
  }
}
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

If `OPENAI_API_KEY` is not set, the system will use rule-based recommendations.

## Running the Server

```bash
uvicorn main:app --reload
```

Server runs on `http://localhost:8000`

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

