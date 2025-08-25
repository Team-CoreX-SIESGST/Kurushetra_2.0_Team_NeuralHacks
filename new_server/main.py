from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import tempfile
from typing import Dict, Any, List
import uvicorn
from dotenv import load_dotenv
from file_processor import FileProcessor
from rag_system import RAGSystem

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="File Processing & RAG System", version="1.0.0")

# Initialize processors
file_processor = FileProcessor()
rag_system = RAGSystem()

@app.get("/")
async def root():
    return {"message": "File Processing & RAG System API"}

@app.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "supported_formats": [
            "PDF (.pdf)",
            "Word Documents (.docx, .doc)",
            "Excel Spreadsheets (.xlsx, .xls)",
            "PowerPoint (.pptx, .ppt)",
            "Text Files (.txt)",
            "CSV Files (.csv)",
            "JSON Files (.json)",
            "XML Files (.xml)",
            "HTML Files (.html, .htm)",
            "Markdown Files (.md)",
            "Images with OCR (.png, .jpg, .jpeg, .tiff)"
        ]
    }

@app.post("/process-file")
async def process_file(file: UploadFile = File(...)):
    """Process uploaded file and extract data to JSON format"""
    try:
        # Validate file type
        if not file_processor.is_supported_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {file_processor.get_supported_formats()}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the file
            extracted_data = file_processor.process_file(temp_file_path, file.filename)
            
            # Save extracted data as JSON
            json_filename = f"extracted_data_{file.filename.split('.')[0]}.json"
            json_path = os.path.join("extracted_data", json_filename)
            
            # Create directory if it doesn't exist
            os.makedirs("extracted_data", exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(extracted_data, json_file, indent=2, ensure_ascii=False)
            
            return {
                "status": "success",
                "message": "File processed successfully",
                "extracted_data": extracted_data,
                "json_file_path": json_path,
                "file_info": {
                    "original_filename": file.filename,
                    "file_size": len(content),
                    "content_type": file.content_type
                }
            }
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/process-and-summarize")
async def process_and_summarize(file: UploadFile = File(...)):
    """Process file and generate RAG-based summary using Gemini API"""
    try:
        # First process the file
        if not file_processor.is_supported_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {file_processor.get_supported_formats()}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the file
            extracted_data = file_processor.process_file(temp_file_path, file.filename)
            
            # Generate summary using RAG system
            summary = await rag_system.generate_summary(extracted_data)
            
            # Save both extracted data and summary
            output_data = {
                "original_file": file.filename,
                "extracted_data": extracted_data,
                "summary": summary,
                "processing_info": {
                    "file_size": len(content),
                    "content_type": file.content_type,
                    "processed_at": rag_system.get_current_timestamp()
                }
            }
            
            # Save to JSON file
            json_filename = f"processed_with_summary_{file.filename.split('.')[0]}.json"
            json_path = os.path.join("processed_data", json_filename)
            
            os.makedirs("processed_data", exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(output_data, json_file, indent=2, ensure_ascii=False)
            
            return {
                "status": "success",
                "message": "File processed and summarized successfully",
                "extracted_data": extracted_data,
                "summary": summary,
                "json_file_path": json_path,
                "file_info": {
                    "original_filename": file.filename,
                    "file_size": len(content),
                    "content_type": file.content_type
                }
            }
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing and summarizing file: {str(e)}")

@app.post("/summarize-json")
async def summarize_json_data(json_data: Dict[Any, Any]):
    """Generate RAG-based summary from provided JSON data"""
    try:
        summary = await rag_system.generate_summary(json_data)
        
        return {
            "status": "success",
            "message": "Summary generated successfully",
            "input_data": json_data,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.post("/process-and-summarize-with-urls")
async def process_and_summarize_with_urls(file: UploadFile = File(...)):
    """Process file, generate RAG-based summary, and find related web URLs"""
    try:
        # First process the file
        if not file_processor.is_supported_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {file_processor.get_supported_formats()}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the file
            extracted_data = file_processor.process_file(temp_file_path, file.filename)
            
            # Generate summary with related web URLs using RAG system
            summary_with_urls = await rag_system.generate_summary_with_urls(extracted_data, include_urls=True)
            
            # Save both extracted data and summary with URLs
            output_data = {
                "original_file": file.filename,
                "extracted_data": extracted_data,
                "summary_with_urls": summary_with_urls,
                "processing_info": {
                    "file_size": len(content),
                    "content_type": file.content_type,
                    "processed_at": rag_system.get_current_timestamp()
                }
            }
            
            # Save to JSON file
            json_filename = f"processed_with_summary_and_urls_{file.filename.split('.')[0]}.json"
            json_path = os.path.join("processed_data", json_filename)
            
            os.makedirs("processed_data", exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(output_data, json_file, indent=2, ensure_ascii=False)
            
            return {
                "status": "success",
                "message": "File processed, summarized, and related URLs found successfully",
                "extracted_data": extracted_data,
                "summary": summary_with_urls,
                "json_file_path": json_path,
                "file_info": {
                    "original_filename": file.filename,
                    "file_size": len(content),
                    "content_type": file.content_type
                }
            }
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file with URL search: {str(e)}")

@app.post("/summarize-json-with-urls")
async def summarize_json_data_with_urls(json_data: Dict[Any, Any]):
    """Generate RAG-based summary with related web URLs from provided JSON data"""
    try:
        summary_with_urls = await rag_system.generate_summary_with_urls(json_data, include_urls=True)
        
        return {
            "status": "success",
            "message": "Summary with related URLs generated successfully",
            "input_data": json_data,
            "summary_with_urls": summary_with_urls
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary with URLs: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "file_processor": "active",
            "rag_system": "active",
            "gemini_api": rag_system.check_api_status()
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
