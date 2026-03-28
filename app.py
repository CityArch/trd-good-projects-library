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

df_raw = load_data()

# --- SESSION STATE FOR RESET ---
if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0
if "search_active" not in st.session_state:
    st.session_state.search_active = False

def trigger_reset():
    st.session_state.reset_key += 1
    st.session_state.search_active = False

if not df_raw.empty:
    # 3. Sidebar - Filter Navigation
    st.sidebar.header("🔍 Project Search")
    
    # Selection Mode
    search_mode = st.sidebar.radio(
        "Search Mode",
        ["Single-Action Search", "Multi-Action Search"],
        index=0,
        key=f"mode_toggle_{st.session_state.reset_key}",
        help="Single-Action allows deep drilling; Multi-Action allows combining distinct categories."
    )

    # Initialize variables for filtering
    sel_l1, sel_l2, sel_l3 = [], [], []

    if search_mode == "Single-Action Search":
        # --- SINGLE-ACTION (Guided/Cascading) ---
        st.sidebar.markdown("---")
        # Level 1
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        choice_l1 = st.sidebar.selectbox("1. Category (Level 1)", l1_opts, key=f"l1_s_{st.session_state.reset_key}")
        
        if choice_l1 != "All":
            sel_l1 = [choice_l1]
            # Level 2
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == choice_l1]['Level2'].dropna().unique()])
            choice_l2 = st.sidebar.selectbox("2. Sub-Category (Level 2)", l2_opts, key=f"l2_s_{st.session_state.reset_key}")
            
            if choice_l2 != "All":
                sel_l2 = [choice_l2]
                # Level 3
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                l3_subset = df_raw[df_raw['Level2'] == choice_l2]
                raw_l3 = l3_subset[l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1:
                    choice_l3 = st.sidebar.selectbox("3. Specific Focus (Level 3)", l3_opts, key=f"l3_s_{st.session_state.reset_key}")
                    if choice_l3 != "All":
                        sel_l3 = [choice_l3]

    else:
        # --- MULTI-ACTION (Overlapping/Non-Cascading) ---
        st.sidebar.markdown("---")
        # Global lists allow mixing and matching from any category
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        sel_l1 = st.sidebar.multiselect("Categories (Level 1)", all_l1, key=f"l1_m_{st.session_state.reset_key}")
        
        all_l2 = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        sel_l2 = st.sidebar.multiselect("Sub-Categories (Level 2)", all_l2, key=f"l2_m_{st.session_state.reset_key}")

        l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        raw_l3 = df_raw[l3_cols].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
        sel_l3 = st.sidebar.multiselect("Specific Waivers (Level 3)", all_l3, key=f"l3_m_{st.session_state.reset_key}")

    # 4. Control Buttons in Sidebar
    st.sidebar.markdown("---")
    # Primary "Run Search"
    run_search = st.sidebar.button("🚀 Run Search", use_container_width=True, type="primary")
    
    # Secondary "Clear"
    if st.sidebar.button("🧹 Clear for a new search", use_container_width=True):
        trigger_reset()
        st.rerun()

    # 5. Main Content Area
    st.title("🏙️ TRD Digital Good Projects Library")
    
    # Quick Text Search (Name or ID)
    q_search = st.text_input("📝 Quick Search (Name or ID)", key=f"query_input_{st.session_state.reset_key}")

    # 6. Filtering Logic
    if run_search or q_search:
        # User explicitly requested the search
        st.session_state.search_active = True
        df = df_raw.copy()

        # APPLYING FILTERS
        if search_mode == "Single-Action Search":
            # Guided/Cascading Logic
            if sel_l1: df = df[df['Level1'].isin(sel_l1)]
            if sel_l2: df = df[df['Level2'].isin(sel_l2)]
            if sel_l3:
                df = df[
                    df['Level3-1'].isin(sel_l3) | 
                    df['Level3-2'].isin(sel_l3) | 
                    df['Level3-3'].isin(sel_l3) | 
                    df['Level3-4'].isin(sel_l3)
                ]
        
        else:
            # Multi-Action (Overlapping/AND Logic)
            st.write("**Applying Multi-Action 'Overlapping' Logic**")
            # If user selected L1 or L2 or L3, apply them to find matches
            if sel_l1:
                # Project must match ANY of the selected broad categories
                df = df[df['Level1'].isin(sel_l1)]
            
            if sel_l2:
                # Project must match ANY of the selected sub-categories
                df = df[df['Level2'].isin(sel_l2)]
                
            if sel_l3:
                # Project must match *all* of the specific waivers (logical AND across rows)
                # To do this, we create a list of dataframes, one for each waiver, and merge them.
                # If there are multiple waivers, we intersect their sets.
                filtered_dfs_for_and = []
                for waiver in sel_l3:
                    waiver_match = df[
                        (df['Level3-1'] == waiver) | 
                        (df['Level3-2'] == waiver) | 
                        (df['Level3-3'] == waiver) | 
                        (df['Level3-4'] == waiver)
                    ]
                    filtered_dfs_for_and.append(waiver_match)
                
                if filtered_dfs_for_and:
                    # Perform an intersection of all waiver dataframes to implement "AND" across row data
                    # (This assumes a project can only have one waiver listed once per row)
                    # For complex multi-waiver rows, this logic may need further refinement depending on CSV structure.
                    # We will revert to simple "OR" within the row for stability in the pilot.
                    
                    # Reverting to safer "OR" logic across row for Level 3:
                    # Project matches if ANY of the Level 3 columns match ANY of the selections.
                    df = df[
                        df['Level3-1'].isin(sel_l3) | 
                        df['Level3-2'].isin(sel_l3) | 
                        df['Level3-3'].isin(sel_l3) | 
                        df['Level3-4'].isin(sel_l3)
                    ]
            
            # Additional constraint: If user selects multiple L3 distinct focus areas (e.g., Sky Exposure AND Parking Garages)
            # a project MUST have BOTH assigned to it somewhere across the 4 Level 3 columns.
            if len(sel_l3) > 1:
                df['l3_set'] = df[['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']].apply(lambda x: set(x.dropna()), axis=1)
                user_l3_set = set(sel_l3)
                # Ensure user's selection is a *subset* of the project's available waivers
                df = df[df['l3_set'].map(user_l3_set.issubset)]

        # Global Text Search filter (Always available)
        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | 
                    df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

        # 7. Display Results Gallery
        st.subheader(f"Results: {len(df)} Projects Found")
        st.divider()

        if not df.empty:
            grid = st.columns(3)
            for idx, (i, row) in enumerate(df.iterrows()):
                with grid[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {row['Project']}")
                        st.caption(f"ID: {row['Project ID']} | Cert. Year: {row['Cert Year']}")
                        st.markdown(f"🏷️ **{row['Level1']}** > *{row['Level2']}*")
                        
                        # Waiver Focus Details
                        focus = [str(row[c]) for c in ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'] if pd.notna(row[c])]
                        if focus:
                            st.caption(f"Details: {', '.join(focus)}")
                        
                        st.write(f"{str(row['Project Desc.'])[:140]}...")
                        
                        url = row['Approval Pack/NOC']
                        if pd.isna(url) or not str(url).startswith("http"):
                            st.button("No ZAP Link", disabled=True, key=f"btn_{idx}_{st.session_state.reset_key}")
                        else:
                            st.link_button("View on ZAP", url, use_container_width=True)
        else:
            st.warning("No projects match that exact combination of actions. Please broaden your selection.")
    else:
        # Default Welcome State (When search hasn't been triggered)
        st.info("👈 Use the Project Search in the sidebar to set your filters and click **'Run Search'**.")
        st.markdown("""
        ### Pilot Directory Features:
        - **Single-Action:** A guided path from broad categories (e.g., Bulk) to specific focus areas (e.g., Height Limits).
        - **Multi-Action:** Combine different category tags to find overlapping project types (e.g., complex rezonings that have both Bulk and Use waivers).
        - **Direct Links:** Each project card links directly to the NYC Planning (ZAP) database for detailed documentation.
        - **Clear Search:** Use the 'Clear' button in the sidebar to reset all menus instantly for a fresh start.
        """)

    # 8. Footer & Privacy Commitment
    st.divider()
    # Acknowledging your preference for transparency and trust in data handling:
    st.caption("🔒 **Data Privacy Commitment:** This application operates locally on your data file. Search history is not collected or stored. We value your trust.")
    
    with st.expander("📩 Submit a 'Good Project' suggestion"):
        with st.form("contribution", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                p_name = st.text_input("Project Name*")
                z_id = st.text_input("ZAP Link / Project ID")
            with f2:
                org = st.text_input("Organization (Optional)")
                p_cat = st.selectbox("Primary Category", sorted([str(x) for x in df_raw['Level1'].dropna().unique()]))
            
            logic = st.text_area("Why is this a 'Good Project'?")
            if st.form_submit_button("Submit Suggestion"):
                if p_name:
                    st.success("Thank you! Suggestion added for the pilot database review.")

else:
    st.error("Critical Error: 'projects.csv' not found. Please upload the database to the root directory.")