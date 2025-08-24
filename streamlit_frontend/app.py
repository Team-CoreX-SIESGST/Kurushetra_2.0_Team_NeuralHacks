import streamlit as st
import requests
import json
import time
import os
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any, Optional
import io

# Page configuration
st.set_page_config(
    page_title="OmniSearch AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .file-upload-area {
        border: 2px dashed #ccc;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
    }
    .search-box {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .result-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .source-citation {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")

class OmniSearchClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def upload_file(self, file, workspace_id: str, file_id: str = None) -> Dict[str, Any]:
        files = {"file": file}
        data = {"workspace_id": workspace_id}
        if file_id:
            data["file_id"] = file_id
        
        response = requests.post(
            f"{self.base_url}/api/v1/upload",
            files=files,
            data=data,
            headers=self.headers
        )
        return response.json()
    
    def search(self, workspace_id: str, query: str, top_k: int = 10, 
               include_web: bool = True, rerank: bool = True, summarize: bool = True) -> Dict[str, Any]:
        payload = {
            "workspace_id": workspace_id,
            "query": query,
            "top_k": top_k,
            "include_web": include_web,
            "rerank": rerank,
            "summarize": summarize
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/search",
            json=payload,
            headers=self.headers
        )
        return response.json()
    
    def get_file_status(self, file_id: str, workspace_id: str) -> Dict[str, Any]:
        params = {"workspace_id": workspace_id}
        response = requests.get(
            f"{self.base_url}/api/v1/status/{file_id}",
            params=params,
            headers=self.headers
        )
        return response.json()
    
    def list_files(self, workspace_id: str) -> Dict[str, Any]:
        params = {"workspace_id": workspace_id}
        response = requests.get(
            f"{self.base_url}/api/v1/files",
            params=params,
            headers=self.headers
        )
        return response.json()
    
    def get_file_info(self, file_id: str, workspace_id: str) -> Dict[str, Any]:
        params = {"workspace_id": workspace_id}
        response = requests.get(
            f"{self.base_url}/api/v1/file/{file_id}",
            params=params,
            headers=self.headers
        )
        return response.json()

def main():
    # Initialize client
    client = OmniSearchClient(API_BASE_URL, API_TOKEN)
    
    # Sidebar configuration
    st.sidebar.title("🔧 Configuration")
    
    # API Configuration
    st.sidebar.subheader("API Settings")
    api_url = st.sidebar.text_input("API Base URL", value=API_BASE_URL)
    api_token = st.sidebar.text_input("API Token", value=API_TOKEN, type="password")
    
    # Workspace Configuration
    st.sidebar.subheader("Workspace")
    workspace_id = st.sidebar.text_input("Workspace ID", value="demo-workspace")
    
    # Update client with new settings
    client = OmniSearchClient(api_url, api_token)
    
    # Health check
    if not client.health_check():
        st.error("❌ Cannot connect to API server. Please check the API URL and ensure the server is running.")
        st.stop()
    
    # Main header
    st.markdown('<h1 class="main-header">🔍 OmniSearch AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-powered document search with web enrichment and intelligent model routing</p>', unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Files", "🔍 Search", "📁 File Management", "📊 Analytics"])
    
    with tab1:
        show_upload_tab(client, workspace_id)
    
    with tab2:
        show_search_tab(client, workspace_id)
    
    with tab3:
        show_file_management_tab(client, workspace_id)
    
    with tab4:
        show_analytics_tab(client, workspace_id)

def show_upload_tab(client: OmniSearchClient, workspace_id: str):
    st.markdown('<h2 class="sub-header">📤 Upload Documents</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Supported Formats:**
        - 📄 PDF (.pdf)
        - 📝 Word (.docx)
        - 📄 Text (.txt)
        
        **Features:**
        - Automatic text extraction and chunking
        - Vector embeddings generation
        - FAISS vector database indexing
        """)
        
        uploaded_file = st.file_uploader(
            "Choose a file to upload",
            type=['pdf', 'docx', 'txt'],
            help="Select a document to upload and process"
        )
        
        if uploaded_file:
            file_id = st.text_input("File ID (optional)", value="")
            
            if st.button("🚀 Upload & Process", type="primary"):
                with st.spinner("Uploading and processing file..."):
                    try:
                        result = client.upload_file(uploaded_file, workspace_id, file_id if file_id else None)
                        
                        if "success" in result and result["success"]:
                            st.success(f"✅ File uploaded successfully!")
                            st.json(result)
                            
                            # Show processing status
                            if "file_id" in result:
                                st.info("Processing file in background. Check File Management tab for status.")
                        else:
                            st.error(f"❌ Upload failed: {result.get('message', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error during upload: {str(e)}")
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Workspace", workspace_id)
        st.metric("API Status", "🟢 Connected" if client.health_check() else "🔴 Disconnected")
        st.markdown('</div>', unsafe_allow_html=True)

def show_search_tab(client: OmniSearchClient, workspace_id: str):
    st.markdown('<h2 class="sub-header">🔍 Intelligent Search</h2>', unsafe_allow_html=True)
    
    # Search configuration
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Enter your search query", placeholder="e.g., What are the key findings about machine learning?")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            top_k = st.slider("Top K results", min_value=5, max_value=50, value=10)
        with col_b:
            include_web = st.checkbox("Include web results", value=True)
        with col_c:
            rerank = st.checkbox("Enable reranking", value=True)
        
        summarize = st.checkbox("Generate AI summary", value=True)
    
    with col2:
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        st.markdown("**Search Options**")
        st.markdown(f"• Top K: {top_k}")
        st.markdown(f"• Web: {'✅' if include_web else '❌'}")
        st.markdown(f"• Rerank: {'✅' if rerank else '❌'}")
        st.markdown(f"• Summary: {'✅' if summarize else '❌'}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🔍 Search", type="primary", disabled=not query):
        if query:
            with st.spinner("Searching documents and generating AI response..."):
                try:
                    result = client.search(
                        workspace_id=workspace_id,
                        query=query,
                        top_k=top_k,
                        include_web=include_web,
                        rerank=rerank,
                        summarize=summarize
                    )
                    
                    if "success" in result and result["success"]:
                        display_search_results(result)
                    else:
                        st.error(f"❌ Search failed: {result.get('message', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Error during search: {str(e)}")

def display_search_results(result: Dict[str, Any]):
    st.markdown('<h3>🎯 AI-Generated Answer</h3>', unsafe_allow_html=True)
    
    # Answer section
    if "data" in result and "answer" in result["data"]:
        st.markdown(f"**Answer:** {result['data']['answer']}")
        
        # Confidence score
        confidence = result["data"].get("confidence", 0)
        st.progress(confidence)
        st.caption(f"Confidence: {confidence:.2%}")
        
        # Sources
        if "sources" in result["data"] and result["data"]["sources"]:
            st.markdown('<h4>📚 Sources</h4>', unsafe_allow_html=True)
            for i, source in enumerate(result["data"]["sources"]):
                with st.expander(f"Source {i+1}: {source.get('src_id', 'Unknown')}"):
                    st.markdown(f"**Quote:** {source.get('quote', 'No quote available')}")
                    st.markdown(f"**Location:** {source.get('url_or_file', 'Unknown')}")
        
        # Code (if present)
        if "code" in result["data"] and result["data"]["code"]:
            st.markdown('<h4>💻 Code</h4>', unsafe_allow_html=True)
            code_data = result["data"]["code"]
            st.code(code_data.get("content", ""), language=code_data.get("language", "text"))
        
        # Raw chunks
        if "raw_chunks" in result["data"] and result["data"]["raw_chunks"]:
            with st.expander("📄 Raw Search Results"):
                for i, chunk in enumerate(result["data"]["raw_chunks"][:5]):  # Show first 5
                    st.markdown(f"**Chunk {i+1}:**")
                    st.text(chunk.get("content", "")[:200] + "..." if len(chunk.get("content", "")) > 200 else chunk.get("content", ""))
        
        # Processing metadata
        if "processing_time" in result["data"]:
            st.info(f"⏱️ Processing time: {result['data']['processing_time']:.2f}s")
    
    else:
        st.warning("No answer generated. Check the search parameters and try again.")

def show_file_management_tab(client: OmniSearchClient, workspace_id: str):
    st.markdown('<h2 class="sub-header">📁 File Management</h2>', unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Refresh File List"):
        st.rerun()
    
    try:
        files_result = client.list_files(workspace_id)
        
        if "success" in files_result and files_result["success"]:
            files = files_result.get("data", {}).get("files", [])
            
            if files:
                st.markdown(f"**Total Files:** {len(files)}")
                
                # Create a DataFrame for better display
                df_data = []
                for file in files:
                    df_data.append({
                        "File ID": file.get("file_id", "N/A"),
                        "Filename": file.get("filename", "N/A"),
                        "Status": file.get("status", "N/A"),
                        "Size": f"{file.get('size', 0) / 1024:.1f} KB",
                        "Uploaded": file.get("uploaded_at", "N/A"),
                        "Chunks": file.get("chunk_count", 0)
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
                
                # File details
                st.markdown('<h4>📋 File Details</h4>', unsafe_allow_html=True)
                selected_file_id = st.selectbox("Select a file to view details", [f["File ID"] for f in df_data])
                
                if selected_file_id:
                    file_info = client.get_file_info(selected_file_id, workspace_id)
                    
                    if "success" in file_info and file_info["success"]:
                        info = file_info.get("data", {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Filename:** {info.get('filename', 'N/A')}")
                            st.markdown(f"**Status:** {info.get('status', 'N/A')}")
                            st.markdown(f"**Size:** {info.get('size', 0)} bytes")
                        
                        with col2:
                            st.markdown(f"**Uploaded:** {info.get('uploaded_at', 'N/A')}")
                            st.markdown(f"**Chunks:** {info.get('chunk_count', 0)}")
                            st.markdown(f"**Processing Time:** {info.get('processing_time', 'N/A')}")
                        
                        # File content preview
                        if "chunks" in info and info["chunks"]:
                            with st.expander("📄 Content Preview"):
                                for i, chunk in enumerate(info["chunks"][:3]):  # Show first 3 chunks
                                    st.markdown(f"**Chunk {i+1}:**")
                                    st.text(chunk.get("content", "")[:300] + "..." if len(chunk.get("content", "")) > 300 else chunk.get("content", ""))
                    else:
                        st.error(f"Failed to get file info: {file_info.get('message', 'Unknown error')}")
            else:
                st.info("📭 No files found in this workspace.")
        
        else:
            st.error(f"Failed to list files: {files_result.get('message', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"❌ Error loading files: {str(e)}")

def show_analytics_tab(client: OmniSearchClient, workspace_id: str):
    st.markdown('<h2 class="sub-header">📊 Analytics & Insights</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**📈 System Status**")
        
        # Health check
        api_health = client.health_check()
        st.metric("API Health", "🟢 Healthy" if api_health else "🔴 Unhealthy")
        
        # Workspace info
        st.metric("Workspace ID", workspace_id)
        st.metric("API Base URL", API_BASE_URL)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**🔧 Configuration**")
        
        # Environment info
        st.metric("Storage Type", os.getenv("STORAGE_TYPE", "local"))
        st.metric("Vector DB", os.getenv("VECTOR_DB_TYPE", "faiss"))
        st.metric("Model Router", "Ollama")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick actions
    st.markdown('<h4>⚡ Quick Actions</h4>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("🏥 Health Check"):
            health = client.health_check()
            if health:
                st.success("✅ API is healthy!")
            else:
                st.error("❌ API is not responding")
    
    with col_b:
        if st.button("📊 API Info"):
            try:
                response = requests.get(f"{API_BASE_URL}/")
                if response.status_code == 200:
                    info = response.json()
                    st.json(info)
                else:
                    st.error("Failed to get API info")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col_c:
        if st.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")

if __name__ == "__main__":
    main()
