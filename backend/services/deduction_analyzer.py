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
        "section_80c": 150000,        # Rs. 1.5 Lakh - Investments
        "section_80ccd_1": 150000,    # Rs. 1.5 Lakh - NPS (counted in 80C)
        "section_80d": 25000,         # Rs. 25,000 - Health Insurance (self + family)
        "section_80d_senior": 50000,  # Rs. 50,000 - Health Insurance (senior citizen)
        "section_80ccd_1b": 50000,    # Rs. 50,000 - NPS additional
        "section_80e": None,          # No limit - Education Loan Interest
        "section_80g": None,          # 50% or 100% - Charitable Donations
        "section_80tta": 10000,       # Rs. 10,000 - Savings Account Interest
        "section_80ttb": 50000,       # Rs. 50,000 - Senior Citizen Interest
        "section_24b": 200000,        # Rs. 2 Lakh - Home Loan Interest
        "section_80ee": 150000,       # Rs. 1.5 Lakh - First-time Homebuyer
        "section_80gg": 60000,        # Rs. 60,000 (5000 x 12) - Rent (no HRA)
        "hra": None                   # HRA depends on salary, rent, and location
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
            
            # Analyze Section 80E - Education Loan Interest
            sec80e_claimed = deductions.get("section_80e", 0)
            if sec80e_claimed > 0:
                analysis["claimed_deductions"]["section_80e"] = {
                    "claimed": sec80e_claimed,
                    "max_limit": "No limit",
                    "available": 0,
                    "note": "No upper limit on education loan interest deduction"
                }
            
            # Analyze Section 80G - Charitable Donations
            sec80g_claimed = deductions.get("section_80g", 0)
            if sec80g_claimed > 0:
                analysis["claimed_deductions"]["section_80g"] = {
                    "claimed": sec80g_claimed,
                    "note": "50% or 100% deduction based on charity type"
                }
            
            # Analyze Section 24B - Home Loan Interest
            sec24b_claimed = deductions.get("section_24b", 0)
            sec24b_max = self.MAX_LIMITS["section_24b"]
            sec24b_available = max(0, sec24b_max - sec24b_claimed)
            
            analysis["claimed_deductions"]["section_24b"] = {
                "claimed": sec24b_claimed,
                "max_limit": sec24b_max,
                "available": sec24b_available,
                "utilization_percent": (sec24b_claimed / sec24b_max * 100) if sec24b_max > 0 else 0
            }
            
            if sec24b_available > 0:
                analysis["unclaimed_opportunities"].append({
                    "section": "24B",
                    "description": "Home Loan Interest Deduction - Get Form 12BA from your lender",
                    "available_amount": sec24b_available,
                    "potential_tax_saving": sec24b_available * 0.30
                })
            
            # Analyze Section 80EE - First-time Homebuyer
            sec80ee_claimed = deductions.get("section_80ee", 0)
            sec80ee_max = self.MAX_LIMITS["section_80ee"]
            sec80ee_available = max(0, sec80ee_max - sec80ee_claimed)
            
            if sec80ee_available > 0:
                analysis["unclaimed_opportunities"].append({
                    "section": "80EE",
                    "description": "First-time Homebuyer Additional Deduction - Up to ₹1.5 Lakh (beyond 24B)",
                    "available_amount": sec80ee_available,
                    "potential_tax_saving": sec80ee_available * 0.30
                })
            
            # Analyze Section 80GG - Rent (no HRA)
            sec80gg_claimed = deductions.get("section_80gg", 0)
            sec80gg_max = self.MAX_LIMITS["section_80gg"]
            sec80gg_available = max(0, sec80gg_max - sec80gg_claimed)
            
            if sec80gg_available > 0 and hra_claimed == 0:
                analysis["unclaimed_opportunities"].append({
                    "section": "80GG",
                    "description": "Rent Deduction (when HRA not received) - Lowest of: Rent-10% income, 25% income, ₹5000/month",
                    "available_amount": sec80gg_available,
                    "potential_tax_saving": sec80gg_available * 0.30
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
            
            if section == "24B" and available > 0:
                recommendations.append(
                    f"Claim home loan interest deduction of up to ₹{available:,.0f} under Section 24B. "
                    f"This can save up to ₹{saving:,.0f} in taxes. Get Form 12BA from your lender."
                )
            
            if section == "80EE" and available > 0:
                recommendations.append(
                    f"As a first-time homebuyer, claim additional deduction of ₹{available:,.0f} under Section 80EE "
                    f"to save up to ₹{saving:,.0f} in taxes."
                )
            
            if section == "80GG" and available > 0:
                recommendations.append(
                    f"Since you're not receiving HRA, claim rent deduction of up to ₹{available:,.0f} under Section 80GG. "
                    f"Keep rent receipts and agreement for proof."
                )
        
        return recommendations

