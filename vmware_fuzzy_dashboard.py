import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from functools import lru_cache

# Logo URL
logo_url = "https://raw.githubusercontent.com/codeboy14/vmwaredashboard/blob/759c5b7274122e51f3245b84ea629ba6fe3ebf72/logoHPE.png"
st.image(logo_url, width=180)

# Load the CSV file with caching
@st.cache_data
def load_data():
    df = pd.read_csv("vmware_kb_articles_1.csv")
    df.columns = df.columns.str.strip()  # Fix: remove whitespace from column names
    return df

df = load_data()

# Extract product names from the 'product' column
@st.cache_data
def extract_products(product_series):
    products = set()
    for product_list in product_series.dropna():
        for product in product_list.split(','):
            products.add(product.strip())
    return sorted(products)

product_list = extract_products(df['product'])

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
        filtered_df = df[df['product'].str.contains(selected_product, case=False, na=False)]
    else:
        filtered_df = df

    # Apply fuzzy matching
    error_lower = error_message.lower()
    scores = filtered_df['keywords'].fillna("").str.lower().apply(lambda x: fuzzy_score(error_lower, x))
    results = filtered_df[scores > 70]

    if not results.empty:
        st.write("Matching KB Articles:")
        for _, row in results.iterrows():
            st.markdown(f"**Article ID:** {row['article_id']}")
            st.markdown(f"**Resolution:** {row['title']}")
            if pd.notna(row['url']) and row['url'].strip():
                st.markdown(f"[View Article]({row['url']})")
            else:
                st.markdown("_No URL available for this article._")
            if 'Complexity' in row and pd.notna(row['Complexity']):
                complexity_status = str(row['Complexity']).strip().lower()
                if complexity_status == 'yes':
                    st.warning("⚠️ **Action:** Engage POD and mentor, complex case.")
                elif complexity_status == 'no':
                    st.info("ℹ️ **Action:** Continue troubleshooting and contact mentor for technical updates.")
            else:
                st.write("_Complexity status not specified._")
            st.markdown("---")
    else:
        st.write("No matching KB articles found.")

# Footer
st.markdown("""
---
<sub>Developed and managed by RTCC AMS. For feedback and changes, please email [tushar.thapa@hpe.com], referring to the Real-Time Collaboration Center under AMS (North America), which is responsible for compute and communication support.</sub>
""", unsafe_allow_html=True)
