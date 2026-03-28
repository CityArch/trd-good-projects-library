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

if not df_raw.empty:
    # 3. Sidebar - Search Interface
    st.sidebar.header("🔍 Project Directory")
    
    # Selection Mode
    search_mode = st.sidebar.radio(
        "Select Search Method",
        ["Single-Action Search", "Multi-Action Search"],
        index=0,
        help="Single-Action drills down one path; Multi-Action allows multiple category tags."
    )

    # Initialize variables for filtering
    sel_l1, sel_l2, sel_l3 = [], [], []

    if search_mode == "Single-Action Search":
        st.sidebar.markdown("---")
        # Step 1: Level 1
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        choice_l1 = st.sidebar.selectbox("1. Select Category (Level 1)", l1_opts)
        
        if choice_l1 != "All":
            sel_l1 = [choice_l1]
            # Step 2: Level 2
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == choice_l1]['Level2'].dropna().unique()])
            choice_l2 = st.sidebar.selectbox("2. Select Sub-Category (Level 2)", l2_opts)
            
            if choice_l2 != "All":
                sel_l2 = [choice_l2]
                # Step 3: Level 3
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                l3_subset = df_raw[df_raw['Level2'] == choice_l2]
                raw_l3 = l3_subset[l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1: # Only show if there are Level 3 options
                    choice_l3 = st.sidebar.selectbox("3. Select Specific Focus (Level 3)", l3_opts)
                    if choice_l3 != "All":
                        sel_l3 = [choice_l3]

    else:
        # Multi-Action Search
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        sel_l1 = st.sidebar.multiselect("Select Categories (Level 1)", all_l1)

        if sel_l1:
            l2_opts = sorted([str(x) for x in df_raw[df_raw['Level1'].isin(sel_l1)]['Level2'].dropna().unique()])
        else:
            l2_opts = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        sel_l2 = st.sidebar.multiselect("Select Sub-Categories (Level 2)", l2_options)

        l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        if sel_l2:
            l3_subset = df_raw[df_raw['Level2'].isin(sel_l2)]
        else:
            l3_subset = df_raw
        
        raw_l3 = l3_subset[l3_cols].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
        sel_l3 = st.sidebar.multiselect("Select Specific Focus (Level 3)", all_l3)

    # 4. Global Run Search Button
    st.sidebar.markdown("---")
    run_search = st.sidebar.button("🚀 Run Search", use_container_width=True, type="primary")

    # 5. Main Content Area
    st.title("🏙️ TRD Digital Good Projects Library")
    
    # Quick Text Search (Always live)
    quick_search = st.text_input("📝 Search by Project Name or ID...", "")

    # 6. Filtering Logic
    if run_search or quick_search:
        df = df_raw.copy()

        if sel_l1:
            df = df[df['Level1'].isin(sel_l1)]
        if sel_l2:
            df = df[df['Level2'].isin(sel_l2)]
        if sel_l3:
            df = df[
                df['Level3-1'].isin(sel_l3) | 
                df['Level3-2'].isin(sel_l3) | 
                df['Level3-3'].isin(sel_l3) | 
                df['Level3-4'].isin(sel_l3)
            ]
        
        if quick_search:
            df = df[
                df['Project'].str.contains(quick_search, case=False, na=False) | 
                df['Project ID'].astype(str).str.contains(quick_search, case=False, na=False)
            ]

        # 7. Display Results
        st.subheader(f"Results: {len(df)} Projects Found")
        st.divider()

        if not df.empty:
            cols = st.columns(3)
            for i, (index, row) in enumerate(df.iterrows()):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {row['Project']}")
                        st.caption(f"ID: {row['Project ID']} | {row['Cert Year']}")
                        st.markdown(f"**{row['Level1']}** > *{row['Level2']}*")
                        
                        # Waiver Tags
                        tags = [row[c] for c in ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'] if pd.notna(row[c])]
                        if tags:
                            st.caption(f"Details: {', '.join([str(t) for t in tags])}")

                        desc = str(row['Project Desc.'])
                        st.write(f"{desc[:140]}..." if len(desc) > 140 else desc)
                        
                        url = row['Approval Pack/NOC']
                        if pd.isna(url) or not str(url).startswith("http"):
                            st.button("No ZAP Link", disabled=True, key=f"btn_{i}")
                        else:
                            st.link_button("View on ZAP", url, use_container_width=True)
        else:
            st.warning("No projects match your specific selection. Please try a different category.")
    else:
        # Default Welcome Screen
        st.info("👈 Use the filters in the sidebar and click **'Run Search'** to start exploring the directory.")
        st.markdown("""
        ### Pilot Directory Features:
        * **Single-Action:** Drill down logically from broad categories to specific waivers.
        * **Multi-Action:** Select multiple tags to compare projects across different zoning types.
        * **Direct Links:** Access NYC Planning (ZAP) documentation directly from each card.
        """)

    # 8. Footer & Privacy
    st.divider()
    st.caption("🔒 **Data Privacy Commitment:** As discussed, we value the trust of our users. This application does not track individual searches or sell data.")
    
    with st.expander("📩 Submit a 'Good Project' for Review"):
        with st.form("sub_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                p_name = st.text_input("Project Name*")
                z_link = st.text_input("ZAP Link")
            with f2:
                org = st.text_input("Organization")
                p_cat = st.selectbox("Category", sorted([str(x) for x in df_raw['Level1'].dropna().unique()]))
            
            logic = st.text_area("Why is this a 'Good Project'?")
            if st.form_submit_button("Submit"):
                if p_name:
                    st.success("Thank you! Your contribution has been submitted for the pilot database.")

else:
    st.error("Critical Error: 'projects.csv' not found. Please upload your database to the root folder.")