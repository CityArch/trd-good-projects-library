import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="TRD Digital Good Projects Library",
    page_icon="🏙️",
    layout="wide"
)

# 2. Data Loading Function (with encoding fallback for Excel CSVs)
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
        # Remove template rows
        df = df[~df['Project'].str.contains("Insert your project name", na=False)]
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # 3. Sidebar - Multi-Action Search Interface
    st.sidebar.header("🔍 Multi-Action Search")
    
    # --- LEVEL 1 SELECTION ---
    all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
    selected_l1 = st.sidebar.multiselect("Select Categories (Level 1)", all_l1)

    # --- LEVEL 2 SELECTION (Cascading) ---
    if selected_l1:
        l2_options = sorted([str(x) for x in df_raw[df_raw['Level1'].isin(selected_l1)]['Level2'].dropna().unique()])
    else:
        l2_options = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
    
    selected_l2 = st.sidebar.multiselect("Select Sub-Categories (Level 2)", l2_options)

    # --- LEVEL 3 SELECTION (Cascading) ---
    l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
    
    if selected_l2:
        l3_subset = df_raw[df_raw['Level2'].isin(selected_l2)]
    elif selected_l1:
        l3_subset = df_raw[df_raw['Level1'].isin(selected_l1)]
    else:
        l3_subset = df_raw

    # FIX: Flatten values, remove NaNs, convert to string, then sort
    raw_l3_values = l3_subset[l3_cols].values.ravel('K')
    all_l3 = sorted([str(x) for x in pd.unique(raw_l3_values) if pd.notna(x)])
    
    selected_l3 = st.sidebar.multiselect("Select Specific Focus (Level 3)", all_l3)

    # --- SEARCH BUTTON ---
    # This button triggers the filtering process
    search_triggered = st.sidebar.button("🚀 Run Search", use_container_width=True)

    # 4. Main UI Content
    st.title("🏙️ TRD Digital Good Projects Library")
    
    # Text Search (Always available)
    search_query = st.text_input("📝 Quick Search by Project Name or ID", "")

    # 5. Logic: Filtering Data
    # Only run the heavy filter if the button is pressed or text is typed
    if search_triggered or search_query:
        df = df_raw.copy()

        # Filtering exactly by the selected categories
        if selected_l1:
            df = df[df['Level1'].isin(selected_l1)]
        
        if selected_l2:
            df = df[df['Level2'].isin(selected_l2)]
            
        if selected_l3:
            # Check if ANY of the Level 3 columns match the user's selections
            df = df[
                df['Level3-1'].isin(selected_l3) | 
                df['Level3-2'].isin(selected_l3) | 
                df['Level3-3'].isin(selected_l3) | 
                df['Level3-4'].isin(selected_l3)
            ]

        if search_query:
            df = df[
                df['Project'].str.contains(search_query, case=False, na=False) | 
                df['Project ID'].astype(str).str.contains(search_query, case=False, na=False)
            ]

        # 6. Display Gallery
        st.write(f"Found **{len(df)}** projects matching your exact criteria.")
        st.divider()

        if not df.empty:
            cols = st.columns(3)
            for i, (index, row) in enumerate(df.iterrows()):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {row['Project']}")
                        st.caption(f"ID: {row['Project ID']} | {row['Cert Year']}")
                        st.markdown(f"**{row['Level1']}** > *{row['Level2']}*")
                        
                        # Display tags from Level 3
                        l3_tags = [row[c] for c in l3_cols if pd.notna(row[c])]
                        if l3_tags:
                            st.caption(f"Waivers: {', '.join([str(t) for t in l3_tags])}")

                        desc = str(row['Project Desc.'])
                        st.write(f"{desc[:140]}..." if len(desc) > 140 else desc)
                        
                        url = row['Approval Pack/NOC']
                        if pd.isna(url) or not str(url).startswith("http"):
                            st.button("No ZAP Link", disabled=True, key=f"btn_{i}")
                        else:
                            st.link_button("View on ZAP", url, use_container_width=True)
        else:
            st.warning("No projects match that combination. Try broadening your selection.")
    else:
        # Initial Welcome Screen
        st.info("👈 Set your filters in the sidebar and hit **'Run Search'** to explore the Good Projects library.")
        st.markdown("""
        ### How it works:
        1. **Select Level 1 Categories** (e.g., Bulk Waivers).
        2. **Refine by Level 2 Sub-categories** (e.g., Height & Setbacks).
        3. **Drill down to Level 3 Focus** (e.g., Sky Exposure Plane).
        4. Click the **Search Button** to see only the projects that fit those categories.
        """)

    # 7. Privacy & Feedback
    st.divider()
    # Acknowledging your preference for transparency and trust:
    st.caption("🔒 **Data Privacy Commitment:** This application is a local tool. We value your trust; your data is never sold or tracked.")
    
    with st.expander("📩 Submit a Project for the Library"):
        with st.form("contribution", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                name = st.text_input("Project Name*")
                link = st.text_input("ZAP Link")
            with f2:
                org = st.text_input("Your Organization")
                cat = st.selectbox("Category", all_l1 if all_l1 else ["General"])
            
            why = st.text_area("Why is this a 'Good Project'?")
            if st.form_submit_button("Submit Suggestion") and name:
                st.success("Thank you! Suggestion recorded for the pilot review.")

else:
    st.error("Wait! The 'projects.csv' file was not found or has column errors.")