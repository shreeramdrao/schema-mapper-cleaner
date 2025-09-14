import json
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PersistenceManager:
    """Handles saving and loading of promoted fixes and mappings."""
    
    def __init__(self, storage_path: str = "promoted_fixes.json"):
        self.storage_path = Path(storage_path)
    
    def load_promoted_fixes(self) -> Dict[str, Any]:
        """
        Load promoted fixes from JSON file.
        
        Returns:
            Dictionary containing promoted fixes and mappings
        """
        if not self.storage_path.exists():
            return {
                'header_aliases': {},
                'fix_rules': []
            }
        
        try:
            # ✅ Handle empty file case
            if self.storage_path.stat().st_size == 0:
                return {
                    'header_aliases': {},
                    'fix_rules': []
                }
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(
                f"Loaded {len(data.get('header_aliases', {}))} header aliases and "
                f"{len(data.get('fix_rules', []))} fix rules"
            )
            return data
            
        except Exception as e:
            # ✅ Handle corrupted JSON gracefully
            logger.error(f"Error loading promoted fixes: {str(e)} — resetting to empty.")
            return {
                'header_aliases': {},
                'fix_rules': []
            }
    
    def save_promoted_fixes(self, fixes_data: Dict[str, Any]) -> bool:
        """
        Save promoted fixes to JSON file.
        
        Args:
            fixes_data: Dictionary containing fixes and mappings to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(fixes_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved promoted fixes to {self.storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving promoted fixes: {str(e)}")
            return False
    
    def add_header_alias(self, original_header: str, canonical_field: str) -> bool:
        """
        Add a header alias to the promoted fixes.
        
        Args:
            original_header: Original header name from input CSV
            canonical_field: Canonical field name it maps to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current_fixes = self.load_promoted_fixes()
            current_fixes['header_aliases'][original_header] = canonical_field
            return self.save_promoted_fixes(current_fixes)
            
        except Exception as e:
            logger.error(f"Error adding header alias: {str(e)}")
            return False
    
    def add_fix_rule(self, field: str, rule_type: str, original_value: str, 
                     replacement_value: str, **params) -> bool:
        """
        Add a fix rule to the promoted fixes.
        
        Args:
            field: Field name the rule applies to
            rule_type: Type of fix rule
            original_value: Original value that needs fixing
            replacement_value: Replacement value
            **params: Additional parameters for the rule
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current_fixes = self.load_promoted_fixes()
            
            rule = {
                'field': field,
                'rule_type': rule_type,
                'original': original_value,
                'replacement': replacement_value,
                'params': params
            }
            
            current_fixes['fix_rules'].append(rule)
            return self.save_promoted_fixes(current_fixes)
            
        except Exception as e:
            logger.error(f"Error adding fix rule: {str(e)}")
            return False
    
    def get_header_aliases(self) -> Dict[str, str]:
        """Get all header aliases."""
        fixes = self.load_promoted_fixes()
        return fixes.get('header_aliases', {})
    
    def get_fix_rules(self, field: str = None) -> List[Dict[str, Any]]:
        """
        Get fix rules, optionally filtered by field.
        
        Args:
            field: Optional field name to filter by
            
        Returns:
            List of fix rules
        """
        fixes = self.load_promoted_fixes()
        rules = fixes.get('fix_rules', [])
        
        if field:
            rules = [rule for rule in rules if rule.get('field') == field]
        
        return rules