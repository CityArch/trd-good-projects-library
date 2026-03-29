import streamlit as st
import pandas as pd
from datetime import date

# 1. Page Configuration
st.set_page_config(
    page_title="TRD Digital Good Projects Library",
    page_icon="🏙️",
    layout="wide"
)

# --- PASSWORD PROTECTION ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True

    st.title("🔒 TRD Project Library Access")
    placeholder = st.empty()
    with placeholder.form("login_form"):
        st.markdown("Please enter the access password to continue.")
        password = st.text_input("Password", type="password")
        submit_password = st.form_submit_button("Enter")
        if submit_password:
            if password == "1234567890":
                st.session_state.password_correct = True
                placeholder.empty()
                st.rerun()
            else:
                st.error("😕 Incorrect password.")
    return False

# 2. Data Loading with Header Cleaning
@st.cache_data
def load_data():
    file_path = 'projects.csv'
    try:
        try:
            # Try standard UTF-8 first
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # Fallback for Excel-style CSVs
            df = pd.read_csv(file_path, encoding='cp1252')
        
        # FIX FOR KEYERROR: Clean all column headers (strip spaces/tabs)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Verify required columns exist
        required = ['Project', 'Project ID', 'Level1', 'Level2']
        missing = [col for col in required if col not in df.columns]
        if missing:
            st.error(f"⚠️ Missing columns in CSV: {missing}. Found: {list(df.columns)}")
            st.stop()
            
        df = df[df['Project'].notna()]
        df = df[~df['Project'].str.contains("Insert your project name", na=False)]
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

# --- RUN AUTHENTICATION ---
if check_password():
    
    # Initialize Session States
    if "reset_key" not in st.session_state: st.session_state.reset_key = 0
    if "search_active" not in st.session_state: st.session_state.search_active = False
    if "submitted_projects" not in st.session_state: st.session_state.submitted_projects = []
    if "temp_cats" not in st.session_state: st.session_state.temp_cats = []

    df_raw = load_data()

    # 3. Sidebar - Search Logic
    st.sidebar.header("🔍 Project Search")
    search_mode = st.sidebar.radio(
        "Search Mode", 
        ["Single-Action Search", "Multi-Action Search"], 
        key=f"mode_{st.session_state.reset_key}"
    )

    final_l1, final_l2, final_l3 = [], [], []

    if search_mode == "Single-Action Search":
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        c1 = st.sidebar.selectbox("1. Category (L1)", l1_opts, key=f"s1_{st.session_state.reset_key}")
        
        if c1 != "All":
            final_l1 = [c1]
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
            c2 = st.sidebar.selectbox("2. Sub-Category (L2)", l2_opts, key=f"s2_{st.session_state.reset_key}")
            
            if c2 != "All":
                final_l2 = [c2]
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                # Filter data for L3 options, ensuring we handle the 4 columns
                raw_l3 = df_raw[df_raw['Level2'] == c2][l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("3. Specific Focus (L3)", l3_opts, key=f"s3_{st.session_state.reset_key}")
                    if c3 != "All": final_l3 = [c3]
    else:
        # Multi-Action Search
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        final_l1 = st.sidebar.multiselect("Categories (L1)", all_l1, key=f"m1_{st.session_state.reset_key}")
        
        all_l2 = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        final_