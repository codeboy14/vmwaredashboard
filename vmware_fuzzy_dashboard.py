import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from functools import lru_cache

# Load the CSV file with caching
@st.cache_data
def load_data():
    # Ensure this file is in the same directory and has a 'Complexity' column
    return pd.read_csv("vmware_kb_articles_1.csv")

df = load_data()

# Extract product keywords from the 'keywords' column
@st.cache_data
def extract_products(keywords_series):
    products = set()
    for keywords in keywords_series.dropna():
        for keyword in keywords.split(','):
            products.add(keyword.strip().split()[0])
    return sorted(products)

product_list = extract_products(df['keywords'])

# Streamlit UI
st.title("HPE Tool: VMware KB Article Finder with Fuzzy Matching")
st.write("Enter an error message or keyword to find relevant VMware KB articles.")

error_message = st.text_input("Error Message or Keyword")
selected_product = st.selectbox("Filter by Product (optional)", ["All"] + product_list)

# Cached fuzzy matching function
@lru_cache(maxsize=2048)
def fuzzy_score(a, b):
    return fuzz.partial_ratio(a, b)

if error_message:
    # Filter by product if selected
    if selected_product != "All":
        filtered_df = df[df['keywords'].str.contains(selected_product, case=False, na=False)]
    else:
        filtered_df = df

    # Apply fuzzy matching using vectorized approach
    error_lower = error_message.lower()
    scores = filtered_df['keywords'].fillna("").str.lower().apply(lambda x: fuzzy_score(error_lower, x))
    results = filtered_df[scores > 70]

    if not results.empty:
        st.write("Matching KB Articles:")
        for _, row in results.iterrows():
            st.markdown(f"**Article ID:** {row['article_id']}")
            st.markdown(f"**Resolution:** {row['title']}")
            
            # Display URL if it exists
            if pd.notna(row['url']) and row['url'].strip():
                st.markdown(f"[View Article]({row['url']})")
            else:
                st.markdown("_No URL available for this article._")

            # --- NEW: Check the 'Complexity' column and print action ---
            if 'Complexity' in row and pd.notna(row['Complexity']):
                complexity_status = str(row['Complexity']).strip().lower()
                if complexity_status == 'yes':
                    st.warning("⚠️ **Action:** Engage POD and mentor, complex case.")
                elif complexity_status == 'no':
                    st.info("ℹ️ **Action:** Continue troubleshooting and contact mentor for technical updates.")
            else:
                st.write("_Complexity status not specified._")
            # --- END of new section ---
                
            st.markdown("---")
    else:
        st.write("No matching KB articles found.")

# Footer with footnote
st.markdown("""
---
<sub>Developed and managed by RTCC AMS. For feedback and changes, please email [tushar.thapa@hpe.com], referring to the Real-Time Command Center under AMS (North America), which is responsible for compute and communication support.</sub>
""", unsafe_allow_html=True)
