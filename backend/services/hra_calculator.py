from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HRACalculator:
    """
    Calculate House Rent Allowance (HRA) exemption
    HRA exemption is the minimum of:
    1. Actual HRA received
    2. Actual rent paid minus 10% of basic salary
    3. 50% of basic salary (metro) or 40% (non-metro)
    """
    
    @staticmethod
    def calculate_hra_exemption(
        basic_salary: float,
        hra_received: float,
        rent_paid: float,
        is_metro: bool = False
    ) -> float:
        """
        Calculate HRA exemption amount
        
        Args:
            basic_salary: Annual basic salary
            hra_received: Annual HRA received
            rent_paid: Annual rent paid
            is_metro: True if living in metro city (Delhi, Mumbai, Chennai, Kolkata)
            
        Returns:
            HRA exemption amount
        """
        try:
            # Component 1: Actual HRA received
            component1 = hra_received
            
            # Component 2: Rent paid minus 10% of basic salary
            component2 = max(0, rent_paid - (basic_salary * 0.10))
            
            # Component 3: 50% of basic (metro) or 40% (non-metro)
            if is_metro:
                component3 = basic_salary * 0.50
            else:
                component3 = basic_salary * 0.40
            
            # HRA exemption is minimum of all three components
            hra_exemption = min(component1, component2, component3)
            
            return max(0, hra_exemption)
            
        except Exception as e:
            logger.error(f"Error calculating HRA exemption: {str(e)}")
            return 0.0

