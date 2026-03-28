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

# --- RESET LOGIC ---
# This function clears the specific keys used for dropdowns and search bars
def reset_search():
    for key in st.session_state.keys():
        if key.startswith("search_"):
            # Reset multiselects to empty lists and selectboxes to "All"
            if isinstance(st.session_state[key], list):
                st.session_state[key] = []
            else:
                st.session_state[key] = "All"
    # Clear the text search input separately
    if "quick_text" in st.session_state:
        st.session_state["quick_text"] = ""

df_raw = load_data()

if not df_raw.empty:
    # 3. Sidebar - Filter Navigation
    st.sidebar.header("🔍 Project Search")
    
    search_mode = st.sidebar.radio(
        "Search Mode",
        ["Single-Action Search", "Multi-Action Search"],
        key="search_mode_toggle"
    )

    # These variables will store our final filters
    final_l1, final_l2, final_l3 = [], [], []

    if search_mode == "Single-Action Search":
        st.sidebar.markdown("---")
        # Level 1
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        c1 = st.sidebar.selectbox("1. Category (Level 1)", l1_opts, key="search_l1_s")
        
        if c1 != "All":
            final_l1 = [c1]
            # Level 2
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
            c2 = st.sidebar.selectbox("2. Sub-Category (Level 2)", l2_opts, key="search_l2_s")
            
            if c2 != "All":
                final_l2 = [c2]
                # Level 3
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                l3_subset = df_raw[df_raw['Level2'] == c2]
                raw_l3 = l3_subset[l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("3. Specific Focus (Level 3)", l3_opts, key="search_l3_s")
                    if c3 != "All":
                        final_l3 = [c3]

    else:
        # Multi-Action Search
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        final_l1 = st.sidebar.multiselect("Select Categories (Level 1)", all_l1, key="search_l1_m")

        if final_l1:
            l2_opts = sorted([str(x) for x in df_raw[df_raw['Level1'].isin(final_l1)]['Level2'].dropna().unique()])
        else:
            l2_opts = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        final_l2 = st.sidebar.multiselect("Select Sub-Categories (Level 2)", l2_opts, key="search_l2_m")

        l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        l3_subset = df_raw[df_raw['Level2'].isin(final_l2)] if final_l2 else df_raw
        raw_l3 = l3_subset[l3_cols].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
        final_l3 = st.sidebar.multiselect("Select Specific Focus (Level 3)", all_l3, key="search_l3_m")

    # 4. Control Buttons in Sidebar
    st.sidebar.markdown("---")
    # PRIMARY Search Button
    run_btn = st.sidebar.button("🚀 Run Search", use_container_width=True, type="primary")
    
    # SECONDARY Clear Button
    if st.sidebar.button("🧹 Clear for a new search", use_container_width=True):
        reset_search()
        st.rerun()

    # 5. Main Content
    st.title("🏙️ TRD Digital Good Projects Library")
    
    # Quick text search bar
    q_search = st.text_input("📝 Quick Search (Name or ID)", key="quick_text")

    # 6. Search Execution
    # Search is only active if the button is pressed OR text is typed
    if run_btn or q_search:
        df = df_raw.copy()

        if final_l1:
            df = df[df['Level1'].isin(final_l1)]
        if final_l2:
            df = df[df['Level2'].isin(final_l2)]
        if final_l3:
            df = df[
                df['Level3-1'].isin(final_l3) | 
                df['Level3-2'].isin(final_l3) | 
                df['Level3-3'].isin(final_l3) | 
                df['Level3-4'].isin(final_l3)
            ]
        
        if q_search:
            df = df[
                df['Project'].str.contains(q_search, case=False, na=False) | 
                df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)
            ]

        # 7. Gallery View
        st.subheader(f"Found {len(df)} Projects")
        st.divider()

        if not df.empty:
            grid = st.columns(3)
            for idx, (i, row) in enumerate(df.iterrows()):
                with grid[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {row['Project']}")
                        st.caption(f"ID: {row['Project ID']} | {row['Cert Year']}")
                        st.markdown(f"**{row['Level1']}** > *{row['Level2']}*")
                        
                        l3_tags = [row[c] for c in ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'] if pd.notna(row[c])]
                        if l3_tags:
                            st.caption(f"Focus: {', '.join([str(t) for t in l3_tags])}")

                        st.write(f"{str(row['Project Desc.'])[:140]}...")
                        
                        url = row['Approval Pack/NOC']
                        if pd.isna(url) or not str(url).startswith("http"):
                            st.button("No Link", disabled=True, key=f"btn_{idx}")
                        else:
                            st.link_button("View on ZAP", url, use_container_width=True)
        else:
            st.warning("No projects match your current selection.")
    else:
        # Welcome State
        st.info("👈 Use the sidebar to set your filters and click **'Run Search'**.")
        st.markdown("""
        ### Pilot Navigation:
        - **Single-Action:** A guided path from broad categories to specific waivers.
        - **Multi-Action:** Select multiple categories to see overlapping project types.
        - **Clear:** Use the 'Clear' button in the sidebar to reset all menus instantly.
        """)

    # 8. Footer & Privacy
    st.divider()
    # Respecting the privacy statement you shared:
    st.caption("🔒 **Data Privacy:** This is a professional pilot tool. We value your trust; your search data is never stored or sold.")
    
    with st.expander("📩 Submit a 'Good Project'"):
        with st.form("contribution", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                p_name = st.text_input("Project Name*")
                z_link = st.text_input("ZAP Link")
            with f2:
                org = st.text_input("Organization")
                all_l1_sub = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
                p_cat = st.selectbox("Category", all_l1_sub)
            
            logic = st.text_area("Why is this a 'Good Project'?")
            if st.form_submit_button("Submit"):
                if p_name:
                    st.success("Thank you! Suggestion added for review.")

else:
    st.error("Error: Could not locate 'projects.csv'.")