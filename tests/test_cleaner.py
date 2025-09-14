import pytest
import pandas as pd
import numpy as np
from cleaner import DataCleaner

class TestDataCleaner:
    
    def setup_method(self):
        """Setup test fixtures."""
        self.cleaner = DataCleaner()
    
    def test_clean_phone(self):
        """Test phone number cleaning."""
        test_cases = [
            ('9876543210', '+91 98765 43210'),
            ('091-9876-543210', '+91 98765 43210'),
            ('+91 98765 43210', '+91 98765 43210'),
            ('919876543210', '+91 98765 43210'),
            ('(91) 9876-543210', '+91 98765 43210')
        ]
        
        for input_phone, expected in test_cases:
            result = self.cleaner._clean_phone(input_phone)
            assert result == expected
    
    def test_clean_email(self):
        """Test email cleaning."""
        test_cases = [
            ('Test@Example.COM', 'test@example.com'),
            ('  user@domain.org  ', 'user@domain.org'),
            ('USER@COMPANY.NET', 'user@company.net')
        ]
        
        for input_email, expected in test_cases:
            result = self.cleaner._clean_email(input_email)
            assert result == expected
    
    def test_clean_tax_id(self):
        """Test tax ID cleaning."""
        test_cases = [
            ('GST-123-456-789', 'GST123456789'),
            ('vat#987654321', 'VAT987654321'),
            ('  reg 456 789  ', 'REG456789')
        ]
        
        for input_tax_id, expected in test_cases:
            result = self.cleaner._clean_tax_id(input_tax_id)
            assert result == expected
    
    def test_clean_currency(self):
        """Test currency cleaning."""
        test_cases = [
            ('$1,234,567.89', 1234567.89),
            ('₹50,00,000', 5000000.0),
            ('USD 25,000', 25000.0),
            ('1.5M', 1.5),  # Should extract the numeric part
            ('invalid', np.nan)
        ]
        
        for input_currency, expected in test_cases:
            result = self.cleaner._clean_currency(input_currency)
            if pd.isna(expected):
                assert pd.isna(result)
            else:
                assert abs(result - expected) < 0.01
    
    def test_clean_date(self):
        """Test date cleaning."""
        test_cases = [
            ('2023-01-15', '2023-01-15'),
            ('01/15/2023', '2023-01-15'),
            ('Jan 15, 2023', '2023-01-15'),
            ('15-01-2023', '2023-01-15')
        ]
        
        for input_date, expected in test_cases:
            result = self.cleaner._clean_date(input_date)
            assert result == expected
    
    def test_clean_website(self):
        """Test website URL cleaning."""
        test_cases = [
            ('example.com', 'https://example.com'),
            ('www.example.com', 'https://www.example.com'),
            ('https://example.com', 'https://example.com'),
            ('HTTP://EXAMPLE.COM', 'https://example.com')
        ]
        
        for input_url, expected in test_cases:
            result = self.cleaner._clean_website(input_url)
            assert result == expected
    
    def test_validate_phone(self):
        """Test phone validation."""
        valid_phones = ['+91 98765 43210', '+1 23456 78901']
        invalid_phones = ['9876543210', '123', '+91-9876543210', 'not a phone']
        
        for phone in valid_phones:
            assert self.cleaner._validate_phone(phone) == True
        
        for phone in invalid_phones:
            assert self.cleaner._validate_phone(phone) == False
    
    def test_validate_email(self):
        """Test email validation."""
        valid_emails = ['test@example.com', 'user.name@domain.co.uk', 'valid+email@test.org']
        invalid_emails = ['invalid.email', '@example.com', 'test@', 'not an email']
        
        for email in valid_emails:
            assert self.cleaner._validate_email(email) == True
        
        for email in invalid_emails:
            assert self.cleaner._validate_email(email) == False
    
    def test_dataframe_cleaning(self):
        """Test cleaning entire dataframe."""
        test_data = {
            'company_name': ['  Test Corp  ', 'ANOTHER COMPANY', 'third business'],
            'phone': ['9876543210', '+91-8765432109', '919876543210'],
            'email': ['TEST@EXAMPLE.COM', '  user@domain.org  ', 'CONTACT@BUSINESS.NET']
        }
        
        df = pd.DataFrame(test_data)
        cleaned_df = self.cleaner.clean_dataframe(df)
        
        # Check that cleaning was applied
        assert cleaned_df['company_name'][0] == 'Test Corp'
        assert cleaned_df['phone'][0] == '+91 98765 43210'
        assert cleaned_df['email'][0] == 'test@example.com'
    
    def test_validation_results(self):
        """Test validation results structure."""
        test_data = {
            'email': ['valid@test.com', 'invalid.email', 'another@valid.org'],
            'phone': ['+91 98765 43210', '123', '+91 87654 32109']
        }
        
        df = pd.DataFrame(test_data)
        validation_results = self.cleaner.validate_dataframe(df)
        
        assert 'email' in validation_results
        assert 'phone' in validation_results
        
        email_results = validation_results['email']
        assert 'valid_count' in email_results
        assert 'invalid_count' in email_results
        assert 'null_count' in email_results
        assert 'total_count' in email_results
        assert 'valid_percentage' in email_results
    
    def test_quality_stats(self):
        """Test data quality statistics."""
        test_data = {
            'field1': ['a', 'b', None, 'd'],
            'field2': [1, 2, 3, 4],
            'field3': [None, None, None, None]
        }
        
        df = pd.DataFrame(test_data)
        stats = self.cleaner.calculate_quality_stats(df)
        
        assert stats['field1']['completeness'] == 75.0  # 3/4 non-null
        assert stats['field2']['completeness'] == 100.0  # 4/4 non-null
        assert stats['field3']['completeness'] == 0.0   # 0/4 non-null