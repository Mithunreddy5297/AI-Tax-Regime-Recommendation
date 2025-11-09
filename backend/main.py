from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from services.ocr_service import OCRService
from services.tax_calculator import TaxCalculator
from services.deduction_analyzer import DeductionAnalyzer
from services.llm_service import LLMService
from services.hra_calculator import HRACalculator

app = FastAPI(
    title="Tax Regime Recommendation API",
    description="AI-powered tax advisory system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_service = OCRService()
tax_calculator = TaxCalculator()
deduction_analyzer = DeductionAnalyzer()
llm_service = LLMService()


class ManualEntryRequest(BaseModel):
    age_group: str = "below_60"  # below_60, 60_80, above_80
    gross_salary: float
    deductions: Dict = {}

class TaxRecommendationResponse(BaseModel):
    extracted_data: Dict
    old_regime_tax: float
    new_regime_tax: float
    recommended_regime: str
    savings: float
    deductions_analysis: Dict
    recommendations: List[str]
    explanations: Dict
    legal_references: List[str]

class RealTimeTaxResponse(BaseModel):
    old_regime_tax: float
    new_regime_tax: float
    recommended_regime: str
    savings: float
    taxable_income_old: float
    taxable_income_new: float
    total_deductions: float
    deductions_analysis: Dict
    tax_breakdown: Dict


@app.get("/")
async def root():
    return {"message": "Tax Regime Recommendation API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/analyze-form16", response_model=TaxRecommendationResponse)
async def analyze_form16(file: UploadFile = File(...)):
    """
    Analyze Form-16 document and provide tax recommendations
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/') and file.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image or PDF.")
        
        # Read file content
        contents = await file.read()
        
        # Step 1: OCR - Extract data from Form-16
        extracted_data = await ocr_service.extract_form16_data(contents, file.content_type)
        
        if not extracted_data:
            raise HTTPException(status_code=400, detail="Failed to extract data from Form-16")
        
        # Step 2: Calculate tax under both regimes
        old_regime_tax = tax_calculator.calculate_old_regime(extracted_data)
        new_regime_tax = tax_calculator.calculate_new_regime(extracted_data)
        
        # Step 3: Determine recommended regime
        recommended_regime = "Old Regime" if old_regime_tax < new_regime_tax else "New Regime"
        savings = abs(old_regime_tax - new_regime_tax)
        
        # Step 4: Analyze deductions
        deductions_analysis = deduction_analyzer.analyze_deductions(extracted_data)
        
        # Step 5: Generate LLM recommendations
        llm_response = await llm_service.generate_recommendations(
            extracted_data=extracted_data,
            old_regime_tax=old_regime_tax,
            new_regime_tax=new_regime_tax,
            deductions_analysis=deductions_analysis
        )
        
        return TaxRecommendationResponse(
            extracted_data=extracted_data,
            old_regime_tax=round(old_regime_tax, 2),
            new_regime_tax=round(new_regime_tax, 2),
            recommended_regime=recommended_regime,
            savings=round(savings, 2),
            deductions_analysis=deductions_analysis,
            recommendations=llm_response.get("recommendations", []),
            explanations=llm_response.get("explanations", {}),
            legal_references=llm_response.get("legal_references", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/calculate-tax")
async def calculate_tax(income_data: Dict):
    """
    Calculate tax for given income data (for testing/manual input)
    """
    try:
        old_regime_tax = tax_calculator.calculate_old_regime(income_data)
        new_regime_tax = tax_calculator.calculate_new_regime(income_data)
        
        return {
            "old_regime_tax": round(old_regime_tax, 2),
            "new_regime_tax": round(new_regime_tax, 2),
            "recommended_regime": "Old Regime" if old_regime_tax < new_regime_tax else "New Regime",
            "savings": round(abs(old_regime_tax - new_regime_tax), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate-tax-realtime", response_model=RealTimeTaxResponse)
async def calculate_tax_realtime(request: ManualEntryRequest):
    """
    Real-time tax calculation for manual entry form
    Returns comprehensive tax analysis with breakdown
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Received request: age_group={request.age_group}, gross_salary={request.gross_salary}")
        logger.info(f"Deductions: {request.deductions}")
        # Prepare income data
        income_data = {
            "age_group": request.age_group,
            "gross_salary": request.gross_salary,
            "deductions": request.deductions
        }
        
        # Calculate taxes
        old_regime_tax = tax_calculator.calculate_old_regime(income_data)
        new_regime_tax = tax_calculator.calculate_new_regime(income_data)
        
        # Determine recommended regime
        recommended_regime = "Old Regime" if old_regime_tax < new_regime_tax else "New Regime"
        savings = abs(old_regime_tax - new_regime_tax)
        
        # Calculate taxable income
        deductions = request.deductions
        standard_deduction = deductions.get("standard_deduction", 50000)
        
        # Calculate HRA exemption if HRA details are provided
        hra_exemption = 0
        hra_basic = deductions.get("hra_basic_salary", 0) or 0
        hra_received = deductions.get("hra_received", 0) or 0
        rent_paid = deductions.get("rent_paid", 0) or 0
        
        # Convert to float if string
        try:
            hra_basic = float(hra_basic) if hra_basic else 0
            hra_received = float(hra_received) if hra_received else 0
            rent_paid = float(rent_paid) if rent_paid else 0
        except (ValueError, TypeError):
            hra_basic = hra_received = rent_paid = 0
        
        if hra_basic > 0 and hra_received > 0 and rent_paid > 0:
            is_metro = deductions.get("is_metro", False)
            if isinstance(is_metro, str):
                is_metro = is_metro.lower() in ['true', '1', 'yes']
            hra_exemption = HRACalculator.calculate_hra_exemption(
                basic_salary=hra_basic,
                hra_received=hra_received,
                rent_paid=rent_paid,
                is_metro=bool(is_metro)
            )
        else:
            # Fallback to direct HRA value if provided
            hra_exemption = float(deductions.get("hra", 0) or 0)
        
        # Convert all deduction values to float
        def safe_float(value, default=0):
            try:
                return float(value) if value else default
            except (ValueError, TypeError):
                return default
        
        # Old regime deductions
        total_deductions_old = (
            safe_float(deductions.get("section_80c", 0)) +
            safe_float(deductions.get("section_80d", 0)) +
            safe_float(deductions.get("section_80ccd_1b", 0)) +
            safe_float(deductions.get("section_80g", 0)) +
            safe_float(deductions.get("section_80tta", 0)) +
            safe_float(deductions.get("section_80ttb", 0)) +
            hra_exemption +
            safe_float(deductions.get("section_24b", 0)) +
            safe_float(deductions.get("other_deductions", 0)) +
            safe_float(standard_deduction)
        )
        
        taxable_income_old = max(0, request.gross_salary - total_deductions_old)
        taxable_income_new = max(0, request.gross_salary - standard_deduction)
        
        # Analyze deductions
        deductions_analysis = deduction_analyzer.analyze_deductions(income_data)
        
        # Get tax breakdown
        old_breakdown = tax_calculator.get_tax_breakdown(income_data, "old")
        new_breakdown = tax_calculator.get_tax_breakdown(income_data, "new")
        
        return RealTimeTaxResponse(
            old_regime_tax=round(old_regime_tax, 2),
            new_regime_tax=round(new_regime_tax, 2),
            recommended_regime=recommended_regime,
            savings=round(savings, 2),
            taxable_income_old=round(taxable_income_old, 2),
            taxable_income_new=round(taxable_income_new, 2),
            total_deductions=round(total_deductions_old, 2),
            deductions_analysis=deductions_analysis,
            tax_breakdown={
                "old_regime": old_breakdown,
                "new_regime": new_breakdown
            }
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error in calculate_tax_realtime: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Error calculating tax: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

