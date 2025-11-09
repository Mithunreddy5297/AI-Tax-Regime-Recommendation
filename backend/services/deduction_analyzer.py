from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeductionAnalyzer:
    """
    Analyzes deductions and identifies unclaimed opportunities
    """
    
    # Maximum limits for deductions (FY 2023-24)
    MAX_LIMITS = {
        "section_80c": 150000,  # Rs. 1.5 Lakh
        "section_80d": 25000,   # Rs. 25,000 (self + family)
        "section_80d_senior": 50000,  # Rs. 50,000 (if senior citizen)
        "section_80ccd_1b": 50000,  # Rs. 50,000 (NPS additional)
        "section_80g": None,  # 50% or 100% of donation (varies)
        "section_80tta": 10000,  # Rs. 10,000 (interest from savings)
        "section_80ttb": 50000,  # Rs. 50,000 (senior citizens - interest income)
        "section_24b": 200000,  # Rs. 2 Lakh (home loan interest)
        "hra": None  # HRA depends on salary, rent, and location
    }
    
    def analyze_deductions(self, income_data: Dict) -> Dict:
        """
        Analyze claimed and unclaimed deductions
        
        Args:
            income_data: Dictionary containing income and deduction details
            
        Returns:
            Dictionary with deduction analysis
        """
        try:
            deductions = income_data.get("deductions", {})
            gross_salary = income_data.get("gross_salary", 0)
            
            analysis = {
                "claimed_deductions": {},
                "unclaimed_opportunities": [],
                "potential_savings": 0.0,
                "recommendations": []
            }
            
            # Analyze Section 80C
            sec80c_claimed = deductions.get("section_80c", 0)
            sec80c_max = self.MAX_LIMITS["section_80c"]
            sec80c_available = max(0, sec80c_max - sec80c_claimed)
            
            analysis["claimed_deductions"]["section_80c"] = {
                "claimed": sec80c_claimed,
                "max_limit": sec80c_max,
                "available": sec80c_available,
                "utilization_percent": (sec80c_claimed / sec80c_max * 100) if sec80c_max > 0 else 0
            }
            
            if sec80c_available > 0:
                analysis["unclaimed_opportunities"].append({
                    "section": "80C",
                    "description": "Investments in ELSS, PPF, NSC, Tax-saving FD, Life Insurance Premium, etc.",
                    "available_amount": sec80c_available,
                    "potential_tax_saving": sec80c_available * 0.30  # Assuming highest tax bracket
                })
            
            # Analyze Section 80D
            sec80d_claimed = deductions.get("section_80d", 0)
            sec80d_max = self.MAX_LIMITS["section_80d"]
            sec80d_available = max(0, sec80d_max - sec80d_claimed)
            
            analysis["claimed_deductions"]["section_80d"] = {
                "claimed": sec80d_claimed,
                "max_limit": sec80d_max,
                "available": sec80d_available,
                "utilization_percent": (sec80d_claimed / sec80d_max * 100) if sec80d_max > 0 else 0
            }
            
            if sec80d_available > 0:
                analysis["unclaimed_opportunities"].append({
                    "section": "80D",
                    "description": "Health Insurance Premium for self, spouse, children, and parents",
                    "available_amount": sec80d_available,
                    "potential_tax_saving": sec80d_available * 0.30
                })
            
            # Analyze Section 80CCD(1B) - NPS
            sec80ccd_claimed = deductions.get("section_80ccd_1b", 0)
            sec80ccd_max = self.MAX_LIMITS["section_80ccd_1b"]
            sec80ccd_available = max(0, sec80ccd_max - sec80ccd_claimed)
            
            analysis["claimed_deductions"]["section_80ccd_1b"] = {
                "claimed": sec80ccd_claimed,
                "max_limit": sec80ccd_max,
                "available": sec80ccd_available,
                "utilization_percent": (sec80ccd_claimed / sec80ccd_max * 100) if sec80ccd_max > 0 else 0
            }
            
            if sec80ccd_available > 0:
                analysis["unclaimed_opportunities"].append({
                    "section": "80CCD(1B)",
                    "description": "Additional contribution to NPS (beyond Section 80C limit)",
                    "available_amount": sec80ccd_available,
                    "potential_tax_saving": sec80ccd_available * 0.30
                })
            
            # Analyze HRA
            hra_claimed = deductions.get("hra", 0)
            hra_analysis = self._analyze_hra(gross_salary, hra_claimed, income_data)
            
            analysis["claimed_deductions"]["hra"] = hra_analysis
            
            if hra_analysis.get("unclaimed_amount", 0) > 0:
                analysis["unclaimed_opportunities"].append({
                    "section": "HRA",
                    "description": "House Rent Allowance - Ensure proper rent receipts and agreement",
                    "available_amount": hra_analysis.get("unclaimed_amount", 0),
                    "potential_tax_saving": hra_analysis.get("unclaimed_amount", 0) * 0.30
                })
            
            # Calculate total potential savings
            analysis["potential_savings"] = sum(
                opp.get("potential_tax_saving", 0) 
                for opp in analysis["unclaimed_opportunities"]
            )
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing deductions: {str(e)}")
            return {}
    
    def _analyze_hra(self, gross_salary: float, hra_claimed: float, income_data: Dict) -> Dict:
        """
        Analyze HRA deduction
        
        HRA is calculated as minimum of:
        1. Actual HRA received
        2. Actual rent paid minus 10% of basic salary
        3. 50% of basic salary (metro) or 40% (non-metro)
        """
        # This is a simplified analysis
        # In production, you'd need actual rent, basic salary, and location data
        
        basic_salary = income_data.get("basic_salary", gross_salary * 0.5)  # Estimate if not available
        
        # Estimate maximum HRA (assuming metro city - 50%)
        max_hra_estimate = basic_salary * 0.5
        
        return {
            "claimed": hra_claimed,
            "estimated_max": max_hra_estimate,
            "unclaimed_amount": max(0, max_hra_estimate - hra_claimed),
            "note": "HRA calculation requires actual rent paid, basic salary, and location details"
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        unclaimed = analysis.get("unclaimed_opportunities", [])
        
        if not unclaimed:
            recommendations.append("Great! You have maximized your deductions. Consider reviewing your investments for better returns.")
            return recommendations
        
        for opp in unclaimed:
            section = opp.get("section", "")
            available = opp.get("available_amount", 0)
            saving = opp.get("potential_tax_saving", 0)
            
            if section == "80C" and available > 0:
                recommendations.append(
                    f"Consider investing ₹{available:,.0f} in Section 80C instruments (ELSS, PPF, NSC) "
                    f"to save up to ₹{saving:,.0f} in taxes."
                )
            
            if section == "80D" and available > 0:
                recommendations.append(
                    f"Consider health insurance premium of ₹{available:,.0f} under Section 80D "
                    f"to save up to ₹{saving:,.0f} in taxes."
                )
            
            if section == "80CCD(1B)" and available > 0:
                recommendations.append(
                    f"Consider additional NPS contribution of ₹{available:,.0f} under Section 80CCD(1B) "
                    f"to save up to ₹{saving:,.0f} in taxes."
                )
            
            if section == "HRA" and available > 0:
                recommendations.append(
                    f"Review your HRA claim. You may be eligible for additional ₹{available:,.0f} deduction. "
                    f"Ensure you have proper rent receipts and rental agreement."
                )
        
        return recommendations

