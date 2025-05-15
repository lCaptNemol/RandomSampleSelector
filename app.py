import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="ID Sampling Tool",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for background color - forcing it to light mode !important
st.markdown("""
<style>
    /* Force blue background regardless of dark/light mode */
    .stApp {
        background-color: #005EAA !important;
    }
    body {
        background-color: #005EAA !important;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stAlert {
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
    .st-bx {
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        padding: 20px;
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        margin-bottom: 10px;
    }
    .stDownloadButton {
        margin-top: 15px;
    }
    .stButton > button {
        margin-top: 15px;
        padding: 8px 15px;
        font-weight: 600;
    }
    .success-box {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    .info-box {
        background-color: #e2f0fd;
        border-color: #b8daff;
        color: #004085;
    }
    .value-metric {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    .value-metric h3 {
        margin: 0;
        font-size: 1.8rem;
        color: #d32f2f;
    }
    .value-metric p {
        margin: 0;
        color: #d32f2f;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("ID Sampling Tool")
st.sidebar.image("generated-icon.png", width=100)

page = st.sidebar.radio("Navigation", ["Sampling Tool", "About"])

# Helper Functions
def read_uploaded_file(uploaded_file):
    """Read an uploaded CSV or Excel file and return a list of numeric IDs."""
    if uploaded_file is None:
        return None
    
    try:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Try different approaches to handle files with or without headers
        if file_ext == '.csv':
            # CSV files - try to auto-detect header
            df = pd.read_csv(uploaded_file)
        elif file_ext in ['.xlsx', '.xls']:
            # Excel files - read with default header inference
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_ext}. Please upload CSV or Excel files.")
            return None
        
        # Extract first column and convert to numeric
        if len(df.columns) > 0:
            # Get first column
            first_col = df.iloc[:, 0]
            
            # Check if first value might be a header (non-numeric)
            if len(first_col) > 1:
                try:
                    # Try to convert first value to see if it's numeric
                    int(float(first_col.iloc[0]))
                except (ValueError, TypeError):
                    # First value is likely a header, skip it
                    first_col = first_col.iloc[1:]
            
            # Filter out non-numeric values
            valid_ids = []
            for value in first_col:
                try:
                    # Try to convert to int
                    num_value = int(float(value))
                    valid_ids.append(num_value)
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    continue
            
            return valid_ids
        else:
            st.error("File contains no data or is incorrectly formatted.")
            return None
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def calculate_eligible_ids(full_pool, current_selections=None, excluded_ids=None, min_id=None, max_id=None):
    """Calculate eligible IDs for sampling."""
    if full_pool is None or len(full_pool) == 0:
        return []
    
    if current_selections is None:
        current_selections = []
    
    if excluded_ids is None:
        excluded_ids = []
    
    # Apply range filters
    filtered_pool = full_pool
    if min_id is not None:
        filtered_pool = [id for id in filtered_pool if id >= min_id]
    
    if max_id is not None:
        filtered_pool = [id for id in filtered_pool if id <= max_id]
    
    # Exclude current selections and excluded IDs
    to_exclude = set(current_selections + excluded_ids)
    eligible_ids = [id for id in filtered_pool if id not in to_exclude]
    
    return eligible_ids

def sample_ids(eligible_ids, sample_size, seed=None):
    """Perform random sampling of IDs."""
    if eligible_ids is None or len(eligible_ids) == 0:
        return []
    
    if sample_size <= 0:
        return []
    
    # Set seed if provided
    if seed is not None:
        np.random.seed(seed)
    
    # Sample IDs
    if sample_size >= len(eligible_ids):
        return eligible_ids
    else:
        return list(np.random.choice(eligible_ids, size=sample_size, replace=False))

def create_final_dataset(current_selections=None, new_sample=None):
    """Combine current selections and new sample to create final dataset."""
    if current_selections is None:
        current_selections = []
    
    if new_sample is None:
        new_sample = []
    
    # Combine and sort
    final_dataset = sorted(current_selections + new_sample)
    
    return final_dataset

def display_metrics(full_pool, eligible_ids, current_selections, new_sample):
    """Display summary metrics."""
    full_pool_len = len(full_pool) if full_pool is not None else 0
    eligible_ids_len = len(eligible_ids) if eligible_ids is not None else 0
    current_selections_len = len(current_selections) if current_selections is not None else 0
    new_sample_len = len(new_sample) if new_sample is not None else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="value-metric">'
                  f'<h3 style="color: #d32f2f;">{full_pool_len}</h3>'
                  '<p style="color: #d32f2f;">Total IDs in Pool</p>'
                  '</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="value-metric">'
                  f'<h3 style="color: #d32f2f;">{eligible_ids_len}</h3>'
                  '<p style="color: #d32f2f;">Eligible for Sampling</p>'
                  '</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="value-metric">'
                  f'<h3 style="color: #d32f2f;">{current_selections_len}</h3>'
                  '<p style="color: #d32f2f;">Previously Selected</p>'
                  '</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="value-metric">'
                  f'<h3 style="color: #d32f2f;">{new_sample_len}</h3>'
                  '<p style="color: #d32f2f;">Newly Selected</p>'
                  '</div>', unsafe_allow_html=True)

# Initialize session state if it doesn't exist
if 'full_pool' not in st.session_state:
    st.session_state.full_pool = None
if 'current_selections' not in st.session_state:
    st.session_state.current_selections = None
if 'excluded_ids' not in st.session_state:
    st.session_state.excluded_ids = None
if 'eligible_ids' not in st.session_state:
    st.session_state.eligible_ids = None
if 'new_sample' not in st.session_state:
    st.session_state.new_sample = None
if 'final_dataset' not in st.session_state:
    st.session_state.final_dataset = None
if 'has_sampling_run' not in st.session_state:
    st.session_state.has_sampling_run = False
if 'validation_errors' not in st.session_state:
    st.session_state.validation_errors = []

def reset_app():
    """Reset all app state."""
    st.session_state.full_pool = None
    st.session_state.current_selections = None
    st.session_state.excluded_ids = None
    st.session_state.eligible_ids = None
    st.session_state.new_sample = None
    st.session_state.final_dataset = None
    st.session_state.has_sampling_run = False
    st.session_state.validation_errors = []

# Main Page
if page == "Sampling Tool":
    st.title("ID Sampling Tool")
    
    # Data Input Section
    st.markdown('<div class="st-bx">', unsafe_allow_html=True)
    st.header("Data Input")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        full_pool_file = st.file_uploader("Upload Full ID Pool (CSV or Excel)", 
                                        type=["csv", "xlsx", "xls"])
        st.caption("A file containing all possible IDs to sample from.")
        if full_pool_file is not None:
            st.session_state.full_pool = read_uploaded_file(full_pool_file)
    
    with col2:
        current_selections_file = st.file_uploader("Upload Current Selections (CSV or Excel, optional)", 
                                                type=["csv", "xlsx", "xls"])
        st.caption("IDs already selected that should be retained.")
        if current_selections_file is not None:
            st.session_state.current_selections = read_uploaded_file(current_selections_file)
    
    with col3:
        excluded_ids_file = st.file_uploader("Upload Excluded IDs (CSV or Excel, optional)", 
                                          type=["csv", "xlsx", "xls"])
        st.caption("IDs that must be excluded from sampling.")
        if excluded_ids_file is not None:
            st.session_state.excluded_ids = read_uploaded_file(excluded_ids_file)
    
    st.markdown('<hr>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sample_size = st.number_input("Number of New IDs to Sample:", 
                                     value=10, min_value=1, step=1)
        st.caption("How many new unique IDs to sample")
    
    with col2:
        seed = st.number_input("Random Seed (optional):", 
                              value=None, min_value=1, step=1)
        st.caption("Set for reproducible sampling")
    
    with col3:
        min_id = st.number_input("Minimum ID Value (optional):", 
                               value=None, step=1)
        max_id = st.number_input("Maximum ID Value (optional):", 
                               value=None, step=1)
        st.caption("Optional range filtering")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        run_sampling = st.button("Run Sampling", type="primary")
        reset_btn = st.button("Reset All", type="secondary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle reset button
    if reset_btn:
        reset_app()
        st.rerun()
    
    # Run sampling when button is clicked
    if run_sampling:
        # Reset validation errors
        st.session_state.validation_errors = []
        
        # Validate inputs
        if st.session_state.full_pool is None:
            st.session_state.validation_errors.append("Please upload a Full ID Pool file.")
        
        # If current selections is None, make it an empty list
        if st.session_state.current_selections is None:
            st.session_state.current_selections = []
        
        # If excluded IDs is None, make it an empty list
        if st.session_state.excluded_ids is None:
            st.session_state.excluded_ids = []
        
        # Validate uniqueness
        if st.session_state.full_pool is not None:
            if len(st.session_state.full_pool) != len(set(st.session_state.full_pool)):
                st.session_state.validation_errors.append("Full ID Pool contains duplicate values.")
        
        if len(st.session_state.current_selections) > 0:
            if len(st.session_state.current_selections) != len(set(st.session_state.current_selections)):
                st.session_state.validation_errors.append("Current Selections contains duplicate values.")
        
        if len(st.session_state.excluded_ids) > 0:
            if len(st.session_state.excluded_ids) != len(set(st.session_state.excluded_ids)):
                st.session_state.validation_errors.append("Excluded IDs contains duplicate values.")
        
        # Check for overlap between current selections and excluded IDs
        if len(st.session_state.current_selections) > 0 and len(st.session_state.excluded_ids) > 0:
            overlap = set(st.session_state.current_selections).intersection(st.session_state.excluded_ids)
            if len(overlap) > 0:
                overlap_str = ", ".join(str(id) for id in list(overlap)[:5])
                if len(overlap) > 5:
                    overlap_str += "... and more"
                st.session_state.validation_errors.append(f"IDs appear in both Current Selections and Excluded IDs: {overlap_str}")
        
        # Apply optional range filters and calculate eligible IDs
        if st.session_state.full_pool is not None:
            st.session_state.eligible_ids = calculate_eligible_ids(
                st.session_state.full_pool,
                st.session_state.current_selections,
                st.session_state.excluded_ids,
                min_id,
                max_id
            )
            
            # Validate if there are enough eligible IDs
            if sample_size > len(st.session_state.eligible_ids):
                st.session_state.validation_errors.append(
                    f"Requested sample size ({sample_size}) exceeds available eligible IDs ({len(st.session_state.eligible_ids)})."
                )
        
        # If no validation errors, proceed with sampling
        if len(st.session_state.validation_errors) == 0 and st.session_state.eligible_ids is not None:
            # Sample new IDs
            if sample_size > 0 and len(st.session_state.eligible_ids) > 0:
                st.session_state.new_sample = sample_ids(st.session_state.eligible_ids, sample_size, seed)
            else:
                st.session_state.new_sample = []
            
            # Create final dataset
            st.session_state.final_dataset = create_final_dataset(
                st.session_state.current_selections,
                st.session_state.new_sample
            )
            
            # Mark that sampling has run successfully
            st.session_state.has_sampling_run = True
        else:
            # If there are errors, don't proceed with sampling
            st.session_state.has_sampling_run = False
    
    # Display validation messages
    if len(st.session_state.validation_errors) > 0:
        st.error("Validation Errors:")
        for error in st.session_state.validation_errors:
            st.markdown(f"- {error}")
    elif st.session_state.has_sampling_run:
        st.success("Sampling completed successfully!")
    
    # Results Section
    if st.session_state.has_sampling_run:
        st.markdown('<div class="st-bx info-box">', unsafe_allow_html=True)
        st.header("Summary Statistics")
        
        display_metrics(
            st.session_state.full_pool,
            st.session_state.eligible_ids,
            st.session_state.current_selections,
            st.session_state.new_sample
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="st-bx success-box">', unsafe_allow_html=True)
        st.header("Final Dataset (Current + New Selections)")
        
        # Download options
        col1, col2 = st.columns([1, 3])
        with col1:
            download_format = st.radio("File Format:", ["CSV", "Excel"])
        
        # Create the final dataset DataFrame
        if st.session_state.final_dataset is not None:
            df = pd.DataFrame({
                "ID": st.session_state.final_dataset,
                "Source": ["Current" if id in st.session_state.current_selections else "New" 
                         for id in st.session_state.final_dataset]
            })
            
            # Download button
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if download_format == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Final Dataset",
                    data=csv,
                    file_name=f"sampled_ids_{timestamp}.csv",
                    mime="text/csv"
                )
            else:  # Excel
                # Save to a temporary file
                temp_file = f"temp_sampled_ids_{timestamp}.xlsx"
                df.to_excel(temp_file, index=False, sheet_name='Sampled IDs')
                
                # Read the file
                with open(temp_file, "rb") as file:
                    excel_data = file.read()
                
                # Provide download button
                st.download_button(
                    label="Download Final Dataset",
                    data=excel_data,
                    file_name=f"sampled_ids_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Clean up the temp file
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            # Display the data table
            st.dataframe(
                df,
                column_config={
                    "ID": st.column_config.NumberColumn("ID"),
                    "Source": st.column_config.TextColumn("Source")
                },
                hide_index=True,
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

# About Page
elif page == "About":
    st.title("About the ID Sampling Tool")
    
    st.markdown("""
    ## ID Sampling Tool
    
    This interactive Streamlit web application supports data scientists and researchers in generating randomized selections of unique numeric IDs from a master dataset with **real-time exclusion and retention control**.
    
    Unlike static sampling tools, this app enables **on-the-fly randomization** even as the researcher actively filters out IDs for exclusion. It’s ideal for workflows where selection criteria evolve during exploratory analysis, data cleaning, or operational constraints.
                
    ### Features:
    
    - **Upload Data Files**: Import your full ID pool, current selections, and excluded IDs
    - **Control Your Sampling**: Specify sample size, set a random seed for reproducibility, and apply ID range filters
    - **Validate Your Data**: Automatic checks for duplicates and conflicts between datasets
    - **Export Results**: Download your final dataset in CSV or Excel format
    
    ### How to Use:
    
    1. Upload your Full ID Pool file (required)
    2. Optionally upload Current Selections and Excluded IDs files
    3. Set the number of new IDs to sample
    4. Optionally set a random seed for reproducible results
    5. Optionally apply ID range filters
    6. Click "Run Sampling"
    7. Review the results and download the final dataset
    
    ### File Formats:
    
    - Upload CSV or Excel files
    - The first column of each file should contain the numeric IDs
    - Other columns will be ignored
    """)
