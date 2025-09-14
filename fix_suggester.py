import pandas as pd
import re
from typing import Dict, List, Any, Optional
from rapidfuzz import fuzz, process
import logging

logger = logging.getLogger(__name__)

class FixSuggester:
    """Suggests targeted fixes for remaining data quality issues."""
    
    def __init__(self):
        # Common domain corrections
        self.common_domain_fixes = {
            'gamil.com': 'gmail.com',
            'gmial.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'yaho.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com',
            'hotmil.com': 'hotmail.com'
        }
        
        # Common country codes
        self.country_codes = {
            'india': '+91',
            'usa': '+1',
            'uk': '+44',
            'canada': '+1',
            'australia': '+61'
        }
    
    def suggest_fixes(self, df: pd.DataFrame, validation_results: Dict) -> List[Dict]:
        """
        Suggest fixes for invalid or suspicious values in the dataframe.
        
        Args:
            df: DataFrame with cleaned data
            validation_results: Validation results from DataCleaner
            
        Returns:
            List of suggested fixes
        """
        suggested_fixes = []
        
        for column in df.columns:
            validation_info = validation_results.get(column, {})
            
            # Always run checks if column looks like email/phone/etc.
            if (
                validation_info.get('invalid_count', 0) > 0
                or any(key in column.lower() for key in ['email', 'phone', 'date', 'website', 'postal'])
            ):
                column_fixes = self._suggest_column_fixes(df, column)
                suggested_fixes.extend(column_fixes)
        
        return suggested_fixes
    
    def _suggest_column_fixes(self, df: pd.DataFrame, column: str) -> List[Dict]:
        """Suggest fixes for a specific column."""
        fixes = []
        column_lower = column.lower()
        
        if 'email' in column_lower:
            fixes.extend(self._suggest_email_fixes(df, column))
        elif 'phone' in column_lower:
            fixes.extend(self._suggest_phone_fixes(df, column))
        elif 'date' in column_lower:
            fixes.extend(self._suggest_date_fixes(df, column))
        elif 'website' in column_lower:
            fixes.extend(self._suggest_website_fixes(df, column))
        elif 'postal' in column_lower or 'zip' in column_lower:
            fixes.extend(self._suggest_postal_fixes(df, column))
        
        return fixes
    
    def _suggest_email_fixes(self, df: pd.DataFrame, column: str) -> List[Dict]:
        """Suggest fixes for email addresses."""
        fixes = []
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for idx, value in df[column].items():
            if pd.notna(value) and not re.match(email_pattern, str(value)):
                email_str = str(value).strip().lower()
                suggested_fix = self._fix_email(email_str)
                
                if suggested_fix and suggested_fix != email_str:
                    fixes.append({
                        'field': column,
                        'row_index': idx,
                        'original_value': value,
                        'suggested_value': suggested_fix,
                        'issue_type': 'email_format',
                        'confidence': 0.8
                    })
        
        return fixes
    
    def _suggest_phone_fixes(self, df: pd.DataFrame, column: str) -> List[Dict]:
        """Suggest fixes for phone numbers."""
        fixes = []
        phone_pattern = r'^\+\d{1,3} \d{5} \d{5}$'
        
        for idx, value in df[column].items():
            if pd.notna(value) and not re.match(phone_pattern, str(value)):
                phone_str = str(value)
                suggested_fix = self._fix_phone(phone_str)
                
                if suggested_fix and suggested_fix != phone_str:
                    fixes.append({
                        'field': column,
                        'row_index': idx,
                        'original_value': value,
                        'suggested_value': suggested_fix,
                        'issue_type': 'phone_format',
                        'confidence': 0.9
                    })
        
        return fixes
    
    def _suggest_date_fixes(self, df: pd.DataFrame, column: str) -> List[Dict]:
        """Suggest fixes for dates."""
        fixes = []
        
        for idx, value in df[column].items():
            if pd.notna(value):
                date_str = str(value)
                try:
                    from datetime import datetime
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    suggested_fix = self._fix_date(date_str)
                    if suggested_fix and suggested_fix != date_str:
                        fixes.append({
                            'field': column,
                            'row_index': idx,
                            'original_value': value,
                            'suggested_value': suggested_fix,
                            'issue_type': 'date_format',
                            'confidence': 0.7
                        })
        
        return fixes
    
    def _suggest_website_fixes(self, df: pd.DataFrame, column: str) -> List[Dict]:
        """Suggest fixes for website URLs."""
        fixes = []
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        
        for idx, value in df[column].items():
            if pd.notna(value) and not re.match(url_pattern, str(value)):
                url_str = str(value).strip()
                suggested_fix = self._fix_website(url_str)
                
                if suggested_fix and suggested_fix != url_str:
                    fixes.append({
                        'field': column,
                        'row_index': idx,
                        'original_value': value,
                        'suggested_value': suggested_fix,
                        'issue_type': 'url_format',
                        'confidence': 0.8
                    })
        
        return fixes
    
    def _suggest_postal_fixes(self, df: pd.DataFrame, column: str) -> List[Dict]:
        """Suggest fixes for postal codes."""
        fixes = []
        postal_pattern = r'^[A-Z0-9]{4,10}$'
        
        for idx, value in df[column].items():
            if pd.notna(value) and not re.match(postal_pattern, str(value)):
                postal_str = str(value)
                suggested_fix = self._fix_postal(postal_str)
                
                if suggested_fix and suggested_fix != postal_str:
                    fixes.append({
                        'field': column,
                        'row_index': idx,
                        'original_value': value,
                        'suggested_value': suggested_fix,
                        'issue_type': 'postal_format',
                        'confidence': 0.9
                    })
        
        return fixes
    
    # -----------------------
    # Fix helper functions
    # -----------------------
    
    def _fix_email(self, email: str) -> Optional[str]:
        """Suggest fix for email address."""
        if '@' in email:
            local, domain = email.rsplit('@', 1)
            
            if domain in self.common_domain_fixes:
                return f"{local}@{self.common_domain_fixes[domain]}"
            
            common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            best_match = process.extractOne(domain, common_domains, scorer=fuzz.ratio)
            
            if best_match and best_match[1] > 70:
                return f"{local}@{best_match[0]}"
        
        return email
    
    def _fix_phone(self, phone: str) -> Optional[str]:
        """Suggest fix for phone number."""
        digits_only = re.sub(r'\D', '', phone)
        
        if len(digits_only) == 10:
            return f"+91 {digits_only[:5]} {digits_only[5:]}"
        elif len(digits_only) == 11 and digits_only.startswith('0'):
            return f"+91 {digits_only[1:6]} {digits_only[6:]}"
        elif len(digits_only) == 12:
            return f"+{digits_only[:2]} {digits_only[2:7]} {digits_only[7:]}"
        
        return phone
    
    def _fix_date(self, date_str: str) -> Optional[str]:
        """Suggest fix for date format."""
        from dateutil import parser
        try:
            parsed_date = parser.parse(date_str)
            return parsed_date.strftime('%Y-%m-%d')
        except (parser.ParserError, ValueError):
            return date_str
    
    def _fix_website(self, url: str) -> Optional[str]:
        """Suggest fix for website URL."""
        url = url.strip().lower()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _fix_postal(self, postal: str) -> Optional[str]:
        """Suggest fix for postal code."""
        cleaned = re.sub(r'[^\w]', '', postal).upper()
        return cleaned if len(cleaned) >= 4 else postal