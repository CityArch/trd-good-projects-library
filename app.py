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
                st.error("😕 Incorrect password. Please try again.")
    return False

# 2. Data Loading with Header Cleaning
@st.cache_data
def load_data():
    file_path = 'projects.csv'
    try:
        try:
            # Standard UTF-8
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # Fallback for Excel-formatted CSVs
            df = pd.read_csv(file_path, encoding='cp1252')
        
        # CLEANING: Strip hidden spaces or tabs from column names to prevent KeyErrors
        df.columns = [str(c).strip() for c in df.columns]
        
        # Filter out empty project rows or instructions
        df = df[df['Project'].notna()]
        df = df[~df['Project'].str.contains("Insert your project name", na=False)]
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

# --- RUN AUTHENTICATION ---
if check_password():
    
    # 3. Session State Initialization
    if "reset_key" not in st.session_state:
        st.session_state.reset_key = 0
    if "search_active" not in st.session_state:
        st.session_state.search_active = False
    if "submitted_projects" not in st.session_state:
        st.session_state.submitted_projects = []
    if "temp_cats" not in st.session_state:
        st.session_state.temp_cats = []

    df_raw = load_data()

    # 4. Sidebar - Project Search
    st.sidebar.header("🔍 Project Search")
    search_mode = st.sidebar.radio(
        "Search Mode", 
        ["Single-Action Search", "Multi-Action Search"], 
        key=f"mode_{st.session_state.reset_key}"
    )

    final_l1, final_l2, final_l3 = [], [], []

    if search_mode == "Single-Action Search":
        # Cascading Logic (Dependent Dropdowns)
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        c1 = st.sidebar.selectbox("1. Category (L1)", l1_opts, key=f"s1_{st.session_state.reset_key}")
        
        if c1 != "All":
            final_l1 = [c1]
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
            c2 = st.sidebar.selectbox("2. Sub-Category (L2)", l2_opts, key=f"s2_{st.session_state.reset_key}")
            
            if c2 != "All":
                final_l2 = [c2]
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                raw_l3 = df_raw[df_raw['Level2'] == c2][l3_cols].values.ravel('K')
                # Fixed: Clean NaNs and convert to string for sorting
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("3. Specific Focus (L3)", l3_opts, key=f"s3_{st.session_state.reset_key}")
                    if c3 != "All":
                        final_l3 = [c3]
    else:
        # Multi-Action Search (Project-wide Logic)
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        final_l1 = st.sidebar.multiselect("Categories (L1)", all_l1, key=f"m1_{st.session_state.reset_key}")
        
        all_l2 = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        final_l2 = st.sidebar.multiselect("Sub-Categories (L2)", all_l2, key=f"m2_{st.session_state.reset_key}")
        
        l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        raw_l3_m = df_raw[l3_cols].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3_m) if pd.notna(x)])
        final_l3 = st.sidebar.multiselect("Specific Waivers (L3)", all_l3, key=f"m3_{st.session_state.reset_key}")

    # Search Control Buttons
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Run Search", use_container_width=True, type="primary"):
        st.session_state.search_active = True
    
    if st.sidebar.button("🧹 Clear for a new search", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.search_active = False
        st.rerun()

    # 5. Main Content Area
    st.title("🏙️ TRD Digital Good Projects Library")
    q_search = st.text_input("📝 Quick Search (Project Name or ID)", key=f"q_{st.session_state.reset_key}")

    if st.session_state.search_active or q_search:
        df = df_raw.copy()
        
        if search_mode == "Single-Action Search":
            # Filter rows based on what has been selected (works for partial L1/L2 selection)
            if final_l1: df = df[df['Level1'].isin(final_l1)]
            if final_l2: df = df[df['Level2'].isin(final_l2)]
            if final_l3:
                df = df[df['Level3-1'].isin(final_l3) | df['Level3-2'].isin(final_l3) | 
                        df['Level3-3'].isin(final_l3) | df['Level3-4'].isin(final_l3)]
        else:
            # Multi-Action Search (Project-Centric "AND" matching)
            if final_l1 or final_l2 or final_l3:
                def check_project_match(group):
                    proj_l1 = set(group['Level1'].dropna())
                    proj_l2 = set(group['Level2'].dropna())
                    # Flatten all L3 columns for that project ID
                    proj_l3 = set(group[['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']].values.flatten())
                    proj_l3 = {str(x) for x in proj_l3 if pd.notna(x)}
                    
                    match_l1 = all(i in proj_l1 for i in final_l1)
                    match_l2 = all(i in proj_l2 for i in final_l2)
                    match_l3 = all(i in proj_l3 for i in final_l3)
                    return match_l1 and match_l2 and match_l3
                
                # Filter by IDs that meet ALL criteria across their row history
                m_ids = df_raw.groupby('Project ID').filter(check_project_match)['Project ID'].unique()
                df = df_raw[df_raw['Project ID'].isin(m_ids)]

        # Apply global text search
        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | 
                    df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

        # Display Results
        st.subheader(f"Found {len(df)} matching project entries")
        st.divider()

        if not df.empty:
            grid = st.columns(3)
            for idx, (i, row) in enumerate(df.iterrows()):