import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="TRD Digital Good Projects Library",
    page_icon="🏙️",
    layout="wide"
)

# 2. Data Loading Function (Handles Excel/CSV Encoding issues)
@st.cache_data
def load_data():
    file_path = 'projects.csv'
    try:
        # Try UTF-8 first, fallback to CP1252 for Excel-saved CSVs
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1252')
        
        # Clean column names and data
        df.columns = [c.strip() for c in df.columns]
        df = df[df['Project'].notna()]
        # Filter out the template instruction row if it exists
        df = df[~df['Project'].str.contains("Insert your project name", na=False)]
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # 3. Sidebar - Filter Gallery
    st.sidebar.header("Filter Gallery")
    
    # Toggle between Single and Multi Search
    search_mode = st.sidebar.radio(
        "Search Mode",
        ["Single-Action Search", "Multi-Action Search"],
        help="Single-Action allows deep drilling; Multi-Action allows selecting multiple tags."
    )

    filtered_df = df_raw.copy()

    if search_mode == "Single-Action Search":
        # --- LEVEL 1 ---
        l1_options = ["All"] + sorted(filtered_df['Level1'].dropna().unique().tolist())
        selected_l1 = st.sidebar.selectbox("Zoning Category (Level 1)", l1_options)

        if selected_l1 != "All":
            filtered_df = filtered_df[filtered_df['Level1'] == selected_l1]
            
            # --- LEVEL 2 ---
            l2_options = ["All"] + sorted(filtered_df['Level2'].dropna().unique().tolist())
            selected_l2 = st.sidebar.selectbox("Sub-Category (Level 2)", l2_options)
            
            if selected_l2 != "All":
                filtered_df = filtered_df[filtered_df['Level2'] == selected_l2]
                
                # --- LEVEL 3 (Specific for Height_Setbacks) ---
                if selected_l2 == "Height_Setbacks":
                    l3_list = [
                        "All", 
                        "Sky Exposure Plane", 
                        "Midtown Daylight Rules", 
                        "Height Limit Waivers", 
                        "Setback Waivers"
                    ]
                    selected_l3 = st.sidebar.selectbox("Specific Waiver (Level 3)", l3_list)
                    
                    if selected_l3 != "All":
                        # Check across all 4 potential Level 3 columns in your database
                        filtered_df = filtered_df[
                            (filtered_df['Level3-1'] == selected_l3) | 
                            (filtered_df['Level3-2'] == selected_l3) | 
                            (filtered_df['Level3-3'] == selected_l3) | 
                            (filtered_df['Level3-4'] == selected_l3)
                        ]

    else:
        # --- MULTI-ACTION SEARCH ---
        all_l1 = sorted(filtered_df['Level1'].dropna().unique().tolist())
        selected_l1_multi = st.sidebar.multiselect("Select Categories (Level 1)", all_l1)
        if selected_l1_multi:
            filtered_df = filtered_df[filtered_df['Level1'].isin(selected_l1_multi)]
            
            all_l2 = sorted(filtered_df['Level2'].dropna().unique().tolist())
            selected_l2_multi = st.sidebar.multiselect("Filter by Sub-Categories (Level 2)", all_l2)
            if selected_l2_multi:
                filtered_df = filtered_df[filtered_df['Level2'].isin(selected_l2_multi)]

    # 4. Main UI Content
    st.title("🏙️ TRD Digital Good Projects Library")
    
    # Text Search
    search_query = st.text_input("🔍 Search by Project Name, ID, or Description", "")
    if search_query:
        filtered_df = filtered_df[
            filtered_df['Project'].str.contains(search_query, case=False, na=False) | 
            filtered_df['Project Desc.'].str.contains(search_query, case=False, na=False) |
            filtered_df['Project ID'].astype(str).str.contains(search_query, case=False, na=False)
        ]

    st.write(f"Showing **{len(filtered_df)}** projects matching your criteria.")
    st.divider()

    # 5. Project Gallery (3-column grid)
    cols = st.columns(3)
    for i, (index, row) in enumerate(filtered_df.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {row['Project']}")
                st.caption(f"ID: {row['Project ID']} | Year: {row['Cert Year']}")
                
                # Breadcrumb style tags
                st.markdown(f"**{row['Level1']}** > *{row['Level2']}*")
                
                # Display any Level 3 specifics if available
                l3_vals = [row['Level3-1'], row['Level3-2'], row['Level3-3'], row['Level3-4']]
                l3_display = [str(v) for v in l3_vals if pd.notna(v)]
                if l3_display:
                    st.caption(f"Focus: {', '.join(l3_display)}")

                # Description summary
                desc = str(row['Project Desc.'])
                st.write(f"{desc[:160]}..." if len(desc) > 160 else desc)
                
                # Action Link
                url = row['Approval Pack/NOC']
                if pd.isna(url) or not str(url).startswith("http"):
                    st.button("No ZAP Link", disabled=True, key=f"btn_{i}")
                else:
                    st.link_button("View on ZAP", url, use_container_width=True)

    # 6. Feedback/Submission Section
    st.divider()
    with st.expander("📩 Submit a 'Good Project' or Leave Feedback"):
        with st.form("contribution_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                new_proj = st.text_input("Project Name*")
                zap_link = st.text_input("ZAP Link / Project ID")
            with f_col2:
                contributor = st.text_input("Your Name (Optional)")
                cat_type = st.selectbox("Category", ["Bulk_Waivers", "Use_Waivers", "Open_Space", "Other"])
            
            logic_text = st.text_area("Why is this a 'Good Project'?")
            
            if st.form_submit_button("Submit for Review"):
                if new_proj:
                    st.success("Thank you! Your suggestion has been sent for review.")
                else:
                    st.error("Please provide a project name.")

else:
    st.info("Please ensure your 'projects.csv' is in the root directory and the column names match.")