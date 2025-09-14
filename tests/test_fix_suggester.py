import pytest
import pandas as pd
from fix_suggester import FixSuggester

class TestFixSuggester:
    
    def setup_method(self):
        """Setup test fixtures."""
        self.suggester = FixSuggester()
    
    def test_email_domain_fixes(self):
        """Test email domain correction suggestions."""
        test_cases = [
            ('user@gamil.com', 'user@gmail.com'),
            ('test@yahooo.com', 'test@yahoo.com'),
            ('contact@hotmial.com', 'contact@hotmail.com'),
            ('valid@gmail.com', 'valid@gmail.com')  # Should not change
        ]
        
        for input_email, expected in test_cases:
            result = self.suggester._fix_email(input_email)
            assert result == expected
    
    def test_phone_format_fixes(self):
        """Test phone number format corrections."""
        test_cases = [
            ('9876543210', '+91 98765 43210'),
            ('09876543210', '+91 98765 43210'),
            ('919876543210', '+91 98765 43210'),
            ('1234567890', '+91 12345 67890')
        ]
        
        for input_phone, expected in test_cases:
            result = self.suggester._fix_phone(input_phone)
            assert result == expected
    
    def test_website_fixes(self):
        """Test website URL corrections."""
        test_cases = [
            ('example.com', 'https://example.com'),
            ('www.test.org', 'https://www.test.org'),
            ('COMPANY.NET', 'https://company.net'),
            ('https://valid.com', 'https://valid.com')  # Should not change
        ]
        
        for input_url, expected in test_cases:
            result = self.suggester._fix_website(input_url)
            assert result == expected
    
    def test_postal_code_fixes(self):
        """Test postal code format corrections."""
        test_cases = [
            ('400-001', '400001'),
            ('560 001', '560001'),
            ('110,001', '110001'),
            ('400001', '400001')  # Should not change
        ]
        
        for input_postal, expected in test_cases:
            result = self.suggester._fix_postal(input_postal)
            assert result == expected
    
    def test_date_fixes(self):
        """Test date format corrections."""
        test_cases = [
            ('01/15/2023', '2023-01-15'),
            ('Jan 15, 2023', '2023-01-15'),
            ('15-01-2023', '2023-01-15'),
            ('2023-01-15', '2023-01-15')  # Should not change
        ]
        
        for input_date, expected in test_cases:
            result = self.suggester._fix_date(input_date)
            assert result == expected
    
    def test_suggest_fixes_integration(self):
        """Test end-to-end fix suggestion."""
        # Create test dataframe with issues
        test_data = {
            'email': ['user@gamil.com', 'valid@test.com', 'broken@'],
            'phone': ['9876543210', '+91 98765 43210', '123'],
            'website': ['example.com', 'https://valid.com', 'broken']
        }
        
        df = pd.DataFrame(test_data)
        
        # Mock validation results
        validation_results = {
            'email': {'valid_count': 1, 'invalid_count': 2, 'null_count': 0, 'total_count': 3},
            'phone': {'valid_count': 1, 'invalid_count': 2, 'null_count': 0, 'total_count': 3},
            'website': {'valid_count': 1, 'invalid_count': 2, 'null_count': 0, 'total_count': 3}
        }
        
        fixes = self.suggester.suggest_fixes(df, validation_results)
        
        # Should suggest fixes for invalid values
        assert len(fixes) > 0
        
        # Check that fixes have required fields
        for fix in fixes:
            assert 'field' in fix
            assert 'original_value' in fix
            assert 'suggested_value' in fix
            assert 'issue_type' in fix
            assert 'confidence' in fix
            assert 'row_index' in fix
    
    def test_no_fixes_for_valid_data(self):
        """Test that no fixes are suggested for valid data."""
        # Create dataframe with all valid data
        test_data = {
            'email': ['valid@test.com', 'another@example.org'],
            'phone': ['+91 98765 43210', '+91 87654 32109']
        }
        
        df = pd.DataFrame(test_data)
        
        # Mock validation results showing all valid
        validation_results = {
            'email': {'valid_count': 2, 'invalid_count': 0, 'null_count': 0, 'total_count': 2},
            'phone': {'valid_count': 2, 'invalid_count': 0, 'null_count': 0, 'total_count': 2}
        }
        
        fixes = self.suggester.suggest_fixes(df, validation_results)
        
        # Should suggest no fixes
        assert len(fixes) == 0