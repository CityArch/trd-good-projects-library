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

# Initialize session state variables for search and text input
if "search_active" not in st.session_state:
    st.session_state.search_active = False
if "query_text" not in st.session_state:
    st.session_state.query_text = ""

if not df_raw.empty:
    # 3. Sidebar - Filter Navigation
    st.sidebar.header("🔍 Project Search")
    
    search_mode = st.sidebar.radio(
        "Search Mode",
        ["Single-Action Search", "Multi-Action Search"],
        key="mode_toggle"
    )

    final_l1, final_l2, final_l3 = [], [], []

    if search_mode == "Single-Action Search":
        st.sidebar.markdown("---")
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        c1 = st.sidebar.selectbox("1. Category (Level 1)", l1_opts)
        
        if c1 != "All":
            final_l1 = [c1]
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
            c2 = st.sidebar.selectbox("2. Sub-Category (Level 2)", l2_opts)
            
            if c2 != "All":
                final_l2 = [c2]
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                l3_subset = df_raw[df_raw['Level2'] == c2]
                raw_l3 = l3_subset[l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("3. Specific Focus (Level 3)", l3_opts)
                    if c3 != "All":
                        final_l3 = [c3]
    else:
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        final_l1 = st.sidebar.multiselect("Select Categories (Level 1)", all_l1)
        
        l2_opts = sorted([str(x) for x in df_raw[df_raw['Level1'].isin(final_l1)]['Level2'].dropna().unique()]) if final_l1 else sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        final_l2 = st.sidebar.multiselect("Select Sub-Categories (Level 2)", l2_opts)

        l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        l3_subset = df_raw[df_raw['Level2'].isin(final_l2)] if final_l2 else df_raw
        raw_l3 = l3_subset[l3_cols].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
        final_l3 = st.sidebar.multiselect("Select Specific Focus (Level 3)", all_l3)

    # 4. Control Buttons
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Run Search", use_container_width=True, type="primary"):
        st.session_state.search_active = True
    
    if st.sidebar.button("🧹 Clear for a new search", use_container_width=True):
        st.session_state.search_active = False
        st.session_state.query_text = ""  # Clear the saved search bar text
        st.rerun()

    # 5. Main Content
    st.title("🏙️ TRD Digital Good Projects Library")
    
    # Text input linked to session state so it can be cleared programmatically
    q_search = st.text_input(
        "📝 Quick Search (Name or ID)", 
        value=st.session_state.query_text, 
        key="query_input"
    )
    # Update state whenever user types
    st.session_state.query_text = q_search

    # 6. Search Execution
    if st.session_state.search_active or st.session_state.query_text:
        df = df_raw.copy()

        if final_l1:
            df = df[df['Level1'].isin(final_l1)]
        if final_l2:
            df = df[df['Level2'].isin(final_l2)]
        if final_l3:
            df = df[df['Level3-1'].isin(final_l3) | df['Level3-2'].isin(final_l3) | df['Level3-3'].isin(final_l3) | df['Level3-4'].isin(final_l3)]
        
        if st.session_state.query_text:
            df = df[df['Project'].str.contains(st.session_state.query_text, case=False, na=False) | 
                    df['Project ID'].astype(str).str.contains(st.session_state.query_text, case=False, na=False)]

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
            st.warning("No projects match your selection.")
    else:
        st.info("👈 Use the sidebar to set your filters and click **'Run Search'**.")

    # 7. Privacy & Submission
    st.divider()
    st.caption("🔒 **Data Privacy:** Professional pilot tool. Search data is not stored or sold.")
    with st.expander("📩 Submit a 'Good Project'"):
        with st.form("contribution", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                p_name = st.text_input("Project Name*")
                z_link = st.text_input("ZAP Link")
            with f2:
                org = st.text_input("Organization")
                p_cat = st.selectbox("Category", sorted([str(x) for x in df_raw['Level1'].dropna().unique()]))
            if st.form_submit_button("Submit") and p_name:
                st.success("Thank you! Suggestion added.")
else:
    st.error("Error: Could not locate 'projects.csv'.")