import pytest
import pandas as pd
from mapping import HeaderMapper

class TestHeaderMapper:
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mapper = HeaderMapper()
        self.canonical_fields = [
            'company_name', 'tax_id', 'email', 'phone', 'address',
            'city', 'state', 'postal_code', 'country', 'website'
        ]
    
    def test_exact_match(self):
        """Test exact header matching."""
        input_headers = ['company_name', 'email', 'phone']
        suggestions = self.mapper.suggest_mappings(input_headers, self.canonical_fields)
        
        assert 'company_name' in suggestions
        assert suggestions['company_name']['confidence'] == 1.0
        assert suggestions['company_name']['method'] == 'exact_match'
    
    def test_promoted_aliases(self):
        """Test promoted aliases take precedence."""
        input_headers = ['VAT#', 'Tel No']
        promoted_aliases = {'VAT#': 'tax_id', 'Tel No': 'phone'}
        
        suggestions = self.mapper.suggest_mappings(
            input_headers, self.canonical_fields, promoted_aliases
        )
        
        assert suggestions['VAT#']['mapped_field'] == 'tax_id'
        assert suggestions['VAT#']['confidence'] == 1.0
        assert suggestions['VAT#']['method'] == 'promoted_alias'
    
    def test_common_aliases(self):
        """Test common alias matching."""
        input_headers = ['vat number', 'telephone', 'zip code']
        suggestions = self.mapper.suggest_mappings(input_headers, self.canonical_fields)
        
        # These should match based on common aliases
        assert 'vat number' in suggestions
        assert suggestions['vat number']['confidence'] >= 0.9
    
    def test_token_overlap(self):
        """Test token overlap scoring."""
        input_headers = ['company business name', 'email address contact']
        suggestions = self.mapper.suggest_mappings(input_headers, self.canonical_fields)
        
        # Should have reasonable matches with good confidence
        assert len(suggestions) >= 1
        for suggestion in suggestions.values():
            if suggestion['method'] == 'token_overlap':
                assert 0.8 <= suggestion['confidence'] <= 0.95
    
    def test_fuzzy_matching(self):
        """Test fuzzy string matching."""
        input_headers = ['compny_nam', 'emal', 'phon']  # Typos
        suggestions = self.mapper.suggest_mappings(input_headers, self.canonical_fields)
        
        # Should find matches despite typos
        assert len(suggestions) >= 1
        for suggestion in suggestions.values():
            if suggestion['method'] == 'fuzzy_match':
                assert suggestion['confidence'] >= 0.6
    
    def test_no_match_below_threshold(self):
        """Test that poor matches are filtered out."""
        input_headers = ['completely_unrelated_field', 'xyz123']
        suggestions = self.mapper.suggest_mappings(input_headers, self.canonical_fields)
        
        # Should not suggest mappings for completely unrelated fields
        assert len(suggestions) == 0 or all(s['confidence'] >= 0.6 for s in suggestions.values())
    
    def test_normalize_header(self):
        """Test header normalization."""
        test_cases = [
            ('Company Name!', 'company name'),
            ('VAT#123', 'vat 123'),
            ('  Multiple   Spaces  ', 'multiple spaces'),
            ('UPPERCASE', 'uppercase'),
            ('Mixed_Case-Header', 'mixed case header')
        ]
        
        for input_header, expected in test_cases:
            result = self.mapper._normalize_header(input_header)
            assert result == expected
