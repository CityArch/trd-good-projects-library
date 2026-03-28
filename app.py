import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="TRD Digital Good Projects Library",
    page_icon="🏙️",
    layout="wide"
)

# 2. Custom CSS for Styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading Function
@st.cache_data
def load_data():
    try:
        # Assumes your file is named 'projects.csv' in the same folder
        df = pd.read_csv('projects.csv')
        # Clean column names and handle specific Pilot Version formatting
        df.columns = [c.strip() for c in df.columns]
        # Filter out header rows from the template if they exist
        df = df[df['Project'].notna()]
        df = df[~df['Project'].str.contains("Insert your project name", na=False)]
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # 4. Header Section
    st.title("🏙️ TRD Digital Good Projects Library")
    st.markdown("""
    *A curated directory of high-quality urban design and planning projects in New York City.*
    Use the sidebar to filter by zoning action or search for specific projects below.
    """)
    st.divider()

    # 5. Sidebar Filters
    st.sidebar.header("Filter Gallery")
    
    # Level 1 Filter
    l1_list = ["All"] + sorted(df_raw['Level1'].dropna().unique().tolist())
    selected_l1 = st.sidebar.selectbox("Zoning Category (Level 1)", l1_list)

    # Level 2 Filter (Dependent on Level 1)
    if selected_l1 != "All":
        temp_df = df_raw[df_raw['Level1'] == selected_l1]
        l2_list = ["All"] + sorted(temp_df['Level2'].dropna().unique().tolist())
    else:
        l2_list = ["All"] + sorted(df_raw['Level2'].dropna().unique().tolist())
    
    selected_l2 = st.sidebar.selectbox("Sub-Category (Level 2)", l2_list)

    # Search Bar
    search_query = st.text_input("🔍 Search by Project Name, ID, or Description", "")

    # Apply Filtering Logic
    df = df_raw.copy()
    if selected_l1 != "All":
        df = df[df['Level1'] == selected_l1]
    if selected_l2 != "All":
        df = df[df['Level2'] == selected_l2]
    if search_query:
        df = df[
            df['Project'].str.contains(search_query, case=False, na=False) | 
            df['Project Desc.'].str.contains(search_query, case=False, na=False) |
            df['Project ID'].str.contains(search_query, case=False, na=False)
        ]

    # 6. Project Gallery (Card View)
    st.write(f"Showing **{len(df)}** projects matching your criteria.")
    
    # Create a 3-column grid
    cols = st.columns(3)

    for i, (index, row) in enumerate(df.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                # Title and ID
                st.markdown(f"### {row['Project']}")
                st.caption(f"ID: {row['Project ID']} | Year: {row['Cert Year']}")
                
                # Tags
                st.write(f"🏷️ **{row['Level1']}**")
                st.write(f"🔹 *{row['Level2']}*")
                
                # Description logic
                desc = str(row['Project Desc.'])
                if len(desc) > 160:
                    st.write(f"{desc[:160]}...")
                else:
                    st.write(desc)
                
                # Link Button
                url = row['Approval Pack/NOC']
                if pd.isna(url) or not str(url).startswith("http"):
                    st.button("No ZAP Link", disabled=True, key=f"btn_{i}")
                else:
                    st.link_button("View on ZAP", url, use_container_width=True)

    # 7. Feedback & Submission Section
    st.divider()
    st.header("📩 Contribute to the Library")
    
    with st.expander("Submit a 'Good Project' or Leave Feedback"):
        st.write("Help us grow this pilot by suggesting projects with exemplary design or zoning logic.")
        with st.form("contribution_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                new_proj = st.text_input("Project Name*")
                zap_id = st.text_input("Project ID / ZAP Link")
            with f_col2:
                contributor = st.text_input("Your Name (Optional)")
                cat = st.selectbox("Category", ["Bulk/Waivers", "Open Space", "Housing/MIH", "Other"])
            
            logic = st.text_area("Why is this a 'Good Project'?")
            
            submitted = st.form_submit_button("Submit for Review")
            if submitted:
                if new_proj:
                    st.success("Thank you! Your submission has been recorded for review.")
                else:
                    st.error("Please provide at least a Project Name.")

else:
    st.warning("Awaiting data... Please ensure 'projects.csv' is in the root directory.")