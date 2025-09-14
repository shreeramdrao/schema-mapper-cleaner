import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def create_sample_data_if_missing():
    """Create sample data files if they don't exist."""
    
    # Create directories
    Path("schema").mkdir(exist_ok=True)
    Path("sample_data").mkdir(exist_ok=True)
    
    # Create canonical schema
    schema_path = Path("schema/Project6StdFormat.csv")
    if not schema_path.exists():
        canonical_data = {
            'company_name': ['Acme Corp', 'Global Industries', 'Tech Solutions Ltd'],
            'tax_id': ['GST123456789', 'VAT987654321', 'REG456789123'],
            'email': ['contact@acme.com', 'info@global.com', 'support@tech.com'],
            'phone': ['+91 98765 43210', '+91 87654 32109', '+91 76543 21098'],
            'address': ['123 Business St', '456 Corporate Ave', '789 Tech Park'],
            'city': ['Mumbai', 'Bangalore', 'Delhi'],
            'state': ['Maharashtra', 'Karnataka', 'Delhi'],
            'postal_code': ['400001', '560001', '110001'],
            'country': ['India', 'India', 'India'],
            'website': ['https://acme.com', 'https://global.com', 'https://tech.com'],
            'industry': ['Manufacturing', 'Consulting', 'Technology'],
            'employees': [500, 250, 100],
            'revenue': [10000000.0, 5000000.0, 2500000.0],
            'date_established': ['2010-01-15', '2005-06-20', '2015-03-10'],
            'contact_person': ['John Doe', 'Jane Smith', 'Bob Wilson']
        }
        
        schema_df = pd.DataFrame(canonical_data)
        schema_df.to_csv(schema_path, index=False)
        logger.info(f"Created canonical schema at {schema_path}")
    
    # Create sample data files
    sample_files = [
        "Project6InputData1.csv",
        "Project6InputData2.csv",
        "Project6InputData3.csv"
    ]
    
    for i, filename in enumerate(sample_files):
        file_path = Path("sample_data") / filename
        if not file_path.exists():
            if i == 0:
                # Clean-ish data
                sample_data = {
                    'Company Name': ['Clean Corp', 'Perfect Ltd', 'Quality Inc'],
                    'Tax ID': ['GST111222333', 'VAT444555666', 'REG777888999'],
                    'Email': ['info@clean.com', 'contact@perfect.com', 'hello@quality.com'],
                    'Phone': ['+91 99999 88888', '+91 88888 77777', '+91 77777 66666'],
                    'Address': ['Clean Street 1', 'Perfect Road 2', 'Quality Lane 3'],
                    'City': ['Chennai', 'Hyderabad', 'Pune'],
                    'State': ['Tamil Nadu', 'Telangana', 'Maharashtra'],
                    'Postal Code': ['600001', '500001', '411001'],
                    'Country': ['India', 'India', 'India'],
                    'Website': ['https://clean.com', 'https://perfect.com', 'https://quality.com'],
                    'Industry': ['Software', 'Hardware', 'Services'],
                    'Employees': [150, 300, 75],
                    'Revenue': [3000000.0, 6000000.0, 1500000.0],
                    'Date Established': ['2012-05-10', '2008-11-22', '2018-02-14'],
                    'Contact Person': ['Alice Johnson', 'Mike Brown', 'Sarah Davis']
                }
            elif i == 1:
                # Messy headers and formats
                sample_data = {
                    'Comp Name': ['Messy Business', 'Chaotic Ltd', 'Disorder Inc'],
                    'VAT#': ['gst222333444', 'VAT555666777', 'reg888999000'],
                    'E-mail': ['INFO@MESSY.COM', 'Contact@Chaotic.net', 'support@disorder.co'],
                    'Tel No.': ['9876543210', '08765432109', '+91-7654321098'],
                    'Addr': ['Messy St, Block A', 'Chaotic Avenue 123', 'Disorder Complex, Unit 5'],
                    'Town': ['mumbai', 'BANGALORE', 'new delhi'],
                    'State/Region': ['mh', 'KA', 'DL'],
                    'ZIP': ['400-001', '560 001', '110,001'],
                    'Nation': ['IND', 'India', 'IN'],
                    'Web': ['messy.com', 'www.chaotic.net', 'http://disorder.co'],
                    'Sector': ['retail', 'MANUFACTURING', 'Service'],
                    'Staff': ['200 employees', '50', '1000+'],
                    'Annual Rev': ['$2,500,000', '₹15,00,000', '45 lakh'],
                    'Founded': ['Jan 2015', '2020-12-01', '03/15/2010'],
                    'Rep': ['JOHN SMITH', 'mary jones', 'Bob_Wilson']
                }
            else:
                # Missing/extra fields, nulls, messy values
                sample_data = {
                    'Organization': ['Broken Corp', '', 'Incomplete Ltd'],
                    'Registration_No': ['', 'INVALID123', None],
                    'Contact_Email': ['broken@gamil.com', 'incomplete@', 'valid@test.com'],
                    'Mobile': ['91-9999888877', '12345', '+91 88888 77777'],
                    'Location': ['Broken City, State', None, ''],
                    'PinCode': ['12345abc', '000000', '560001'],
                    'HomePage': ['broken', 'https://incomplete.com', ''],
                    'Business_Type': ['', 'Tech', None],
                    'WorkForce': ['', '50.5', 'Many'],
                    'YearlyIncome': ['Unknown', '2500000.50', ''],
                    'StartDate': ['01-01-2020', '2025/13/45', '2015-06-15'],
                    'Manager': ['', 'Test Manager', None],
                    'Extra_Field1': ['Data1', 'Data2', 'Data3'],
                    'Extra_Field2': [100, 200, 300]
                }
            
            sample_df = pd.DataFrame(sample_data)
            sample_df.to_csv(file_path, index=False)
            logger.info(f"Created sample data at {file_path}")

def normalize_column_name(column_name: str) -> str:
    """Normalize column name for comparison."""
    import re
    normalized = column_name.lower()
    normalized = re.sub(r'[^\w\s]', '_', normalized)
    normalized = re.sub(r'\s+', '_', normalized)
    normalized = re.sub(r'_+', '_', normalized)
    return normalized.strip('_')

def calculate_similarity_score(str1: str, str2: str) -> float:
    """Calculate similarity score between two strings."""
    from rapidfuzz import fuzz
    return fuzz.ratio(str1.lower(), str2.lower()) / 100.0

def safe_convert_to_numeric(value: Any, default: float = 0.0) -> float:
    """Safely convert value to numeric."""
    if pd.isna(value):
        return default
    
    try:
        # Remove common non-numeric characters
        import re
        if isinstance(value, str):
            cleaned = re.sub(r'[^\d.-]', '', value)
            return float(cleaned) if cleaned else default
        return float(value)
    except (ValueError, TypeError):
        return default

def detect_data_type(series: pd.Series) -> str:
    """Detect the most likely data type of a pandas Series."""
    # Remove null values for analysis
    clean_series = series.dropna()
    
    if len(clean_series) == 0:
        return 'unknown'
    
    # Convert to string for pattern matching
    string_series = clean_series.astype(str)
    
    # Check for email pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    email_matches = string_series.str.match(email_pattern).sum()
    if email_matches > len(clean_series) * 0.8:
        return 'email'
    
    # Check for phone pattern
    phone_pattern = r'^[\+]?[\d\s\-\(\)]{10,}$'
    phone_matches = string_series.str.match(phone_pattern).sum()
    if phone_matches > len(clean_series) * 0.8:
        return 'phone'
    
    # Check for date pattern
    import dateutil.parser as parser
    date_count = 0
    for value in string_series.head(min(10, len(string_series))):
        try:
            parser.parse(value)
            date_count += 1
        except (parser.ParserError, ValueError):
            pass
    
    if date_count > len(string_series.head(10)) * 0.7:
        return 'date'
    
    # Check for numeric
    numeric_count = 0
    for value in clean_series:
        try:
            float(value)
            numeric_count += 1
        except (ValueError, TypeError):
            pass
    
    if numeric_count > len(clean_series) * 0.8:
        return 'numeric'
    
    return 'text'
