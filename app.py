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
    # 3. Sidebar - Multi-Action Search Interface
    st.sidebar.header("🔍 Multi-Action Search")
    st.sidebar.info("Select multiple categories across levels to find specific projects.")

    # --- LEVEL 1 SELECTION ---
    all_l1 = sorted(df_raw['Level1'].dropna().unique().tolist())
    selected_l1 = st.sidebar.multiselect("Select Categories (Level 1)", all_l1)

    # --- LEVEL 2 SELECTION (Cascading) ---
    if selected_l1:
        l2_options = sorted(df_raw[df_raw['Level1'].isin(selected_l1)]['Level2'].dropna().unique().tolist())
    else:
        l2_options = sorted(df_raw['Level2'].dropna().unique().tolist())
    
    selected_l2 = st.sidebar.multiselect("Select Sub-Categories (Level 2)", l2_options)

    # --- LEVEL 3 SELECTION (Cascading) ---
    # We look across all Level3 columns (1 through 4) for options
    l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
    
    if selected_l2:
        l3_subset = df_raw[df_raw['Level2'].isin(selected_l2)]
    elif selected_l1:
        l3_subset = df_raw[df_raw['Level1'].isin(selected_l1)]
    else:
        l3_subset = df_raw

    # Flatten unique values from all Level 3 columns
    all_l3 = sorted(pd.unique(l3_subset[l3_cols].values.ravel('K')))
    all_l3 = [x for x in all_l3 if pd.notna(x) and str(x).strip() != ""]
    
    selected_l3 = st.sidebar.multiselect("Select Specific Focus (Level 3)", all_l3)

    # --- SEARCH BUTTON ---
    search_triggered = st.sidebar.button("🚀 Run Search", use_container_width=True)

    # 4. Main UI Content
    st.title("🏙️ TRD Digital Good Projects Library")
    
    # Text Search (Always available)
    search_query = st.text_input("📝 Quick Search (Project Name or ID)", "")

    # 5. Logic: Filtering Data
    if search_triggered or search_query:
        df = df_raw.copy()

        # Apply Level 1 Filter
        if selected_l1:
            df = df[df['Level1'].isin(selected_l1)]
        
        # Apply Level 2 Filter
        if selected_l2:
            df = df[df['Level2'].isin(selected_l2)]
            
        # Apply Level 3 Filter (Check if selection exists in ANY of the 4 columns)
        if selected_l3:
            df = df[
                df['Level3-1'].isin(selected_l3) | 
                df['Level3-2'].isin(selected_l3) | 
                df['Level3-3'].isin(selected_l3) | 
                df['Level3-4'].isin(selected_l3)
            ]

        # Apply Text Search
        if search_query:
            df = df[
                df['Project'].str.contains(search_query, case=False, na=False) | 
                df['Project ID'].astype(str).str.contains(search_query, case=False, na=False)
            ]

        # 6. Display Gallery
        st.write(f"Found **{len(df)}** projects matching your criteria.")
        st.divider()

        if not df.empty:
            cols = st.columns(3)
            for i, (index, row) in enumerate(df.iterrows()):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {row['Project']}")
                        st.caption(f"ID: {row['Project ID']} | {row['Cert Year']}")
                        st.markdown(f"**{row['Level1']}** > *{row['Level2']}*")
                        
                        # Gather tags
                        tags = [row[c] for c in l3_cols if pd.notna(row[c])]
                        if tags:
                            st.caption(f"Waivers: {', '.join(tags)}")

                        desc = str(row['Project Desc.'])
                        st.write(f"{desc[:140]}..." if len(desc) > 140 else desc)
                        
                        url = row['Approval Pack/NOC']
                        if pd.isna(url) or not str(url).startswith("http"):
                            st.button("No ZAP Link", disabled=True, key=f"btn_{i}")
                        else:
                            st.link_button("View on ZAP", url, use_container_width=True)
        else:
            st.warning("No projects match that exact combination. Try broadening your selection.")
    else:
        # Default view before search is pressed
        st.info("👈 Use the Multi-Action Search in the sidebar and hit 'Run Search' to explore the library.")
        st.image("https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&q=80&w=1000", caption="NYC Planning & Design")

    # 7. Privacy & Feedback
    st.divider()
    st.caption("🔒 **Data Privacy Note:** This pilot is built on trust. We do not track personal data or sell user information.")
    
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
                st.success("Thank you! Suggestion recorded.")

else:
    st.error("Data source error. Please check your 'projects.csv' file.")