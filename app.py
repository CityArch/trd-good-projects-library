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
        
        # Clean column names
        df.columns = [c.strip() for c in df.columns]
        # Remove empty rows and template instructions
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
    
    search_mode = st.sidebar.radio(
        "Search Mode",
        ["Single-Action Search", "Multi-Action Search"],
        index=0,
        key=f"mode_toggle_{st.session_state.reset_key}"
    )

    # Filtering Criteria Containers
    sel_l1, sel_l2, sel_l3 = [], [], []

    if search_mode == "Single-Action Search":
        st.sidebar.markdown("---")
        # Step 1: Level 1
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        c1 = st.sidebar.selectbox("1. Category (Level 1)", l1_opts, key=f"l1_s_{st.session_state.reset_key}")
        
        if c1 != "All":
            sel_l1 = [c1]
            # Step 2: Level 2
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
            c2 = st.sidebar.selectbox("2. Sub-Category (Level 2)", l2_opts, key=f"l2_s_{st.session_state.reset_key}")
            
            if c2 != "All":
                sel_l2 = [choice_l2 := c2]
                # Step 3: Level 3
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                l3_subset = df_raw[df_raw['Level2'] == c2]
                raw_l3 = l3_subset[l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("3. Specific Focus (Level 3)", l3_opts, key=f"l3_s_{st.session_state.reset_key}")
                    if c3 != "All":
                        sel_l3 = [c3]
    else:
        # --- MULTI-ACTION (Overlapping "AND" Logic) ---
        st.sidebar.markdown("---")
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        sel_l1 = st.sidebar.multiselect("Categories (Level 1)", all_l1, key=f"l1_m_{st.session_state.reset_key}")
        
        all_l2 = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        sel_l2 = st.sidebar.multiselect("Sub-Categories (Level 2)", all_l2, key=f"l2_m_{st.session_state.reset_key}")

        l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        raw_l3 = df_raw[l3_cols].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
        sel_l3 = st.sidebar.multiselect("Specific Waivers (Level 3)", all_l3, key=f"l3_m_{st.session_state.reset_key}")

    # 4. Control Buttons
    st.sidebar.markdown("---")
    run_search = st.sidebar.button("🚀 Run Search", use_container_width=True, type="primary")
    
    if st.sidebar.button("🧹 Clear for a new search", use_container_width=True):
        trigger_reset()
        st.rerun()

    # 5. Main UI
    st.title("🏙️ TRD Digital Good Projects Library")
    q_search = st.text_input("📝 Quick Search (Name or ID)", key=f"query_input_{st.session_state.reset_key}")

    # 6. Filtering Logic (Project-Centric)
    if run_search or q_search:
        st.session_state.search_active = True
        
        # We find projects (by Project ID) that satisfy the conditions
        df = df_raw.copy()
        
        if search_mode == "Single-Action Search":
            # Simple row-based filtering for guided search
            if sel_l1: df = df[df['Level1'].isin(sel_l1)]
            if sel_l2: df = df[df['Level2'].isin(sel_l2)]
            if sel_l3:
                df = df[df['Level3-1'].isin(sel_l3) | df['Level3-2'].isin(sel_l3) | 
                        df['Level3-3'].isin(sel_l3) | df['Level3-4'].isin(sel_l3)]
        else:
            # --- PROJECT-CENTRIC "AND" LOGIC ---
            # 1. Group by Project ID to see all attributes for each project
            def check_project_match(group):
                project_l1 = set(group['Level1'].dropna())
                project_l2 = set(group['Level2'].dropna())
                project_l3 = set(group[['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']].values.flatten())
                project_l3 = {str(x) for x in project_l3 if pd.notna(x)}

                # Does this project have ALL selected L1s, L2s, and L3s across its rows?
                match_l1 = all(item in project_l1 for item in sel_l1)
                match_l2 = all(item in project_l2 for item in sel_l2)
                match_l3 = all(item in project_l3 for item in sel_l3)
                
                return match_l1 and match_l2 and match_l3

            if sel_l1 or sel_l2 or sel_l3:
                # Get IDs of projects that match the multi-criteria
                matching_ids = df_raw.groupby('Project ID').filter(check_project_match)['Project ID'].unique()
                df = df_raw[df_raw['Project ID'].isin(matching_ids)]
                
                # Further refine visible rows: Show rows that match at least one of the selected criteria
                if sel_l1 or sel_l2 or sel_l3:
                    mask = (df['Level1'].isin(sel_l1)) | (df['Level2'].isin(sel_l2)) | \
                           (df['Level3-1'].isin(sel_l3)) | (df['Level3-2'].isin(sel_l3)) | \
                           (df['Level3-3'].isin(sel_l3)) | (df['Level3-4'].isin(sel_l3))
                    df = df[mask]

        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | 
                    df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

        # 7. Display Results
        st.subheader(f"Results: {len(df)} Entries Found")
        st.divider()

        if not df.empty:
            grid = st.columns(3)
            # Display every matching entry (Innovation QNS will appear multiple times if it has multiple matching rows)
            for idx, (i, row) in enumerate(df.iterrows()):
                with grid[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {row['Project']}")
                        st.caption(f"ID: {row['Project ID']} | {row['Cert Year']}")
                        st.markdown(f"🏷️ **{row['Level1']}** > *{row['Level2']}*")
                        l3_vals = [row[c] for c in ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'] if pd.notna(row[c])]
                        if l3_vals:
                            st.caption(f"Details: {', '.join([str(t) for t in l3_vals])}")
                        st.write(f"{str(row['Project Desc.'])[:140]}...")
                        
                        url = row['Approval Pack/NOC']
                        if pd.isna(url) or not str(url).startswith("http"):
                            st.button("No Link", disabled=True, key=f"btn_{idx}_{st.session_state.reset_key}")
                        else:
                            st.link_button("View on ZAP", url, use_container_width=True)
        else:
            st.warning("No projects match that exact combination of actions.")
    else:
        st.info("👈 Use the sidebar filters and click **'Run Search'** to explore.")

    # 8. Privacy & Footer
    st.divider()
    st.caption("🔒 **Data Privacy:** This is a professional pilot tool. We value your trust; search data is never stored or sold.")
    
    with st.expander("📩 Submit a 'Good Project'"):
        with st.form("contribution", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                p_name = st.text_input("Project Name*")
                z_link = st.text_input("ZAP Link")
            with f2:
                org = st.text_input("Organization")
                all_l1_sub = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
                p_cat = st.selectbox("Category", all_l1_sub if all_l1_sub else ["General"])
            if st.form_submit_button("Submit") and p_name:
                st.success("Thank you! Suggestion added.")
else:
    st.error("Error: Could not locate 'projects.csv'.")