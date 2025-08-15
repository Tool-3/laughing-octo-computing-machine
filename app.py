import os
from dotenv import load_dotenv
import streamlit as st
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from firecrawl import FirecrawlApp

# Load environment variables (works locally)
load_dotenv()

# For Streamlit Cloud, use st.secrets
API_KEY = os.getenv("FIRECRAWL_API_KEY") or st.secrets.get("FIRECRAWL_API_KEY")

class ExampleSchema(BaseModel):
    title: str = Field(..., description="Page title")
    description: str = Field(None, description="Meta description or summary")

client = FirecrawlApp(api_key=API_KEY)

def scrape_urls(urls: List[str], schema_model: BaseModel) -> Dict[str, Any]:
    schema_json = schema_model.model_json_schema()
    results = {}
    for url in urls:
        try:
            response = client.scrape_url(
                url,
                params={
                    "formats": ["extract"],
                    "extract": {
                        "schema": schema_json,
                        "prompt": "Extract the page title and description"
                    }
                }
            )
            results[url] = response.get("extract", {})
        except Exception as e:
            results[url] = {"error": str(e)}
    return results

def main():
    st.title("🔍 Firecrawl Scraper (Streamlit)")
    st.write("Enter one or more URLs below and extract structured data using Firecrawl.")

    url_input = st.text_area("URLs", height=150, placeholder="https://example.com")
    urls = [u.strip() for u in url_input.splitlines() if u.strip()]

    if st.button("Scrape"):
        if not urls:
            st.error("Please enter at least one URL.")
        elif not API_KEY:
            st.error("API key not found — add it in Streamlit Secrets or your .env file.")
        else:
            with st.spinner("Scraping..."):
                results = scrape_urls(urls, ExampleSchema)
            for url, data in results.items():
                st.subheader(url)
                st.json(data)

if __name__ == "__main__":
    main()
