import pandas as pd
import numpy as np
import re
from typing import Dict, Any
from datetime import datetime
import logging
from dateutil import parser

logger = logging.getLogger(__name__)

class DataCleaner:
    """Handles deterministic data cleaning and validation."""

    def __init__(self):
        self.cleaning_rules = {
            'phone': self._clean_phone,
            'email': self._clean_email,
            'tax_id': self._clean_tax_id,
            'postal_code': self._clean_postal_code,
            'revenue': self._clean_currency,
            'employees': self._clean_number,
            'date_established': self._clean_date,
            'website': self._clean_website,
            'company_name': self._clean_text,
            'address': self._clean_text,
            'city': self._clean_text,
            'state': self._clean_text,
            'country': self._clean_text,
            'industry': self._clean_text,
            'contact_person': self._clean_text,
            'currency': self._clean_currency_code
        }

        self.validation_rules = {
            'phone': self._validate_phone,
            'email': self._validate_email,
            'tax_id': self._validate_tax_id,
            'postal_code': self._validate_postal_code,
            'revenue': self._validate_number,
            'employees': self._validate_integer,
            'date_established': self._validate_date,
            'website': self._validate_website,
            'company_name': self._validate_text,
            'address': self._validate_text,
            'city': self._validate_text,
            'state': self._validate_text,
            'country': self._validate_text,
            'industry': self._validate_text,
            'contact_person': self._validate_text,
            'currency': self._validate_text
        }

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean entire dataframe deterministically."""
        cleaned_df = df.copy()
        cleaned_df = cleaned_df.loc[:, ~cleaned_df.columns.duplicated()]

        for column in cleaned_df.columns:
            column_lower = column.lower()

            cleaning_func = None
            for rule_key, rule_func in self.cleaning_rules.items():
                if rule_key in column_lower:
                    cleaning_func = rule_func
                    break

            if cleaning_func:
                logger.info(f"Cleaning column: {column}")
                cleaned_df[column] = cleaned_df[column].apply(
                    lambda x: cleaning_func(x) if pd.notna(x) else x
                )

            # ✅ Fill missing values based on type
            if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                cleaned_df[column] = cleaned_df[column].fillna(0)
            else:
                cleaned_df[column] = cleaned_df[column].fillna("Unknown")

        return cleaned_df

    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Validate entire dataframe and return results safely."""
        validation_results = {}
        df = df.loc[:, ~df.columns.duplicated()]

        for column in df.columns:
            column_lower = column.lower()
            validation_func = None

            for rule_key, rule_func in self.validation_rules.items():
                if rule_key in column_lower:
                    validation_func = rule_func
                    break

            if validation_func:
                logger.info(f"Validating column: {column}")

                valid_mask = df[column].apply(
                    lambda x: bool(validation_func(x)) if pd.notna(x) else False
                ).astype(bool)

                total_count = len(df)
                valid_count = int(valid_mask.sum())
                null_count = int(df[column].isna().sum())
                invalid_mask = (~valid_mask) & df[column].notna()
                invalid_count = int(invalid_mask.sum())

                validation_results[column] = {
                    'valid_count': valid_count,
                    'invalid_count': invalid_count,
                    'null_count': null_count,
                    'total_count': total_count,
                    'valid_percentage': (valid_count / total_count) * 100 if total_count > 0 else 0
                }

        return validation_results

    def calculate_quality_stats(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Calculate data quality statistics for each column safely."""
        stats = {}
        df = df.loc[:, ~df.columns.duplicated()]

        for column in df.columns:
            col_data = df[column]

            if isinstance(col_data, pd.DataFrame):
                logger.warning(f"Column '{column}' returned DataFrame, using first subcolumn.")
                col_data = col_data.iloc[:, 0]

            total_count = len(df)
            non_null_count = int(col_data.notna().sum())

            try:
                dtype_str = str(col_data.dtype)
            except AttributeError:
                dtype_str = "unknown"

            stats[column] = {
                'completeness': (non_null_count / total_count) * 100 if total_count > 0 else 0,
                'null_count': int(col_data.isna().sum()),
                'non_null_count': non_null_count,
                'unique_values': int(col_data.nunique(dropna=True)),
                'data_type': dtype_str
            }

        return stats

    # -----------------------
    # Cleaning functions
    # -----------------------

    def _clean_phone(self, value: Any) -> str:
        if pd.isna(value):
            return value
        phone_str = str(value)
        digits_only = re.sub(r'\D', '', phone_str)

        if len(digits_only) == 10:
            digits_only = '91' + digits_only
        elif len(digits_only) == 11 and digits_only.startswith('0'):
            digits_only = '91' + digits_only[1:]

        if len(digits_only) == 12:
            return f"+{digits_only[:2]} {digits_only[2:7]} {digits_only[7:]}"
        elif len(digits_only) >= 10:
            return f"+91 {digits_only[-10:-5]} {digits_only[-5:]}"
        return digits_only

    def _clean_email(self, value: Any) -> str:
        if pd.isna(value):
            return value
        email_str = str(value).strip().lower()
        email_str = re.sub(r'\s+', '', email_str)

        common_fixes = {
            'gamil.com': 'gmail.com',
            'gmial.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'yaho.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com',
            'hotmil.com': 'hotmail.com'
        }

        if '@' in email_str:
            local, domain = email_str.split('@', 1)
            domain = common_fixes.get(domain, domain)
            email_str = f"{local}@{domain}"

        return email_str

    def _clean_tax_id(self, value: Any) -> str:
        if pd.isna(value):
            return value
        return re.sub(r'[^\w]', '', str(value).strip().upper())

    def _clean_postal_code(self, value: Any) -> str:
        if pd.isna(value):
            return value
        return re.sub(r'[^\w]', '', str(value).strip()).upper()

    def _clean_currency(self, value: Any) -> float:
        if pd.isna(value):
            return value
        cleaned = re.sub(r'[^\d.-]', '', str(value).strip())
        try:
            return float(cleaned)
        except ValueError:
            return np.nan

    def _clean_currency_code(self, value: Any) -> str:
        if pd.isna(value):
            return value
        val = str(value).strip().upper()
        mapping = {
            '₹': 'INR', 'RS': 'INR', 'INR': 'INR',
            'USD': 'USD', '$': 'USD',
            'EUR': 'EUR', '€': 'EUR'
        }
        return mapping.get(val, val)

    def _clean_number(self, value: Any) -> float:
        if pd.isna(value):
            return value
        cleaned = re.sub(r'[^\d.-]', '', str(value).strip())
        try:
            return float(cleaned)
        except ValueError:
            return np.nan

    def _clean_date(self, value: Any) -> str:
        if pd.isna(value):
            return value
        try:
            parsed_date = parser.parse(str(value).strip())
            return parsed_date.strftime('%Y-%m-%d')
        except (parser.ParserError, ValueError):
            return str(value)

    def _clean_website(self, value: Any) -> str:
        if pd.isna(value):
            return value
        url_str = str(value).strip().lower()
        if not url_str.startswith(('http://', 'https://')):
            url_str = 'https://' + url_str
        return url_str

    def _clean_text(self, value: Any) -> str:
        if pd.isna(value):
            return value
        return re.sub(r'\s+', ' ', str(value).strip()).title()

    # -----------------------
    # Validation functions
    # -----------------------

    def _validate_phone(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        return bool(re.match(r'^\+\d{1,3} \d{5} \d{5}$', str(value)))

    def _validate_email(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(value)))

    def _validate_tax_id(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        return bool(re.match(r'^[A-Z0-9]{8,15}$', str(value)))

    def _validate_postal_code(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        return bool(re.match(r'^[A-Z0-9]{4,10}$', str(value)))

    def _validate_number(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _validate_integer(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        try:
            val = float(value)
            return val.is_integer() and val >= 0
        except (ValueError, TypeError):
            return False

    def _validate_date(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        try:
            datetime.strptime(str(value), '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _validate_website(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        return bool(re.match(r'^https?://[^\s/$.?#].[^\s]*$', str(value)))

    def _validate_text(self, value: Any) -> bool:
        if pd.isna(value):
            return False
        return len(str(value).strip()) > 0