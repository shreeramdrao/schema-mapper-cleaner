# Schema Mapper & Data Quality Fixer

A production-ready Streamlit application that automatically maps messy CSV headers to a canonical schema and fixes data quality issues with intelligent suggestions and learning capabilities.

## 🚀 Features

- **Intelligent Header Mapping**: Automatically suggests mappings between input CSV headers and canonical schema fields using multiple similarity algorithms
- **Deterministic Data Cleaning**: Automated cleaning and validation for phone numbers, emails, dates, currencies, postal codes, and more
- **Before/After Analytics**: Visual comparison of data quality metrics with interactive charts
- **Targeted Fix Suggestions**: AI-powered suggestions for remaining data quality issues
- **Learning System**: Promotes and remembers successful fixes for future automatic application
- **Interactive UI**: Clean, intuitive Streamlit interface with step-by-step workflow
- **Production Ready**: Modular architecture, comprehensive error handling, and unit tests

## 📁 Project Structure

```
project6_schema_mapper/
├── app.py                  # Main Streamlit application
├── mapping.py              # Header mapping logic with fuzzy matching
├── cleaner.py              # Deterministic cleaning & validation functions
├── fix_suggester.py        # Targeted fixes for remaining issues
├── persistence.py          # JSON storage for promoted fixes
├── schema_loader.py        # Canonical schema management
├── utils.py                # Shared helper functions
├── schema/
│   └── Project6StdFormat.csv    # Canonical schema definition
├── sample_data/
│   ├── Project6InputData1.csv   # Clean sample data
│   ├── Project6InputData2.csv   # Messy headers and formats
│   └── Project6InputData3.csv   # Missing fields and nulls
├── tests/                  # Unit tests
│   ├── test_mapping.py
│   ├── test_cleaner.py
│   └── test_fix_suggester.py
├── requirements.txt        # Python dependencies
├── promoted_fixes.json     # Saved fixes (auto-created)
└── README.md
```

## 🛠️ Installation & Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd project6_schema_mapper
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 📊 Usage Workflow

### Step 1: Data Upload
- Upload your CSV file or select from sample datasets
- View basic file statistics and preview

### Step 2: Header Mapping
- Review auto-generated header mappings with confidence scores
- Override mappings manually using dropdown selectors
- Green (🟢): High confidence (90%+)
- Yellow (🟡): Medium confidence (70-89%)
- Red (🔴): Low confidence (<70%)

### Step 3: Data Cleaning & Validation
- Run automated data cleaning and validation
- View before/after quality metrics
- See visual charts showing improvement percentages
- Preview cleaned data sample

### Step 4: Targeted Fixes
- Review remaining data quality issues
- Apply suggested fixes for emails, phones, dates, etc.
- Promote successful fixes to be remembered for future uploads

### Step 5: Final Report & Download
- Review final data quality statistics
- Download cleaned CSV file
- View completeness metrics and quality charts

## 🧠 Intelligent Features

### Header Mapping Algorithm
The system uses multiple techniques to suggest header mappings:

1. **Exact Match** (Confidence: 1.0)
2. **Promoted Aliases** (Confidence: 1.0) - Previously learned mappings
3. **Common Aliases** (Confidence: 0.95) - Built-in domain knowledge
4. **Token Overlap** (Confidence: 0.8-0.95) - Jaccard similarity on words
5. **Fuzzy String Matching** (Confidence: 0.6-0.75) - Character-level similarity

### Data Cleaning Functions
- **Phone Numbers**: Normalize format, add country codes
- **Email Addresses**: Lowercase, format validation
- **Tax IDs/VAT**: Remove punctuation, uppercase
- **Dates**: Parse and convert to ISO format (YYYY-MM-DD)
- **Currency/Numbers**: Remove symbols, convert to float
- **Postal Codes**: Extract alphanumeric characters
- **URLs**: Add protocols, normalize format
- **Text Fields**: Trim whitespace, title case

### Fix Suggestions
The system identifies and suggests fixes for:
- Email domain typos (gamil.com → gmail.com)
- Missing phone country codes
- Invalid date formats
- Malformed URLs
- Postal code formatting issues

### Learning & Memory
- Successful fixes can be "promoted" to be automatically applied
- Header aliases are remembered for future uploads
- All learning data stored in `promoted_fixes.json`

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Test coverage includes:
- Header mapping algorithms
- Data cleaning functions
- Fix suggestion logic
- Persistence operations

## 📋 Sample Data

The application includes three sample datasets:

1. **Project6InputData1.csv**: Clean data with standard headers
2. **Project6InputData2.csv**: Messy headers and mixed formats
3. **Project6InputData3.csv**: Missing fields, nulls, and invalid data

## 🔧 Configuration

### Canonical Schema
Edit `schema/Project6StdFormat.csv` to modify the canonical schema. The system will automatically adapt to schema changes.

### Promoted Fixes
The `promoted_fixes.json` file stores learned mappings and fix rules:
```json
{
  "header_aliases": {
    "VAT#": "tax_id",
    "Tel No.": "phone"
  },
  "fix_rules": [
    {
      "field": "email",
      "rule_type": "domain_fix",
      "original": "user@gamil.com",
      "replacement": "user@gmail.com"
    }
  ]
}
```

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Environment Variables
```bash
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## 🛡️ Security Considerations

- Input validation on all uploaded files
- Secure file handling with pathlib
- No execution of user-provided code
- Sanitized data preview and display

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**File Upload Error**: Ensure CSV files use UTF-8 encoding
**Memory Issues**: Large files (>100MB) may require increased memory limits
**Mapping Issues**: Check canonical schema format and field names

### Logging
The application uses Python logging. Set log level in code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

- Handles CSV files up to 10,000 rows efficiently
- Header mapping: O(n*m) where n=input headers, m=canonical fields
- Data cleaning: O(n) where n=total cells
- Memory usage: ~2x CSV file size

## 🔮 Future Enhancements

- Machine learning-based data type detection
- Integration with cloud storage (S3, GCS)
- API endpoints for programmatic access
- Bulk processing capabilities
- Advanced analytics and reporting
- Custom validation rules

---
For support or questions, please open an issue on the repository.