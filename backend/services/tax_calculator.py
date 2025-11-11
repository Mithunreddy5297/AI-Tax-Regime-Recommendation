from typing import Dict
import logging
from .hra_calculator import HRACalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaxCalculator:
    """
    Tax calculation engine for Old and New tax regimes
    Based on Indian Income Tax Act
    """
    
    # Old Regime Tax Slabs (FY 2023-24)
    OLD_REGIME_SLABS = [
        (0, 250000, 0),
        (250000, 500000, 0.05),
        (500000, 1000000, 0.20),
        (1000000, float('inf'), 0.30)
    ]
    
    # New Regime Tax Slabs (FY 2023-24)
    NEW_REGIME_SLABS = [
        (0, 300000, 0),
        (300000, 700000, 0.05),
        (700000, 1000000, 0.10),
        (1000000, 1200000, 0.15),
        (1200000, 1500000, 0.20),
        (1500000, float('inf'), 0.30)
    ]
    
    # Senior Citizen Tax Slabs (Old Regime) - FY 2023-24
    SENIOR_CITIZEN_OLD_SLABS = [
        (0, 300000, 0),  # Higher exemption limit
        (300000, 500000, 0.05),
        (500000, 1000000, 0.20),
        (1000000, float('inf'), 0.30)
    ]
    
    # Super Senior Citizen Tax Slabs (Old Regime) - FY 2023-24
    SUPER_SENIOR_CITIZEN_OLD_SLABS = [
        (0, 500000, 0),  # Even higher exemption limit
        (500000, 1000000, 0.20),
        (1000000, float('inf'), 0.30)
    ]
    
    # Standard Deduction (applicable in both regimes)
    STANDARD_DEDUCTION = 50000
    
    # Cess rate
    CESS_RATE = 0.04  # 4% of income tax
    
    # Health and Education Cess
    HEALTH_EDUCATION_CESS_RATE = 0.04  # 4% of income tax
    
    # Form 16 Deduction Limits (FY 2023-24)
    FORM16_DEDUCTION_LIMITS = {
        "section_80c": 150000,        # Investments
        "section_80ccd_1": 150000,    # NPS (part of 80C)
        "section_80d": 25000,         # Health Insurance
        "section_80d_senior": 50000,  # Health Insurance (Senior)
        "section_80ccd_1b": 50000,    # Additional NPS
        "section_80e": None,          # Education Loan (No limit)
        "section_80g": None,          # Charitable Donations
        "section_80tta": 10000,       # Savings Interest
        "section_80ttb": 50000,       # Senior Citizen Interest
        "section_24b": 200000,        # Home Loan Interest
        "section_80ee": 150000,       # First-time Homebuyer
        "section_80gg": 60000,        # Rent (no HRA)
        "hra": None                   # HRA (based on calculation)
    }
    
    def calculate_old_regime(self, income_data: Dict) -> float:
        """
        Calculate tax under Old Regime
        
        Args:
            income_data: Dictionary containing income and deduction details
            
        Returns:
            Total tax liability
        """
        try:
            gross_salary = income_data.get("gross_salary", 0)
            deductions = income_data.get("deductions", {})
            age_group = income_data.get("age_group", "below_60")
            
            # Helper function to safely convert to float
            def safe_float(value, default=0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default
            
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
                try:
                    hra_exemption = float(deductions.get("hra", 0) or 0)
                except (ValueError, TypeError):
                    hra_exemption = 0
            
            # Calculate total deductions (Chapter VI-A and others)
            total_deductions = (
                safe_float(deductions.get("section_80c", 0)) +
                safe_float(deductions.get("section_80ccd_1", 0)) +
                safe_float(deductions.get("section_80d", 0)) +
                safe_float(deductions.get("section_80ccd_1b", 0)) +
                safe_float(deductions.get("section_80e", 0)) +
                safe_float(deductions.get("section_80g", 0)) +
                safe_float(deductions.get("section_80tta", 0)) +
                safe_float(deductions.get("section_80ttb", 0)) +
                hra_exemption +
                safe_float(deductions.get("section_24b", 0)) +
                safe_float(deductions.get("section_80ee", 0)) +
                safe_float(deductions.get("section_80gg", 0)) +
                safe_float(deductions.get("other_deductions", 0))
            )
            
            # Standard deduction
            standard_deduction = deductions.get("standard_deduction", self.STANDARD_DEDUCTION)
            
            # Taxable income
            taxable_income = max(0, gross_salary - total_deductions - standard_deduction)
            
            # Get appropriate tax slabs based on age
            slabs = self._get_tax_slabs_by_age(self.OLD_REGIME_SLABS, age_group)
            
            # Calculate tax using old regime slabs
            tax = self._calculate_tax_by_slabs(taxable_income, slabs)
            
            # Add cess
            total_tax = tax + (tax * self.CESS_RATE)
            
            return total_tax
            
        except Exception as e:
            logger.error(f"Error calculating old regime tax: {str(e)}")
            return 0.0
    
    def calculate_new_regime(self, income_data: Dict) -> float:
        """
        Calculate tax under New Regime
        
        Args:
            income_data: Dictionary containing income and deduction details
            
        Returns:
            Total tax liability
        """
        try:
            gross_salary = income_data.get("gross_salary", 0)
            deductions = income_data.get("deductions", {})
            age_group = income_data.get("age_group", "below_60")
            
            # In new regime, only standard deduction is allowed
            standard_deduction = deductions.get("standard_deduction", self.STANDARD_DEDUCTION)
            
            # Taxable income (no other deductions in new regime)
            taxable_income = max(0, gross_salary - standard_deduction)
            
            # Get appropriate tax slabs based on age
            slabs = self._get_tax_slabs_by_age(self.NEW_REGIME_SLABS, age_group)
            
            # Calculate tax using new regime slabs
            tax = self._calculate_tax_by_slabs(taxable_income, slabs)
            
            # Add cess
            total_tax = tax + (tax * self.CESS_RATE)
            
            return total_tax
            
        except Exception as e:
            logger.error(f"Error calculating new regime tax: {str(e)}")
            return 0.0
    
    def _calculate_tax_by_slabs(self, taxable_income: float, slabs: list) -> float:
        """
        Calculate tax based on tax slabs
        
        Args:
            taxable_income: Taxable income amount
            slabs: List of tuples (min, max, rate)
            
        Returns:
            Tax amount
        """
        tax = 0.0
        remaining_income = taxable_income
        
        for min_income, max_income, rate in slabs:
            if remaining_income <= 0:
                break
            
            slab_income = min(remaining_income, max_income - min_income)
            if slab_income > 0:
                tax += slab_income * rate
                remaining_income -= slab_income
        
        return tax
    
    def _get_tax_slabs_by_age(self, base_slabs: list, age_group: str) -> list:
        """
        Get tax slabs based on age group
        
        Args:
            base_slabs: Base tax slabs
            age_group: "below_60", "60_80", or "above_80"
            
        Returns:
            Appropriate tax slabs for the age group
        """
        if age_group == "below_60":
            return base_slabs
        elif age_group == "60_80":
            # Senior citizen - use old regime senior citizen slabs if applicable
            if base_slabs == self.OLD_REGIME_SLABS:
                return self.SENIOR_CITIZEN_OLD_SLABS
            return base_slabs  # New regime doesn't have age-based slabs
        elif age_group == "above_80":
            # Super senior citizen
            if base_slabs == self.OLD_REGIME_SLABS:
                return self.SUPER_SENIOR_CITIZEN_OLD_SLABS
            return base_slabs
        return base_slabs
    
    def get_tax_breakdown(self, income_data: Dict, regime: str = "old") -> Dict:
        """
        Get detailed tax breakdown
        
        Args:
            income_data: Dictionary containing income and deduction details
            regime: "old" or "new"
            
        Returns:
            Dictionary with tax breakdown
        """
        if regime.lower() == "old":
            tax = self.calculate_old_regime(income_data)
        else:
            tax = self.calculate_new_regime(income_data)
        
        gross_salary = income_data.get("gross_salary", 0)
        deductions = income_data.get("deductions", {})
        
        if regime.lower() == "old":
            # Helper function to safely convert to float
            def safe_float(value, default=0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default
            
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
                try:
                    hra_exemption = float(deductions.get("hra", 0) or 0)
                except (ValueError, TypeError):
                    hra_exemption = 0
            
            total_deductions = (
                safe_float(deductions.get("section_80c", 0)) +
                safe_float(deductions.get("section_80ccd_1", 0)) +
                safe_float(deductions.get("section_80d", 0)) +
                safe_float(deductions.get("section_80ccd_1b", 0)) +
                safe_float(deductions.get("section_80e", 0)) +
                safe_float(deductions.get("section_80g", 0)) +
                safe_float(deductions.get("section_80tta", 0)) +
                safe_float(deductions.get("section_80ttb", 0)) +
                hra_exemption +
                safe_float(deductions.get("section_24b", 0)) +
                safe_float(deductions.get("section_80ee", 0)) +
                safe_float(deductions.get("section_80gg", 0)) +
                safe_float(deductions.get("other_deductions", 0)) +
                safe_float(deductions.get("standard_deduction", self.STANDARD_DEDUCTION))
            )
        else:
            total_deductions = deductions.get("standard_deduction", self.STANDARD_DEDUCTION)
        
        taxable_income = max(0, gross_salary - total_deductions)
        
        return {
            "gross_salary": gross_salary,
            "total_deductions": total_deductions,
            "taxable_income": taxable_income,
            "tax": tax,
            "effective_tax_rate": (tax / gross_salary * 100) if gross_salary > 0 else 0
        }

