"""
Document Converter service for OmniSearch AI.
Converts various document formats (.txt, .md, .pdf, .docx, .rtf, .odt, .csv) to JSON format.
"""

import os
import uuid
import json
import csv
import pandas as pd
from typing import List, Dict, Any, Optional, BinaryIO, Union
from datetime import datetime
import PyPDF2
import docx
from striprtf.striprtf import rtf_to_text
from odf import text, teletype
from odf.opendocument import load
import markdown
from io import StringIO

class DocumentConverterService:
    """Service for converting various document formats to JSON."""
    
    def __init__(self):
        self.supported_formats = {
            '.txt': 'text/plain',
            '.md': 'text/markdown', 
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.rtf': 'application/rtf',
            '.odt': 'application/vnd.oasis.opendocument.text',
            '.csv': 'text/csv'
        }
    
    async def convert_to_json(self, file: BinaryIO, filename: str, file_id: str = None) -> Dict[str, Any]:
        """
        Convert a document file to JSON format.
        
        Args:
            file: File binary data
            filename: Original filename
            file_id: Optional file identifier
            
        Returns:
            JSON representation of the document with structured content and metadata
        """
        try:
            if not file_id:
                file_id = str(uuid.uuid4())
            
            # Validate file format
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Extract content based on file type
            content_data = await self._extract_content(file, file_extension)
            
            # Create JSON structure
            json_document = {
                "document_id": file_id,
                "filename": filename,
                "file_extension": file_extension,
                "mime_type": self.supported_formats[file_extension],
                "conversion_timestamp": datetime.now().isoformat(),
                "metadata": {
                    "file_size": self._get_file_size(file),
                    "total_characters": len(str(content_data.get('raw_text', ''))),
                    "total_words": len(str(content_data.get('raw_text', '')).split()),
                    "document_type": self._classify_document_type(content_data),
                    "language": "en",  # Could be enhanced with language detection
                    "encoding": content_data.get('encoding', 'utf-8')
                },
                "content": content_data
            }
            
            return json_document
            
        except Exception as e:
            print(f"Document conversion failed: {e}")
            return {
                "document_id": file_id or str(uuid.uuid4()),
                "filename": filename,
                "error": str(e),
                "conversion_timestamp": datetime.now().isoformat(),
                "status": "conversion_failed"
            }
    
    async def _extract_content(self, file: BinaryIO, file_extension: str) -> Dict[str, Any]:
        """Extract content from different file formats."""
        try:
            if file_extension == '.txt':
                return await self._extract_txt_content(file)
            elif file_extension == '.md':
                return await self._extract_md_content(file)
            elif file_extension == '.pdf':
                return await self._extract_pdf_content(file)
            elif file_extension == '.docx':
                return await self._extract_docx_content(file)
            elif file_extension == '.rtf':
                return await self._extract_rtf_content(file)
            elif file_extension == '.odt':
                return await self._extract_odt_content(file)
            elif file_extension == '.csv':
                return await self._extract_csv_content(file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            print(f"Content extraction failed: {e}")
            raise
    
    async def _extract_txt_content(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract content from TXT file."""
        try:
            file.seek(0)
            content = file.read()
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            text_content = None
            used_encoding = 'utf-8'
            
            for encoding in encodings:
                try:
                    text_content = content.decode(encoding)
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if text_content is None:
                text_content = content.decode('latin-1', errors='ignore')
                used_encoding = 'latin-1'
            
            # Split into paragraphs
            paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
            
            return {
                "raw_text": text_content,
                "structured_content": {
                    "type": "plain_text",
                    "paragraphs": paragraphs,
                    "line_count": len(text_content.split('\n')),
                    "paragraph_count": len(paragraphs)
                },
                "encoding": used_encoding,
                "format_specific": {
                    "text_format": "plain"
                }
            }
            
        except Exception as e:
            print(f"TXT extraction failed: {e}")
            raise
    
    async def _extract_md_content(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract content from Markdown file."""
        try:
            file.seek(0)
            content = file.read().decode('utf-8')
            
            # Convert markdown to HTML for structure extraction
            md = markdown.Markdown(extensions=['meta', 'toc'])
            html_content = md.convert(content)
            
            # Extract headers
            lines = content.split('\n')
            headers = []
            paragraphs = []
            code_blocks = []
            
            current_paragraph = []
            in_code_block = False
            current_code_block = []
            
            for line in lines:
                stripped_line = line.strip()
                
                if stripped_line.startswith('```'):
                    if in_code_block:
                        code_blocks.append('\n'.join(current_code_block))
                        current_code_block = []
                        in_code_block = False
                    else:
                        if current_paragraph:
                            paragraphs.append(' '.join(current_paragraph))
                            current_paragraph = []
                        in_code_block = True
                elif in_code_block:
                    current_code_block.append(line)
                elif stripped_line.startswith('#'):
                    if current_paragraph:
                        paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
                    headers.append({
                        "level": len(stripped_line.split()[0]),
                        "text": stripped_line.lstrip('#').strip()
                    })
                elif stripped_line:
                    current_paragraph.append(stripped_line)
                elif current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
            
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
            
            return {
                "raw_text": content,
                "structured_content": {
                    "type": "markdown",
                    "headers": headers,
                    "paragraphs": paragraphs,
                    "code_blocks": code_blocks,
                    "html_content": html_content,
                    "metadata": getattr(md, 'Meta', {})
                },
                "encoding": "utf-8",
                "format_specific": {
                    "markdown_extensions": ['meta', 'toc'],
                    "has_toc": '[TOC]' in content.upper()
                }
            }
            
        except Exception as e:
            print(f"Markdown extraction failed: {e}")
            raise
    
    async def _extract_pdf_content(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract content from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            pages_content = []
            full_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    pages_content.append({
                        "page_number": page_num + 1,
                        "text": page_text.strip(),
                        "character_count": len(page_text)
                    })
                    full_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            # Extract metadata
            metadata = {}
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get('/Title', ''),
                    "author": pdf_reader.metadata.get('/Author', ''),
                    "subject": pdf_reader.metadata.get('/Subject', ''),
                    "creator": pdf_reader.metadata.get('/Creator', ''),
                    "producer": pdf_reader.metadata.get('/Producer', ''),
                    "creation_date": str(pdf_reader.metadata.get('/CreationDate', '')),
                    "modification_date": str(pdf_reader.metadata.get('/ModDate', ''))
                }
            
            return {
                "raw_text": full_text.strip(),
                "structured_content": {
                    "type": "pdf",
                    "pages": pages_content,
                    "total_pages": len(pdf_reader.pages),
                    "pdf_metadata": metadata
                },
                "encoding": "pdf",
                "format_specific": {
                    "pdf_version": pdf_reader.pdf_header if hasattr(pdf_reader, 'pdf_header') else 'unknown',
                    "encrypted": pdf_reader.is_encrypted
                }
            }
            
        except Exception as e:
            print(f"PDF extraction failed: {e}")
            raise
    
    async def _extract_docx_content(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract content from DOCX file."""
        try:
            doc = docx.Document(file)
            paragraphs = []
            full_text = ""
            headers = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraph_info = {
                        "text": para.text,
                        "style": para.style.name if para.style else "Normal"
                    }
                    
                    # Check if it's a header
                    if para.style and ('heading' in para.style.name.lower() or 'title' in para.style.name.lower()):
                        headers.append({
                            "text": para.text,
                            "style": para.style.name
                        })
                    
                    paragraphs.append(paragraph_info)
                    full_text += para.text + "\n"
            
            # Extract document properties
            core_props = doc.core_properties
            doc_metadata = {
                "title": core_props.title or "",
                "author": core_props.author or "",
                "subject": core_props.subject or "",
                "created": str(core_props.created) if core_props.created else "",
                "modified": str(core_props.modified) if core_props.modified else "",
                "keywords": core_props.keywords or ""
            }
            
            return {
                "raw_text": full_text.strip(),
                "structured_content": {
                    "type": "docx",
                    "paragraphs": paragraphs,
                    "headers": headers,
                    "document_metadata": doc_metadata,
                    "total_paragraphs": len(paragraphs)
                },
                "encoding": "docx",
                "format_specific": {
                    "document_format": "Office Open XML"
                }
            }
            
        except Exception as e:
            print(f"DOCX extraction failed: {e}")
            raise
    
    async def _extract_rtf_content(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract content from RTF file."""
        try:
            file.seek(0)
            rtf_content = file.read().decode('utf-8', errors='ignore')
            
            # Convert RTF to plain text
            plain_text = rtf_to_text(rtf_content)
            
            # Split into paragraphs
            paragraphs = [p.strip() for p in plain_text.split('\n\n') if p.strip()]
            
            return {
                "raw_text": plain_text,
                "structured_content": {
                    "type": "rtf",
                    "paragraphs": paragraphs,
                    "paragraph_count": len(paragraphs)
                },
                "encoding": "rtf",
                "format_specific": {
                    "rich_text_format": True,
                    "original_rtf_size": len(rtf_content)
                }
            }
            
        except Exception as e:
            print(f"RTF extraction failed: {e}")
            raise
    
    async def _extract_odt_content(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract content from ODT file."""
        try:
            file.seek(0)
            doc = load(file)
            
            paragraphs = []
            full_text = ""
            
            # Extract text from ODT
            for paragraph in doc.getElementsByType(text.P):
                para_text = teletype.extractText(paragraph)
                if para_text.strip():
                    paragraphs.append(para_text)
                    full_text += para_text + "\n"
            
            return {
                "raw_text": full_text.strip(),
                "structured_content": {
                    "type": "odt",
                    "paragraphs": paragraphs,
                    "paragraph_count": len(paragraphs)
                },
                "encoding": "odt",
                "format_specific": {
                    "document_format": "OpenDocument Text"
                }
            }
            
        except Exception as e:
            print(f"ODT extraction failed: {e}")
            raise
    
    async def _extract_csv_content(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract content from CSV file."""
        try:
            file.seek(0)
            content = file.read().decode('utf-8', errors='ignore')
            
            # Parse CSV
            csv_reader = csv.reader(StringIO(content))
            rows = list(csv_reader)
            
            if not rows:
                return {
                    "raw_text": "",
                    "structured_content": {"type": "csv", "data": []},
                    "encoding": "csv"
                }
            
            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []
            
            # Convert to list of dictionaries
            structured_data = []
            for row in data_rows:
                if len(row) >= len(headers):
                    row_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                    structured_data.append(row_dict)
            
            # Create text representation
            text_content = f"CSV Data with {len(headers)} columns and {len(data_rows)} rows:\n"
            text_content += "Headers: " + ", ".join(headers) + "\n\n"
            
            for i, row_dict in enumerate(structured_data[:10]):  # Limit to first 10 rows for text
                text_content += f"Row {i+1}: " + ", ".join([f"{k}: {v}" for k, v in row_dict.items()]) + "\n"
            
            if len(structured_data) > 10:
                text_content += f"... and {len(structured_data) - 10} more rows"
            
            return {
                "raw_text": text_content,
                "structured_content": {
                    "type": "csv",
                    "headers": headers,
                    "data": structured_data,
                    "total_rows": len(data_rows),
                    "total_columns": len(headers),
                    "data_types": self._analyze_csv_types(structured_data, headers)
                },
                "encoding": "csv",
                "format_specific": {
                    "csv_dialect": "excel",
                    "has_headers": True
                }
            }
            
        except Exception as e:
            print(f"CSV extraction failed: {e}")
            raise
    
    def _analyze_csv_types(self, data: List[Dict], headers: List[str]) -> Dict[str, str]:
        """Analyze data types in CSV columns."""
        type_analysis = {}
        
        for header in headers:
            column_data = [row.get(header, '') for row in data[:100]]  # Sample first 100 rows
            
            # Simple type detection
            if all(self._is_number(val) for val in column_data if val):
                type_analysis[header] = "numeric"
            elif all(self._is_date(val) for val in column_data if val):
                type_analysis[header] = "date"
            else:
                type_analysis[header] = "text"
        
        return type_analysis
    
    def _is_number(self, value: str) -> bool:
        """Check if string represents a number."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_date(self, value: str) -> bool:
        """Check if string represents a date."""
        try:
            pd.to_datetime(value)
            return True
        except:
            return False
    
    def _classify_document_type(self, content_data: Dict[str, Any]) -> str:
        """Classify document type based on content."""
        content_type = content_data.get('structured_content', {}).get('type', 'unknown')
        
        if content_type == 'csv':
            return 'data_table'
        elif content_type == 'markdown':
            return 'technical_documentation'
        elif content_type in ['pdf', 'docx', 'odt', 'rtf']:
            return 'formatted_document'
        else:
            return 'plain_text'
    
    def _get_file_size(self, file: BinaryIO) -> int:
        """Get file size in bytes."""
        try:
            current_pos = file.tell()
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(current_pos)  # Restore position
            return size
        except:
            return 0
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return list(self.supported_formats.keys())
    
    def get_format_info(self) -> Dict[str, str]:
        """Get mapping of supported formats to MIME types."""
        return self.supported_formats.copy()
    
    async def batch_convert(self, files: List[tuple], workspace_id: str = None) -> List[Dict[str, Any]]:
        """
        Convert multiple files to JSON format.
        
        Args:
            files: List of (file, filename) tuples
            workspace_id: Optional workspace identifier
            
        Returns:
            List of JSON documents
        """
        results = []
        
        for file, filename in files:
            try:
                json_doc = await self.convert_to_json(file, filename)
                if workspace_id:
                    json_doc['workspace_id'] = workspace_id
                results.append(json_doc)
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")
                results.append({
                    "filename": filename,
                    "error": str(e),
                    "status": "failed"
                })
        
        return results
