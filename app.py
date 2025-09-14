import streamlit as st
import pandas as pd
import json
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px

from schema_loader import SchemaLoader
from mapping import HeaderMapper
from cleaner import DataCleaner
from fix_suggester import FixSuggester
from persistence import PersistenceManager
from utils import create_sample_data_if_missing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Schema Mapper & Data Quality Fixer",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_components():
    """Initialize all components."""
    if 'schema_loader' not in st.session_state:
        st.session_state.schema_loader = SchemaLoader()
    if 'mapper' not in st.session_state:
        st.session_state.mapper = HeaderMapper()
    if 'cleaner' not in st.session_state:
        st.session_state.cleaner = DataCleaner()
    if 'fix_suggester' not in st.session_state:
        st.session_state.fix_suggester = FixSuggester()
    if 'persistence' not in st.session_state:
        st.session_state.persistence = PersistenceManager()

def main():
    """Main Streamlit application."""
    st.title("🔧 Schema Mapper & Data Quality Fixer")
    st.markdown("---")
    
    create_sample_data_if_missing()
    initialize_components()
    
    canonical_schema = st.session_state.schema_loader.load_canonical_schema()
    if canonical_schema is None:
        st.error("❌ Could not load canonical schema. Please check schema/Project6StdFormat.csv")
        return
    
    promoted_fixes = st.session_state.persistence.load_promoted_fixes()
    
    with st.sidebar:
        st.header("📤 Data Upload")
        upload_option = st.radio("Choose data source:", ["Upload CSV", "Use Sample Data"])
        
        df_uploaded = None
        filename = ""
        
        if upload_option == "Upload CSV":
            uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
            if uploaded_file:
                try:
                    df_uploaded = pd.read_csv(uploaded_file)
                    filename = uploaded_file.name
                    st.success(f"✅ Loaded {filename}")
                    st.info(f"Shape: {df_uploaded.shape}")
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
                    return
        else:
            sample_files = ["Project6InputData1.csv", "Project6InputData2.csv", "Project6InputData3.csv"]
            selected_sample = st.selectbox("Select sample dataset:", sample_files)
            try:
                sample_path = Path("sample_data") / selected_sample
                df_uploaded = pd.read_csv(sample_path)
                filename = selected_sample
                st.success(f"✅ Loaded {filename}")
                st.info(f"Shape: {df_uploaded.shape}")
            except Exception as e:
                st.error(f"❌ Error loading sample: {str(e)}")
                return
    
    if df_uploaded is None:
        st.info("👆 Please upload a CSV file or select sample data from the sidebar to begin.")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Header Mapping","🧹 Data Cleaning","🔧 Targeted Fixes","📊 Final Report"])
    
    with tab1:
        st.header("📋 Header Mapping")
        handle_header_mapping(df_uploaded, canonical_schema, promoted_fixes)
    
    with tab2:
        st.header("🧹 Data Cleaning & Validation")
        if 'final_mapping' in st.session_state:
            handle_data_cleaning(df_uploaded, st.session_state.final_mapping)
        else:
            st.info("Please complete header mapping first.")
    
    with tab3:
        st.header("🔧 Targeted Fixes")
        if 'cleaned_df' in st.session_state and 'validation_results' in st.session_state:
            handle_targeted_fixes()
        else:
            st.info("Please complete data cleaning first.")
    
    with tab4:
        st.header("📊 Final Report & Download")
        if 'final_df' in st.session_state:
            handle_final_report(filename)
        else:
            st.info("Complete all previous steps to see the final report.")

def handle_header_mapping(df_uploaded: pd.DataFrame, canonical_schema: List[str], promoted_fixes: Dict):
    st.markdown("Map your CSV headers to the canonical schema fields.")
    with st.spinner("🔍 Analyzing headers..."):
        mapping_suggestions = st.session_state.mapper.suggest_mappings(
            list(df_uploaded.columns), canonical_schema, promoted_fixes.get('header_aliases', {})
        )
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Mapping Suggestions")
        mapping_data = []
        for orig_header in df_uploaded.columns:
            suggestion = mapping_suggestions.get(orig_header)
            if suggestion:
                mapped_field = suggestion['mapped_field']
                confidence = suggestion['confidence']
                confidence_color = "🟢" if confidence >= 0.9 else "🟡" if confidence >= 0.7 else "🔴"
            else:
                mapped_field, confidence, confidence_color = "SKIP", 0.0, "⚪"
            mapping_data.append({
                'Original Header': orig_header,
                'Suggested Mapping': mapped_field,
                'Confidence': f"{confidence_color} {confidence:.2f}",
                'Sample Values': ', '.join(df_uploaded[orig_header].dropna().astype(str).head(3).tolist())
            })
        st.dataframe(pd.DataFrame(mapping_data), use_container_width=True)
    
    with col2:
        st.subheader("Manual Overrides")
        final_mapping = {}
        canonical_options = ['SKIP'] + canonical_schema
        for orig_header in df_uploaded.columns:
            suggestion = mapping_suggestions.get(orig_header)
            default_idx = canonical_options.index(suggestion['mapped_field']) if suggestion and suggestion['mapped_field'] in canonical_options else 0
            selected = st.selectbox(f"{orig_header}", canonical_options, index=default_idx, key=f"mapping_{orig_header}")
            if selected != 'SKIP':
                final_mapping[orig_header] = selected
        if st.button("💾 Confirm Mapping", type="primary"):
            st.session_state.final_mapping = final_mapping
            st.success("✅ Mapping confirmed!")
            for orig, mapped in final_mapping.items():
                st.markdown(f"• `{orig}` → `{mapped}`")

def handle_data_cleaning(df_uploaded: pd.DataFrame, final_mapping: Dict[str, str]):
    if st.button("🧹 Run Data Cleaning & Validation", type="primary"):
        with st.spinner("🔄 Cleaning and validating data..."):
            try:
                # --- Step 1: Apply header mapping without dropping duplicates
                mapped_df = df_uploaded.rename(columns=final_mapping)

                # --- Step 2: Merge duplicate mapped columns row-wise (first non-null wins)
                merged_df = pd.DataFrame()
                for target_field in set(final_mapping.values()):
                    dupes = [col for col, mapped in final_mapping.items() if mapped == target_field]
                    if len(dupes) > 1:
                        merged_df[target_field] = df_uploaded[dupes].apply(
                            lambda row: next((x for x in row if pd.notna(x)), None), axis=1
                        )
                    else:
                        merged_df[target_field] = mapped_df[target_field]

                # --- Step 3: Run cleaning
                cleaned_df = st.session_state.cleaner.clean_dataframe(merged_df)

                # --- Step 4: Apply promoted fixes automatically
                promoted_fixes = st.session_state.persistence.load_promoted_fixes()
                if 'fix_rules' in promoted_fixes:
                    for rule in promoted_fixes['fix_rules']:
                        field = rule.get('field')
                        original = rule.get('original')
                        replacement = rule.get('replacement')
                        if field in cleaned_df.columns:
                            mask = cleaned_df[field] == original
                            cleaned_df.loc[mask, field] = replacement

                # --- Step 5: Validate
                validation_results = st.session_state.cleaner.validate_dataframe(cleaned_df)

                st.session_state.original_mapped_df = merged_df
                st.session_state.cleaned_df = cleaned_df
                st.session_state.validation_results = validation_results

                st.success("✅ Data cleaning completed with duplicate merges and promoted fixes applied!")

            except Exception as e:
                st.error(f"❌ Error during data cleaning: {str(e)}")
                logger.error(f"Error in handle_data_cleaning: {str(e)}")
                return
    if 'cleaned_df' in st.session_state and 'validation_results' in st.session_state:
        display_cleaning_results()

def display_cleaning_results():
    original_df = st.session_state.original_mapped_df
    cleaned_df = st.session_state.cleaned_df
    validation_results = st.session_state.validation_results
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Before Cleaning")
        st.json(st.session_state.cleaner.calculate_quality_stats(original_df))
    with col2:
        st.subheader("✨ After Cleaning")
        st.json(st.session_state.cleaner.calculate_quality_stats(cleaned_df))
    st.subheader("📈 Data Quality Improvement")
    fields = list(validation_results.keys())
    before_valid, after_valid = [], []
    for field in fields:
        total_rows = len(cleaned_df)
        valid_count = validation_results[field]['valid_count']
        after_valid.append((valid_count / total_rows) * 100 if total_rows > 0 else 0)
        non_null_count = original_df[field].notna().sum() if field in original_df.columns else 0
        before_valid.append((non_null_count / total_rows) * 100 if total_rows > 0 else 0)
    fig = go.Figure(data=[
        go.Bar(name='Before', x=fields, y=before_valid, marker_color='lightcoral'),
        go.Bar(name='After', x=fields, y=after_valid, marker_color='lightgreen')
    ])
    fig.update_layout(title='Data Quality: Before vs After (%)', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("🔍 Sample Cleaned Data")
    st.dataframe(cleaned_df.head(10), use_container_width=True)

def handle_targeted_fixes():
    cleaned_df = st.session_state.cleaned_df
    validation_results = st.session_state.validation_results
    st.markdown("Review and fix remaining data quality issues.")
    suggested_fixes = st.session_state.fix_suggester.suggest_fixes(cleaned_df, validation_results)
    if not suggested_fixes:
        st.success("🎉 No issues found! Your data is clean.")
        st.session_state.final_df = cleaned_df
        return
    st.subheader(f"🔧 {len(suggested_fixes)} Issues Found")
    if "applied_fixes" not in st.session_state:
        st.session_state.applied_fixes = []
    fixes_by_field = {}
    for fix in suggested_fixes:
        fixes_by_field.setdefault(fix['field'], []).append(fix)
    for field, field_fixes in fixes_by_field.items():
        st.markdown(f"**{field}** ({len(field_fixes)} issues)")
        for i, fix in enumerate(field_fixes):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1: st.text(f"Value: {fix['original_value']}")
            with col2: st.text(f"Issue: {fix['issue_type']}")
            with col3: st.text(f"Suggested: {fix['suggested_value']}")
            with col4:
                if st.button("Apply", key=f"fix_{field}_{i}"):
                    st.session_state.applied_fixes.append(fix)
                    st.success("✅ Applied")
    if st.session_state.applied_fixes:
        final_df = cleaned_df.copy()
        for fix in st.session_state.applied_fixes:
            mask = final_df[fix['field']] == fix['original_value']
            final_df.loc[mask, fix['field']] = fix['suggested_value']
        st.session_state.final_df = final_df
        st.subheader("💾 Promote Fixes")
        if st.button("🚀 Promote Applied Fixes"):
            current_promoted = st.session_state.persistence.load_promoted_fixes()
            if 'fix_rules' not in current_promoted:
                current_promoted['fix_rules'] = []
            for fix in st.session_state.applied_fixes:
                rule = {
                    'field': fix['field'],
                    'rule': fix['issue_type'],
                    'original': fix['original_value'],
                    'replacement': fix['suggested_value']
                }
                if rule not in current_promoted['fix_rules']:
                    current_promoted['fix_rules'].append(rule)
            st.session_state.persistence.save_promoted_fixes(current_promoted)
            st.success("✅ Fixes promoted and will be applied automatically to future uploads!")

def handle_final_report(filename: str):
    final_df = st.session_state.final_df
    st.success(f"🎉 Data processing complete! Processed {len(final_df)} rows.")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Rows", len(final_df))
    with col2: st.metric("Total Fields", len(final_df.columns))
    with col3:
        completeness = (final_df.notna().sum().sum() / (len(final_df) * len(final_df.columns))) * 100
        st.metric("Data Completeness", f"{completeness:.1f}%")
    st.subheader("📊 Final Cleaned Data")
    st.dataframe(final_df, use_container_width=True)
    csv_data = final_df.to_csv(index=False)
    cleaned_filename = f"cleaned_{filename}" if filename else "cleaned_data.csv"
    st.download_button("📥 Download Cleaned CSV", data=csv_data, file_name=cleaned_filename, mime="text/csv", type="primary")
    st.subheader("📈 Final Data Quality Summary")
    quality_stats = st.session_state.cleaner.calculate_quality_stats(final_df)
    plot_df = pd.DataFrame({"Field": list(quality_stats.keys()),"Completeness": [quality_stats[f]['completeness'] for f in quality_stats]})
    fig = px.bar(plot_df, x="Field", y="Completeness", title="Data Completeness by Field (%)",
                 labels={"Field": "Fields", "Completeness": "Completeness (%)"},
                 color="Completeness", color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()