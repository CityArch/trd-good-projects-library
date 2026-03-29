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
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1252')
        
        # Clean column names to prevent KeyErrors
        df.columns = [str(c).strip() for c in df.columns]
        
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
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("3. Specific Focus (L3)", l3_opts, key=f"s3_{st.session_state.reset_key}")
                    if c3 != "All":
                        final_l3 = [c3]
    else:
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        final_l1 = st.sidebar.multiselect("Categories (L1)", all_l1, key=f"m1_{st.session_state.reset_key}")
        
        all_l2 = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        final_l2 = st.sidebar.multiselect("Sub-Categories (L2)", all_l2, key=f"m2_{st.session_state.reset_key}")
        
        l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        raw_l3_m = df_raw[l3_cols].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3_m) if pd.notna(x)])
        final_l3 = st.sidebar.multiselect("Specific Waivers (L3)", all_l3, key=f"m3_{st.session_state.reset_key}")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Run Search", use_container_width=True, type="primary"):
        st.session_state.search_active = True
    
    if st.sidebar.button("🧹 Clear for a new search", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.search_active = False
        st.rerun()

    # 5. Main Content Area
    st.title("🏙️ TRD Digital Good Projects Library")
    q_search = st.text_input("📝 Quick Search (Name or ID)", key=f"q_{st.session_state.reset_key}")

    if st.session_state.search_active or q_search:
        df = df_raw.copy()
        
        if search_mode == "Single-Action Search":
            if final_l1: df = df[df['Level1'].isin(final_l1)]
            if final_l2: df = df[df['Level2'].isin(final_l2)]
            if final_l3:
                df = df[df['Level3-1'].isin(final_l3) | df['Level3-2'].isin(final_l3) | 
                        df['Level3-3'].isin(final_l3) | df['Level3-4'].isin(final_l3)]
        else:
            if final_l1 or final_l2 or final_l3:
                def check_project_match(group):
                    proj_l1 = set(group['Level1'].dropna())
                    proj_l2 = set(group['Level2'].dropna())
                    proj_l3 = set(group[['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']].values.flatten())
                    proj_l3 = {str(x) for x in proj_l3 if pd.notna(x)}
                    m1 = all(i in proj_l1 for i in final_l1)
                    m2 = all(i in proj_l2 for i in final_l2)
                    m3 = all(i in proj_l3 for i in final_l3)
                    return m1 and m2 and m3
                m_ids = df_raw.groupby('Project ID').filter(check_project_match)['Project ID'].unique()
                df = df_raw[df_raw['Project ID'].isin(m_ids)]

        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | 
                    df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

        st.subheader(f"Results: {len(df)} Entries")
        st.divider()

        if not df.empty:
            grid = st.columns(3)
            # --- FIXED INDENTATION BLOCK ---
            for idx, (i, row) in enumerate(df.iterrows()):
                with grid[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {row['Project']}")
                        st.caption(f"ID: {row['Project ID']} | {row['Cert Year']}")
                        st.write(f"**{row['Level1']}** > {row['Level2']}")
                        zap_url = str(row['Approval Pack/NOC'])
                        if zap_url.startswith("http"):
                            st.link_button("View on ZAP", zap_url, use_container_width=True)
                        else:
                            st.button("No ZAP Link", disabled=True, use_container_width=True)
        else:
            st.warning("No projects match that exact combination.")
    else:
        st.info("👈 Use the sidebar to explore the library.")

    # 6. ADMIN REVIEW
    st.divider()
    st.header("⏳ Recently Submitted Projects")
    official_ids = set(df_raw['Project ID'].astype(str).unique())
    st.session_state.submitted_projects = [p for p in st.session_state.submitted_projects if str(p['id']) not in official_ids]

    if not st.session_state.submitted_projects:
        st.write("No new submissions pending review.")
    else:
        for p in st.session_state.submitted_projects:
            with st.expander(f"Review: {p['name']} (ID: {p['id']})"):
                st.write(f"**Description:** {p['desc']}")
                st.write(f"**Categories:** {', '.join(p['cats'])}")
                st.write(f"**Link:** {p['link']} | **Date:** {p['date']}")

    # 7. SUBMISSION FORM
    st.divider()
    st.header("📩 Submit a 'Good Project'")
    with st.expander("Open Submission Form"):
        st.subheader("1. Categorize Project")
        ca, cb, cc = st.columns(3)
        with ca: 
            s1 = st.selectbox("Category (L1)", sorted(df_raw['Level1'].dropna().unique()), key="sub_l1")
        with cb: 
            s2_opts = sorted(df_raw[df_raw['Level1'] == s1]['Level2'].dropna().unique())
            s2_sel = st.selectbox("Sub-Category (L2)", s2_opts, key="sub_l2")
        with cc:
            raw_l3_sub = df_raw[df_raw['Level2'] == s2_sel][['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K')
            s3_list = sorted([str(x) for x in pd.unique(raw_l3_sub) if pd.notna(x)])
            s3_sel = st.multiselect("Focus (L3)", s3_list, key="sub_l3")

        if st.button("➕ Complete Selections"):
            cat_label = f"{s1} > {s2_sel}" + (f" ({', '.join(s3_sel)})" if s3_sel else "")
            if cat_label not in st.session_state.temp_cats:
                st.session_state.temp_cats.append(cat_label)
                st.toast(f"Added Category!")

        if st.session_state.temp_cats:
            st.write("**Selections:**")
            for cat in st.session_state.temp_cats:
                st.write(f"- {cat}")
            if st.button("🗑️ Reset Categories"):
                st.session_state.temp_cats = []
                st.rerun()

        st.markdown("---")
        st.subheader("2. Project Details")
        with st.form("final_sub", clear_on_submit=True):
            f_name = st.text_input("Project Name*")
            f_id = st.text_input("Project ID*")
            f_desc = st.text_area("Description")
            f_link = st.text_input("ZAP Link")
            f_date = st.date_input("Certification Date", date.today())
            
            if st.form_submit_button("Submit Project"):
                if f_name and f_id:
                    st.session_state.submitted_projects.append({
                        "name": f_name, "id": f_id, "desc": f_desc,
                        "link": f_link, "date": str(f_date),
                        "cats": st.session_state.temp_cats.copy()
                    })
                    st.session_state.temp_cats = []
                    st.success("Project submitted!")
                    st.rerun()
                else:
                    st.error("Name and ID are required.")

    st.divider()
    st.caption("🔒 **Data Privacy:** Professional pilot tool. Restricted access.")

else:
    st.stop()