import streamlit as st
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="SmartScanner",
    layout="wide"
)

# Constants
BACKEND_URL = "http://localhost:8000"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        return response.status_code == 200
    except:
        return False

def main():
    st.title("SmartScanner")
    
    # Check backend health
    if not check_backend_health():
        st.error("Backend server is not running. Please start the backend server.")
        return
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["Upload Documents", "Search Documents"])
    
    with tab1:
        st.header("Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("Process Files"):
                try:
                    files = [("files", file) for file in uploaded_files]
                    response = requests.post(
                        f"{BACKEND_URL}/upload",
                        files=files
                    )
                    if response.status_code == 200:
                        st.success("Files processed successfully!")
                    else:
                        st.error(f"Failed to process files: {response.text}")
                except Exception as e:
                    st.error(f"Error uploading files: {str(e)}")
    
    with tab2:
        st.header("Search Documents")
        search_term = st.text_input("Enter search term")
        
        if search_term:
            if st.button("Search"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/search",
                        json={"search_term": search_term}
                    )
                    if response.status_code == 200:
                        results = response.json()
                        
                        # Display results
                        st.subheader(f"Found {len(results)} matches:")
                        for result in results:
                            with st.expander(f"Match in {result['filename']} (Page {result['page']})"):
                                st.write(result['text'])
                                st.write(f"Similarity Score: {result['score']:.2f}")
                    else:
                        st.error(f"Search failed: {response.text}")
                except Exception as e:
                    st.error(f"Error performing search: {str(e)}")

if __name__ == "__main__":
    main() 