import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="TRD Digital Good Projects Library",
    page_icon="🏙️",
    layout="wide"
)

# 2. Data Loading Function
@st.cache_data
def load_data():
    file_path = 'projects.csv'
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1252')
        
        df.columns = [c.strip() for c in df.columns]
        df = df[df['Project'].notna()]
        df = df[~df['Project'].str.contains("Insert your project name", na=False)]
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

# --- RESET FUNCTION ---
def reset_filters():
    # This clears all selected values in the session state
    for key in st.session_state.keys():
        if key.startswith("filter_") or key == "quick_search":
            st.session_state[key] = [] if isinstance(st.session_state[key], list) else "All"
    # Special handling for text input which doesn't like lists
    if "quick_search" in st.session_state:
        st.session_state["quick_search"] = ""

df_raw = load_data()

if not df_raw.empty:
    # 3. Sidebar - Search Interface
    st.sidebar.header("🔍 Project Directory")
    
    search_mode = st.sidebar.radio(
        "Select Search Method",
        ["Single-Action Search", "Multi-Action Search"],
        key="filter_search_mode"
    )

    sel_l1, sel_l2, sel_l3 = [], [], []

    if search_mode == "Single-Action Search":
        st.sidebar.markdown("---")
        # Step 1: Level 1
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        choice_l1 = st.sidebar.selectbox("1. Select Category (Level 1)", l1_opts, key="filter_l1_s")
        
        if choice_l1 != "All":
            sel_l1 = [choice_l1]
            # Step 2: Level 2
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == choice_l1]['Level2'].dropna().unique()])
            choice_l2 = st.sidebar.selectbox("2. Select Sub-Category (Level 2)", l2_opts, key="filter_l2_s")
            
            if choice_l2 != "All":
                sel_l2 = [choice_l2]
                # Step 3: Level 3
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                l3_subset = df_raw[df_raw['Level2'] == choice_l2]
                raw_l3 = l3_subset[l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1:
                    choice_l3 = st.sidebar.selectbox("3. Select Specific Focus (Level 3)", l3_opts, key="filter_l3_s")
                    if choice_l3 != "All":
                        sel_l3 = [choice_l3]

    else:
        # Multi-Action Search
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        sel_l1 = st.sidebar.multiselect("Select Categories (Level 1)", all_l1, key="filter_l1_m")

        if sel_l1:
            l2_opts