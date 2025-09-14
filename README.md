# Schema Mapper & Data Quality Fixer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)  
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://schema-mapper-cleaner.streamlit.app/)
[Original High Clarity Video Link](https://drive.google.com/file/d/1RQxjc-pwdztZF8ejnZkuq0UNsLivWkCL/view?usp=sharing )

A production-ready **Streamlit application** that automatically maps messy CSV headers to a canonical schema and fixes data quality issues with intelligent suggestions and learning capabilities.

---

## 🚀 Features

- **Intelligent Header Mapping**: Automatically suggests mappings between input CSV headers and canonical schema fields using similarity algorithms
- **Deterministic Data Cleaning**: Automated cleaning and validation for phone numbers, emails, dates, currencies, postal codes, and more
- **Before/After Analytics**: Visual comparison of data quality metrics with interactive charts
- **Targeted Fix Suggestions**: Smart suggestions for remaining data quality issues (typos, invalid formats, missing codes)
- **Learning System**: Promotes and remembers successful fixes for future automatic application
- **Interactive UI**: Clean, intuitive Streamlit interface with step-by-step workflow
- **Production Ready**: Modular architecture, JSON persistence, error handling, and tests

---

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

---

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

The app will be available at **http://localhost:8501**

---

## ☁️ Deployment

To deploy on **Streamlit Cloud**:

1. Push your code and datasets to GitHub.  
2. Go to [Streamlit Cloud](https://share.streamlit.io/) and connect your repo.  
3. Set the entrypoint as `app.py`.  
4. Ensure `requirements.txt` is included.  

That’s it — the app will be live on your Streamlit Cloud URL.

---

## 📊 Usage Workflow

### Step 1: Data Upload
- Upload your CSV file or select from sample datasets
- View basic file statistics and preview

### Step 2: Header Mapping
- Review auto-generated header mappings with confidence scores
- Override mappings manually if needed
- Confidence codes:
  - 🟢 High (90%+)
  - 🟡 Medium (70–89%)
  - 🔴 Low (<70%)

### Step 3: Data Cleaning & Validation
- One-click cleaning and validation
- View before/after metrics and improvement charts
- Preview cleaned data sample

### Step 4: Targeted Fixes
- See remaining data quality issues
- Apply suggestions (email domains, phone codes, invalid dates, etc.)
- Promote successful fixes for future reuse

### Step 5: Final Report & Download
- Review final statistics & completeness
- Download cleaned CSV
- Visualize field-level quality metrics

---

## 🧠 System Design

### Deterministic First
The system **prioritizes deterministic transforms** (regex cleaning, parsing, normalization).  
AI-like techniques (fuzzy string matching, typo correction) are used **only for targeted fixes** when deterministic rules cannot fully resolve issues.

### Header Mapping Algorithm
1. **Exact Match** (Confidence: 1.0)  
2. **Promoted Aliases** (Confidence: 1.0)  
3. **Common Aliases** (Confidence: 0.95)  
4. **Token Overlap** (Confidence: 0.8–0.95)  
5. **Fuzzy String Matching** (Confidence: 0.6–0.75)  

### Cleaning Functions
- **Phone Numbers**: Normalize format, add country codes  
- **Emails**: Lowercase, fix domain typos  
- **Tax IDs/VAT**: Remove punctuation, uppercase  
- **Dates**: Parse and standardize to ISO format  
- **Currency/Numbers**: Remove symbols, convert to float  
- **Postal Codes**: Strip non-alphanumeric characters  
- **Websites**: Add protocols if missing  
- **Text Fields**: Trim whitespace, title case  
- **Missing Values**:
  - Numbers → `0`  
  - Text → `"Unknown"`  

### Fix Suggestions
- Email domain corrections (`gamil.com → gmail.com`)  
- Missing phone country codes  
- Invalid date corrections  
- Malformed URL fixes  
- Postal code formatting  

### Learning & Memory
- Promoted fixes remembered in `promoted_fixes.json`  
- Aliases auto-applied in future uploads  

---

## 🧪 Testing

Run tests with:
```bash
pytest tests/ -v
```

Covers:
- Header mapping logic  
- Cleaning functions  
- Fix suggestions  
- Persistence  

---

## 📋 Sample Data

- **Project6InputData1.csv**: Clean dataset  
- **Project6InputData2.csv**: Messy headers & formats  
- **Project6InputData3.csv**: Missing fields & nulls  

---

## 📈 Performance

- Efficient for CSVs up to **10,000 rows**  
- Header mapping: **O(n × m)** (headers × schema fields)  
- Cleaning: **O(n)** (cells)  
- Memory usage: ~2× CSV file size  

---

## 🔮 Future Enhancements

- ML-based data type detection  
- Cloud storage integration (S3, GCS)  
- API endpoints for programmatic access  
- Bulk processing  
- Custom validation rules  
- Advanced analytics dashboard  

---

For support or questions, please open an **issue** in this repository.  
