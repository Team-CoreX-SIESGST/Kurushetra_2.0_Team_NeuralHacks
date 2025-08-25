import streamlit as st
import requests
import json
import os
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

def main():
    st.set_page_config(
        page_title="File Processing & RAG System",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 File Processing & RAG System")
    st.markdown("Upload files and get AI-powered summaries using Gemini API")
    
    # Sidebar
    st.sidebar.title("🔧 Options")
    
    # Check API status
    check_api_status()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📊 Supported Formats", "🔍 JSON Summarizer"])
    
    with tab1:
        upload_and_process_tab()
    
    with tab2:
        supported_formats_tab()
    
    with tab3:
        json_summarizer_tab()

def check_api_status():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            st.sidebar.success("✅ API Server: Online")
            
            # Show service status
            services = health_data.get("services", {})
            for service, status in services.items():
                if status == "active" or status == "configured":
                    st.sidebar.success(f"✅ {service.title()}: {status}")
                else:
                    st.sidebar.warning(f"⚠️ {service.title()}: {status}")
        else:
            st.sidebar.error("❌ API Server: Error")
    except requests.exceptions.RequestException:
        st.sidebar.error("❌ API Server: Offline")
        st.sidebar.markdown("**Start the server first:**")
        st.sidebar.code("python main.py")

def upload_and_process_tab():
    """Main file upload and processing interface"""
    st.header("📤 Upload and Process Files")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file to process",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'csv', 'txt', 'json', 'xml', 'html', 'htm', 'md', 'png', 'jpg', 'jpeg', 'tiff'],
        help="Upload any supported file format"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.info(f"📁 **File:** {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Processing options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Extract Data Only", use_container_width=True):
                process_file_only(uploaded_file)
        
        with col2:
            if st.button("🤖 Process + AI Summary", use_container_width=True):
                process_file_with_summary(uploaded_file)

def process_file_only(uploaded_file):
    """Process file and extract data to JSON"""
    with st.spinner("🔄 Processing file..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_BASE_URL}/process-file", files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ File processed successfully!")
                
                # Show file info
                file_info = result.get("file_info", {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{file_info.get('file_size', 0)} bytes")
                with col2:
                    st.metric("Content Type", file_info.get('content_type', 'Unknown'))
                with col3:
                    st.metric("Status", result.get('status', 'Unknown'))
                
                # Show extracted data
                st.subheader("📋 Extracted Data")
                extracted_data = result.get("extracted_data", {})
                
                # Display content based on type
                content_type = extracted_data.get("content_type", "unknown")
                
                if content_type == "text":
                    st.text_area("Text Content", extracted_data.get("content", ""), height=200)
                elif content_type == "csv":
                    st.write("**CSV Data Preview:**")
                    data = extracted_data.get("data", [])
                    if data:
                        st.dataframe(data[:100])  # Show first 100 rows
                elif content_type == "excel":
                    st.write("**Excel Sheets:**")
                    sheets = extracted_data.get("sheets", {})
                    for sheet_name, sheet_data in sheets.items():
                        st.write(f"**Sheet: {sheet_name}**")
                        data = sheet_data.get("data", [])
                        if data:
                            st.dataframe(data[:100])
                else:
                    # Show raw JSON for other types
                    st.json(extracted_data)
                
                # Download JSON button
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="💾 Download JSON",
                    data=json_str,
                    file_name=f"extracted_{uploaded_file.name}.json",
                    mime="application/json"
                )
                
            else:
                st.error(f"❌ Error processing file: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def process_file_with_summary(uploaded_file):
    """Process file and generate AI summary"""
    with st.spinner("🤖 Processing file and generating AI summary..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_BASE_URL}/process-and-summarize", files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ File processed and summarized successfully!")
                
                # Show file info
                file_info = result.get("file_info", {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{file_info.get('file_size', 0)} bytes")
                with col2:
                    st.metric("Content Type", file_info.get('content_type', 'Unknown'))
                with col3:
                    st.metric("Status", result.get('status', 'Unknown'))
                
                # Show summaries
                summary = result.get("summary", {})
                
                if "error" in summary:
                    st.warning("⚠️ AI Summary unavailable - using fallback")
                    fallback = summary.get("fallback_summary", {})
                    st.json(fallback)
                else:
                    summaries = summary.get("summaries", {})
                    
                    # Display different summary types in tabs
                    if summaries:
                        summary_tabs = st.tabs(list(summaries.keys()))
                        
                        for i, (summary_type, summary_content) in enumerate(summaries.items()):
                            with summary_tabs[i]:
                                st.markdown(f"**{summary_type.title()} Summary:**")
                                st.write(summary_content)
                    
                    # Show metadata
                    metadata = summary.get("metadata", {})
                    if metadata:
                        st.subheader("📊 Summary Metadata")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Generated:** {metadata.get('generated_at', 'Unknown')}")
                            st.write(f"**Source:** {metadata.get('source_file', 'Unknown')}")
                        with col2:
                            stats = summary.get("content_stats", {})
                            if stats:
                                st.write(f"**Word Count:** {stats.get('word_count', 0)}")
                                st.write(f"**Characters:** {stats.get('character_count', 0)}")
                
                # Show extracted data in expander
                with st.expander("📋 View Extracted Data"):
                    st.json(result.get("extracted_data", {}))
                
                # Download JSON button
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="💾 Download Complete JSON",
                    data=json_str,
                    file_name=f"processed_{uploaded_file.name}.json",
                    mime="application/json"
                )
                
            else:
                st.error(f"❌ Error processing file: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def supported_formats_tab():
    """Show supported file formats"""
    st.header("📊 Supported File Formats")
    
    try:
        response = requests.get(f"{API_BASE_URL}/supported-formats")
        if response.status_code == 200:
            result = response.json()
            formats = result.get("supported_formats", [])
            
            st.success(f"✅ {len(formats)} file formats supported")
            
            # Display formats in a nice table
            format_data = []
            for fmt in formats:
                if "(" in fmt and ")" in fmt:
                    name = fmt.split("(")[0].strip()
                    extensions = fmt.split("(")[1].split(")")[0]
                    format_data.append({"Format": name, "Extensions": extensions})
            
            if format_data:
                st.table(format_data)
            else:
                for fmt in formats:
                    st.write(f"• {fmt}")
                    
        else:
            st.error("❌ Could not fetch supported formats")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def json_summarizer_tab():
    """JSON data summarizer"""
    st.header("🔍 JSON Data Summarizer")
    st.write("Paste JSON data below to generate AI summaries")
    
    # JSON input
    json_input = st.text_area(
        "JSON Data",
        height=200,
        placeholder='{\n  "title": "Sample Document",\n  "content": "Your content here...",\n  "data": [{"key": "value"}]\n}'
    )
    
    if st.button("🤖 Generate Summary", use_container_width=True):
        if json_input.strip():
            try:
                # Parse JSON
                json_data = json.loads(json_input)
                
                with st.spinner("🤖 Generating AI summary..."):
                    response = requests.post(
                        f"{API_BASE_URL}/summarize-json",
                        json=json_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Summary generated successfully!")
                        
                        summary = result.get("summary", {})
                        
                        if "error" in summary:
                            st.warning("⚠️ AI Summary unavailable - using fallback")
                            fallback = summary.get("fallback_summary", {})
                            st.json(fallback)
                        else:
                            summaries = summary.get("summaries", {})
                            
                            if summaries:
                                summary_tabs = st.tabs(list(summaries.keys()))
                                
                                for i, (summary_type, summary_content) in enumerate(summaries.items()):
                                    with summary_tabs[i]:
                                        st.markdown(f"**{summary_type.title()} Summary:**")
                                        st.write(summary_content)
                            
                            # Show metadata
                            metadata = summary.get("metadata", {})
                            if metadata:
                                st.subheader("📊 Summary Metadata")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Generated:** {metadata.get('generated_at', 'Unknown')}")
                                with col2:
                                    stats = summary.get("content_stats", {})
                                    if stats:
                                        st.write(f"**Word Count:** {stats.get('word_count', 0)}")
                                        st.write(f"**Characters:** {stats.get('character_count', 0)}")
                        
                        # Download button
                        json_str = json.dumps(result, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="💾 Download Summary JSON",
                            data=json_str,
                            file_name="json_summary.json",
                            mime="application/json"
                        )
                        
                    else:
                        st.error(f"❌ Error generating summary: {response.text}")
                        
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format. Please check your JSON syntax.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter JSON data")

if __name__ == "__main__":
    main()
