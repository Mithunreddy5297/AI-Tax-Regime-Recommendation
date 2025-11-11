import os
from typing import Dict, List, Optional
import logging
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service for generating tax recommendations and explanations
    Uses Google Gemini API by default, can be configured for other models
    """
    
    def __init__(self):
        """Initialize LLM service"""
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        # Check if API key is valid (not empty and not placeholder)
        self.use_gemini = bool(
            self.api_key and 
            self.api_key != "your_gemini_api_key_here" and
            len(self.api_key) > 10 and
            GEMINI_AVAILABLE
        )
        
        if self.use_gemini:
            try:
                genai.configure(api_key=self.api_key)
                self.model_client = genai.GenerativeModel(self.model)
                logger.info(f"Google Gemini client initialized successfully with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini client: {str(e)}")
                self.use_gemini = False
                self.model_client = None
        else:
            if not GEMINI_AVAILABLE:
                logger.warning("google-generativeai package not installed. Install with: pip install google-generativeai")
            logger.warning("Google Gemini API key not found or invalid. Using rule-based recommendations.")
            self.model_client = None
    
    async def generate_recommendations(
        self,
        extracted_data: Dict,
        old_regime_tax: float,
        new_regime_tax: float,
        deductions_analysis: Dict
    ) -> Dict:
        """
        Generate personalized tax recommendations using LLM
        
        Args:
            extracted_data: Extracted Form-16 data
            old_regime_tax: Tax under old regime
            new_regime_tax: Tax under new regime
            deductions_analysis: Deduction analysis results
            
        Returns:
            Dictionary with recommendations, explanations, and legal references
        """
        if not self.use_gemini:
            # Fallback to rule-based recommendations
            return self._generate_rule_based_recommendations(
                extracted_data, old_regime_tax, new_regime_tax, deductions_analysis
            )
        
        try:
            # Prepare context for LLM
            context = self._prepare_context(
                extracted_data, old_regime_tax, new_regime_tax, deductions_analysis
            )
            
            # Generate prompt
            prompt = self._create_prompt(context)
            
            # Call Google Gemini API
            try:
                response = self.model_client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=1500
                    )
                )
                
                # Parse response
                llm_output = response.text
            except Exception as e:
                logger.error(f"Error calling Google Gemini API: {str(e)}")
                # Fallback to rule-based recommendations
                return self._generate_rule_based_recommendations(
                    extracted_data, old_regime_tax, new_regime_tax, deductions_analysis
                )
            
            # Parse JSON response
            try:
                parsed_response = json.loads(llm_output)
            except:
                # If not JSON, extract structured data
                parsed_response = self._parse_text_response(llm_output)
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error generating Gemini recommendations: {str(e)}")
            # Fallback to rule-based
            return self._generate_rule_based_recommendations(
                extracted_data, old_regime_tax, new_regime_tax, deductions_analysis
            )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM"""
        return """You are an expert tax advisor specializing in Indian Income Tax laws. 
        Provide accurate, personalized tax recommendations with legal references.
        Always cite relevant sections of the Income Tax Act, 1961.
        Be clear, concise, and actionable in your recommendations.
        Format your response as JSON with keys: recommendations (array), explanations (object), legal_references (array)."""
    
    def _prepare_context(
        self,
        extracted_data: Dict,
        old_regime_tax: float,
        new_regime_tax: float,
        deductions_analysis: Dict
    ) -> str:
        """Prepare context string for LLM"""
        context = f"""
        Taxpayer Information:
        - Gross Salary: ₹{extracted_data.get('gross_salary', 0):,.2f}
        - Taxable Income: ₹{extracted_data.get('taxable_income', 0):,.2f}
        
        Tax Calculations:
        - Old Regime Tax: ₹{old_regime_tax:,.2f}
        - New Regime Tax: ₹{new_regime_tax:,.2f}
        - Recommended Regime: {'Old Regime' if old_regime_tax < new_regime_tax else 'New Regime'}
        - Potential Savings: ₹{abs(old_regime_tax - new_regime_tax):,.2f}
        
        Deductions:
        - Section 80C: ₹{extracted_data.get('deductions', {}).get('section_80c', 0):,.2f}
        - Section 80D: ₹{extracted_data.get('deductions', {}).get('section_80d', 0):,.2f}
        - Section 80CCD(1B): ₹{extracted_data.get('deductions', {}).get('section_80ccd_1b', 0):,.2f}
        - HRA: ₹{extracted_data.get('deductions', {}).get('hra', 0):,.2f}
        
        Unclaimed Opportunities:
        {json.dumps(deductions_analysis.get('unclaimed_opportunities', []), indent=2)}
        """
        return context
    
    def _create_prompt(self, context: str) -> str:
        """Create user prompt for LLM"""
        return f"""
        Based on the following tax information, provide personalized recommendations:
        
        {context}
        
        Please provide:
        1. Top 3-5 actionable recommendations to optimize tax savings
        2. Detailed explanations for why the recommended regime is better
        3. Legal references (sections of Income Tax Act, 1961)
        4. Specific suggestions for unclaimed deductions
        
        Format your response as JSON:
        {{
            "recommendations": ["rec1", "rec2", ...],
            "explanations": {{
                "regime_recommendation": "explanation text",
                "deduction_optimization": "explanation text"
            }},
            "legal_references": ["Section 80C", "Section 80D", ...]
        }}
        """
    
    def _parse_text_response(self, text: str) -> Dict:
        """Parse text response if JSON parsing fails"""
        return {
            "recommendations": [text[:200] + "..."] if text else [],
            "explanations": {
                "regime_recommendation": text[:500] if text else "",
                "deduction_optimization": ""
            },
            "legal_references": ["Section 80C", "Section 80D", "Section 80CCD(1B)"]
        }
    
    def _generate_rule_based_recommendations(
        self,
        extracted_data: Dict,
        old_regime_tax: float,
        new_regime_tax: float,
        deductions_analysis: Dict
    ) -> Dict:
        """Generate rule-based recommendations as fallback"""
        recommendations = []
        explanations = {}
        legal_references = []
        
        # Regime recommendation
        if old_regime_tax < new_regime_tax:
            recommended = "Old Regime"
            savings = new_regime_tax - old_regime_tax
            recommendations.append(
                f"Choose Old Regime to save ₹{savings:,.2f} in taxes. "
                "You have significant deductions that make the old regime more beneficial."
            )
            explanations["regime_recommendation"] = (
                f"The Old Regime is more beneficial because your deductions "
                f"(Section 80C, 80D, HRA, etc.) reduce your taxable income significantly, "
                f"resulting in ₹{savings:,.2f} lower tax liability compared to the New Regime."
            )
        else:
            recommended = "New Regime"
            savings = old_regime_tax - new_regime_tax
            recommendations.append(
                f"Choose New Regime to save ₹{savings:,.2f} in taxes. "
                "The lower tax slabs in the new regime benefit you more."
            )
            explanations["regime_recommendation"] = (
                f"The New Regime offers lower tax rates with simplified slabs. "
                f"Even without deductions, you save ₹{savings:,.2f} compared to the Old Regime."
            )
        
        # Deduction recommendations
        unclaimed = deductions_analysis.get("unclaimed_opportunities", [])
        if unclaimed:
            recommendations.append(
                f"You have {len(unclaimed)} unclaimed deduction opportunities. "
                "Consider maximizing these to further reduce your tax liability."
            )
            explanations["deduction_optimization"] = (
                "Review the unclaimed deductions section for specific investment "
                "and insurance opportunities that can reduce your taxable income."
            )
        
        # Legal references
        legal_references = [
            "Section 80C - Deduction for investments in specified instruments",
            "Section 80D - Deduction for health insurance premium",
            "Section 80CCD(1B) - Additional deduction for NPS contribution",
            "Section 10(13A) - House Rent Allowance exemption"
        ]
        
        return {
            "recommendations": recommendations,
            "explanations": explanations,
            "legal_references": legal_references
        }

