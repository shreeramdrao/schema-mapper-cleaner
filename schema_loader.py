import pandas as pd
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class SchemaLoader:
    """Handles loading and managing the canonical schema."""
    
    def __init__(self, schema_path: str = "schema/Project6StdFormat.csv"):
        self.schema_path = Path(schema_path)
    
    def load_canonical_schema(self) -> Optional[List[str]]:
        """
        Load the canonical schema from CSV file.
        
        Returns:
            List of canonical field names, or None if loading fails
        """
        try:
            if not self.schema_path.exists():
                logger.error(f"Schema file not found: {self.schema_path}")
                return None
            
            schema_df = pd.read_csv(self.schema_path)
            
            # Get column names (the canonical schema fields)
            if "canonical_name" in schema_df.columns:
                 canonical_fields = schema_df["canonical_name"].dropna().astype(str).str.strip().tolist()
            elif "name" in schema_df.columns:
                canonical_fields = schema_df["name"].dropna().astype(str).str.strip().tolist()
            else:
                logger.error("Schema file does not contain 'canonical_name' or 'name' column")
                return None
            
            logger.info(f"Loaded {len(canonical_fields)} canonical fields")
            return canonical_fields
            
        except Exception as e:
            logger.error(f"Error loading canonical schema: {str(e)}")
            return None
    
    def get_field_info(self, field_name: str) -> dict:
        """
        Get information about a specific canonical field.
        
        Args:
            field_name: Name of the canonical field
            
        Returns:
            Dictionary with field information
        """
        try:
            schema_df = pd.read_csv(self.schema_path)
            
            if field_name not in schema_df.columns:
                return {"exists": False}
            
            # Get sample values and basic info
            field_data = schema_df[field_name].dropna()
            
            return {
                "exists": True,
                "sample_values": field_data.head(5).tolist(),
                "data_type": str(field_data.dtype),
                "non_null_count": len(field_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting field info for {field_name}: {str(e)}")
            return {"exists": False, "error": str(e)}
