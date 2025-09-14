import pandas as pd
from typing import Dict, List, Tuple, Optional
import re
from rapidfuzz import fuzz, process
import logging

logger = logging.getLogger(__name__)

class HeaderMapper:
    """Handles intelligent header mapping between input CSV and canonical schema."""
    
    def __init__(self):
        # Common aliases for mapping
        self.common_aliases = {
            # Order
            'order_id': ['order id', 'order no', 'reference'],
            'order_date': ['orderdate', 'ordered_on'],

            # Customer
            'customer_id': ['cust id', 'client_ref'],
            'customer_name': ['customer', 'client_name'],
            'email': ['contact', 'email address', 'e-mail', 'mail'],
            'phone': ['mobile', 'phone number', 'telephone', 'contact number'],
            
            # Addresses
            'billing_address': ['bill addr', 'bill_to'],
            'shipping_address': ['ship addr', 'ship_to'],
            'city': ['town', 'locality', 'city'],
            'state': ['state/province', 'region'],
            'postal_code': ['zip', 'zip code', 'postcode', 'postal', 'zip/postal', 'pin'],
            'country': ['country/region', 'nation'],
            
            # Product
            'product_sku': ['sku', 'stock_code'],
            'product_name': ['item', 'desc'],
            'category': ['cat.'],
            'subcategory': ['subcat'],
            'quantity': ['qty'],
            'unit_price': ['price', 'unit price'],
            'currency': ['currency'],
            
            # Discounts, tax, shipping
            'discount_pct': ['disc%', 'discount'],
            'tax_pct': ['tax%', 'gst'],
            'shipping_fee': ['ship fee', 'logistics_fee'],
            'total_amount': ['total', 'grand_total'],
            
            # IDs
            'tax_id': ['reg no', 'gstin'],
            
            # Extra fields (skip)
            'SKIP': ['coupon_code']
        }
    
    def suggest_mappings(self, input_headers: List[str], canonical_fields: List[str], 
                        promoted_aliases: Dict[str, str] = None) -> Dict[str, Dict]:
        """
        Suggest mappings between input headers and canonical fields.
        
        Args:
            input_headers: List of headers from input CSV
            canonical_fields: List of canonical schema fields
            promoted_aliases: Previously saved header aliases
            
        Returns:
            Dictionary mapping input headers to suggested canonical fields with confidence
        """
        if promoted_aliases is None:
            promoted_aliases = {}
        
        suggestions = {}
        
        for header in input_headers:
            suggestion = self._find_best_match(header, canonical_fields, promoted_aliases)
            if suggestion:
                suggestions[header] = suggestion
        
        return suggestions
    
    def _find_best_match(self, header: str, canonical_fields: List[str], 
                        promoted_aliases: Dict[str, str]) -> Optional[Dict]:
        """Find the best matching canonical field for an input header."""
        
        # Check promoted aliases first (highest confidence)
        if header in promoted_aliases:
            return {
                'mapped_field': promoted_aliases[header],
                'confidence': 1.0,
                'method': 'promoted_alias'
            }
        
        header_clean = self._normalize_header(header)
        best_match = None
        best_score = 0
        best_method = None
        
        for canonical_field in canonical_fields:
            canonical_clean = self._normalize_header(canonical_field)
            
            # Exact match
            if header_clean == canonical_clean:
                return {
                    'mapped_field': canonical_field,
                    'confidence': 1.0,
                    'method': 'exact_match'
                }
            
            # Check common aliases
            if canonical_field.lower() in self.common_aliases:
                aliases = self.common_aliases[canonical_field.lower()]
                for alias in aliases:
                    if fuzz.ratio(header_clean, self._normalize_header(alias)) > 85:
                        score = 0.95
                        if score > best_score:
                            best_match = canonical_field
                            best_score = score
                            best_method = 'alias_match'
            
            # Token overlap scoring
            header_tokens = set(header_clean.split())
            canonical_tokens = set(canonical_clean.split())
            
            if header_tokens and canonical_tokens:
                overlap = len(header_tokens & canonical_tokens)
                union = len(header_tokens | canonical_tokens)
                jaccard_score = overlap / union if union > 0 else 0
                
                if jaccard_score > 0.5:
                    score = 0.8 + (jaccard_score - 0.5) * 0.3  # 0.8 to 0.95
                    if score > best_score:
                        best_match = canonical_field
                        best_score = score
                        best_method = 'token_overlap'
            
            # Fuzzy string similarity
            fuzzy_score = fuzz.ratio(header_clean, canonical_clean) / 100
            if fuzzy_score > 0.7:
                score = 0.6 + (fuzzy_score - 0.7) * 0.5  # 0.6 to 0.75
                if score > best_score:
                    best_match = canonical_field
                    best_score = score
                    best_method = 'fuzzy_match'
        
        if best_match and best_score > 0.6:
            return {
                'mapped_field': best_match,
                'confidence': best_score,
                'method': best_method
            }
        
        return None
    
    def _normalize_header(self, header: str) -> str:
        """Normalize header for comparison."""
        # Convert to lowercase
        normalized = header.lower()
        # Remove special characters
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        # Replace multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', normalized)
        # Strip whitespace
        normalized = normalized.strip()
        return normalized
