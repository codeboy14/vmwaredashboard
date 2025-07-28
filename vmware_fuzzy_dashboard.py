import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

# Load the CSV file
df = pd.read_csv("vmware_kb_articles.csv")

# Extract product keywords from the 'keywords' column
def extract_products(keywords_series):
    products = set()
    for keywords in keywords_series.dropna():
        for keyword in keywords.split(','):
            products.add(keyword.strip().split()[0])
    return sorted(products)

product_list = extract_products(df['keywords'])

# Streamlit UI
st.title("VMware KB Article Finder with Fuzzy Matching")
st.write("Enter an error message or keyword to find relevant VMware KB articles.")

error_message = st.text_input("Error Message or Keyword")
selected_product = st.selectbox("Filter by Product (optional)", ["All"] + product_list)

if error_message:
    filtered_df = df[df['keywords'].str.contains(selected_product, case=False, na=False)] if selected_product != "All" else df

    def fuzzy_filter(row):
        return fuzz.partial_ratio(error_message.lower(), str(row['keywords']).lower()) > 70

    results = filtered_df[filtered_df.apply(fuzzy_filter, axis=1)]

    if not results.empty:
        st.write("Matching KB Articles:")
        for _, row in results.iterrows():
            st.markdown(f"**Article ID:** {row['article_id']}")
            st.markdown(f"**Resolution:** {row['title']}")
            st.markdown(f"View Article")
            st.markdown("---")
    else:
        st.write("No matching KB articles found.")

# Footer with footnote
st.markdown("""
---
<sub>Developed and managed by RTCC AMS. For feedback and changes, please email [tushar.thapa@hpe.com](mailto:tushar.thapa@hpe.com) to the Real-Time Command Center under AMS (North America), which is responsible for compute and communication support.</sub>
""", unsafe_allow_html=True)
