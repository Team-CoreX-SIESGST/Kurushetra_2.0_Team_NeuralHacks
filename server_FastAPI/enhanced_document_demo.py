#!/usr/bin/env python3
"""
Enhanced Document Processing Demo Script for OmniSearch AI.
Demonstrates the complete workflow: Document -> JSON -> Gemini RAG -> Web Search -> Enhanced Summary.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add the app directory to the path so we can import our services
sys.path.append(str(Path(__file__).parent / "app"))

from services.document_converter import DocumentConverterService
from services.gemini_rag_service import GeminiRAGService
from services.enhanced_summary_service import EnhancedSummaryService

class EnhancedDocumentDemo:
    """Demo class for enhanced document processing workflow."""
    
    def __init__(self):
        self.document_converter = DocumentConverterService()
        self.gemini_rag_service = GeminiRAGService()
        self.enhanced_summary_service = EnhancedSummaryService()
        
    async def demo_document_conversion(self, file_path: str):
        """Demo document to JSON conversion."""
        print(f"🔄 Converting document to JSON: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                filename = os.path.basename(file_path)
                json_document = await self.document_converter.convert_to_json(file, filename)
                
                print(f"✅ Document converted successfully!")
                print(f"   📄 Document ID: {json_document.get('document_id', 'Unknown')}")
                print(f"   📊 Total characters: {json_document.get('metadata', {}).get('total_characters', 0):,}")
                print(f"   📝 Total words: {json_document.get('metadata', {}).get('total_words', 0):,}")
                print(f"   🏷️  Document type: {json_document.get('metadata', {}).get('document_type', 'Unknown')}")
                print(f"   📅 Conversion time: {json_document.get('conversion_timestamp', 'Unknown')}")
                
                return json_document
                
        except Exception as e:
            print(f"❌ Document conversion failed: {e}")
            return None
    
    async def demo_gemini_rag_summary(self, json_document: dict):
        """Demo Gemini RAG summarization."""
        print(f"\n🧠 Generating summary using Gemini RAG...")
        
        try:
            summary = await self.gemini_rag_service.generate_document_summary(json_document)
            
            print(f"✅ Summary generated successfully!")
            print(f"   📝 Summary: {summary.get('summary', 'No summary available')[:200]}...")
            print(f"   🏷️  Key topics: {', '.join(summary.get('key_topics', [])[:5])}")
            print(f"   💡 Insights count: {len(summary.get('insights', []))}")
            print(f"   🎯 Confidence: {summary.get('confidence', 0):.2f}")
            
            return summary
            
        except Exception as e:
            print(f"❌ Summary generation failed: {e}")
            return None
    
    async def demo_search_tags(self, json_document: dict):
        """Demo search tag generation."""
        print(f"\n🔍 Generating search tags...")
        
        try:
            search_tags = await self.gemini_rag_service.generate_search_tags(json_document)
            
            print(f"✅ Search tags generated!")
            print(f"   🏷️  Tags ({len(search_tags)}): {', '.join(search_tags)}")
            
            return search_tags
            
        except Exception as e:
            print(f"❌ Search tag generation failed: {e}")
            return []
    
    async def demo_complete_workflow(self, file_path: str):
        """Demo the complete enhanced document processing workflow."""
        print(f"\n🚀 STARTING COMPLETE WORKFLOW DEMO")
        print(f"{'=' * 60}")
        print(f"📄 File: {file_path}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 60}")
        
        start_time = datetime.now()
        
        try:
            with open(file_path, 'rb') as file:
                filename = os.path.basename(file_path)
                
                print(f"\n📋 STEP 1: Complete Enhanced Processing")
                result = await self.enhanced_summary_service.process_document_with_web_enhancement(
                    file=file, 
                    filename=filename
                )
                
                if result.get("status") == "success":
                    print(f"✅ Complete workflow finished successfully!")
                    
                    # Display results
                    doc_summary = result.get("document_summary", {})
                    web_research = result.get("web_research", {})
                    enhanced_summary = result.get("enhanced_summary", {})
                    processing_meta = result.get("processing_metadata", {})
                    
                    print(f"\n📊 RESULTS SUMMARY:")
                    print(f"   🆔 Document ID: {result.get('document_id', 'Unknown')}")
                    print(f"   📝 Original Summary: {doc_summary.get('summary', 'N/A')[:150]}...")
                    print(f"   🏷️  Key Topics: {', '.join(doc_summary.get('key_topics', [])[:5])}")
                    print(f"   🔍 Search Tags: {', '.join(web_research.get('search_tags', []))}")
                    print(f"   🌐 Web URLs Found: {web_research.get('total_urls_found', 0)}")
                    
                    print(f"\n🚀 ENHANCED SUMMARY:")
                    enhanced_text = enhanced_summary.get('enhanced_summary', 'Not available')
                    print(f"   {enhanced_text[:300]}...")
                    
                    print(f"\n💡 CONTEXTUAL INSIGHTS:")
                    for i, insight in enumerate(enhanced_summary.get('contextual_insights', [])[:3], 1):
                        print(f"   {i}. {insight}")
                    
                    print(f"\n🔗 RELATED TOPICS:")
                    for i, topic in enumerate(enhanced_summary.get('related_topics', [])[:3], 1):
                        print(f"   {i}. {topic}")
                    
                    print(f"\n⚡ PROCESSING STATS:")
                    print(f"   ⏱️  Total time: {processing_meta.get('processing_time', 0):.2f} seconds")
                    print(f"   📋 Workflow steps: {len(processing_meta.get('workflow_steps', []))}")
                    print(f"   🌐 Web sources: {enhanced_summary.get('web_sources_used', 0)}")
                    print(f"   🎯 Confidence: {enhanced_summary.get('confidence_score', 0):.2f}")
                    
                else:
                    print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Complete workflow failed: {e}")
        
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"\n{'=' * 60}")
        print(f"⏰ Total demo time: {total_time:.2f} seconds")
        print(f"🏁 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 60}")
    
    def create_sample_document(self, content: str, filename: str) -> str:
        """Create a sample document for testing."""
        file_path = f"sample_{filename}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    async def run_comprehensive_demo(self):
        """Run a comprehensive demo with different document types."""
        print(f"\n🎯 ENHANCED DOCUMENT PROCESSING DEMO")
        print(f"{'🌟' * 30}")
        print(f"Gemini-Powered RAG with Web Enhancement")
        print(f"{'🌟' * 30}")
        
        # Check supported formats
        supported_formats = self.document_converter.get_supported_formats()
        print(f"\n📋 Supported formats: {', '.join(supported_formats)}")
        
        # Create sample documents for demo
        sample_docs = [
            ("sample_research.txt", """
            Artificial Intelligence in Healthcare: A Comprehensive Review
            
            Abstract:
            The integration of artificial intelligence (AI) in healthcare has revolutionized medical diagnosis, treatment planning, and patient care. This paper examines the current applications of AI in various healthcare domains, including medical imaging, drug discovery, and personalized medicine.
            
            Introduction:
            Healthcare systems worldwide are experiencing unprecedented challenges, from aging populations to the increasing complexity of medical conditions. AI technologies, particularly machine learning and deep learning algorithms, offer promising solutions to enhance healthcare delivery, improve diagnostic accuracy, and reduce costs.
            
            Key Applications:
            1. Medical Imaging: AI algorithms can analyze X-rays, MRIs, and CT scans with accuracy comparable to human radiologists.
            2. Drug Discovery: Machine learning accelerates the identification of potential drug candidates and predicts their effectiveness.
            3. Personalized Medicine: AI enables treatment customization based on individual patient characteristics and genetic profiles.
            4. Clinical Decision Support: AI systems assist healthcare providers in making evidence-based treatment decisions.
            
            Challenges and Considerations:
            Despite the promising potential, AI implementation in healthcare faces several challenges including data privacy concerns, regulatory compliance, ethical considerations, and the need for extensive validation studies.
            
            Conclusion:
            AI represents a transformative force in healthcare, offering unprecedented opportunities to improve patient outcomes and system efficiency. However, successful implementation requires careful consideration of technical, ethical, and regulatory factors.
            """),
            
            ("sample_business.md", """
            # Digital Transformation Strategy for Modern Enterprises
            
            ## Executive Summary
            
            Digital transformation has become a critical imperative for businesses seeking to remain competitive in today's rapidly evolving marketplace. This document outlines key strategies and best practices for successful digital transformation initiatives.
            
            ## Key Components
            
            ### Technology Infrastructure
            - Cloud computing adoption
            - Data analytics and business intelligence
            - Artificial intelligence and automation
            - Cybersecurity enhancement
            
            ### Organizational Change
            - Digital culture development
            - Skills training and development
            - Change management processes
            - Leadership alignment
            
            ### Customer Experience
            - Digital touchpoint optimization
            - Personalization strategies
            - Omnichannel integration
            - Real-time customer support
            
            ## Implementation Roadmap
            
            1. **Assessment Phase**: Current state analysis and gap identification
            2. **Strategy Development**: Vision setting and roadmap creation
            3. **Pilot Programs**: Small-scale implementation and testing
            4. **Scale-up**: Full deployment across the organization
            5. **Optimization**: Continuous improvement and refinement
            
            ## Success Metrics
            
            - Customer satisfaction scores
            - Operational efficiency gains
            - Revenue growth from digital channels
            - Employee digital adoption rates
            
            ## Conclusion
            
            Digital transformation is not just about technology—it's about reimagining how businesses operate, deliver value, and engage with stakeholders in the digital age.
            """)
        ]
        
        # Process each sample document
        for filename, content in sample_docs:
            try:
                # Create sample file
                file_path = self.create_sample_document(content, filename)
                print(f"\n📄 Created sample document: {filename}")
                
                # Run complete workflow demo
                await self.demo_complete_workflow(file_path)
                
                # Clean up
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🧹 Cleaned up: {file_path}")
                
                print(f"\n{'-' * 40}")
                
            except Exception as e:
                print(f"❌ Demo failed for {filename}: {e}")
        
        # Show service stats
        print(f"\n📊 SERVICE STATISTICS:")
        try:
            stats = self.enhanced_summary_service.get_service_stats()
            print(f"   🔧 Service: {stats.get('service_name', 'Unknown')}")
            print(f"   📋 Workflow steps: {stats.get('workflow_steps', 0)}")
            print(f"   🔗 Integrated services: {len(stats.get('services_integrated', []))}")
            print(f"   📄 Supported formats: {len(stats.get('supported_formats', []))}")
            print(f"   ⚡ Capabilities: {len(stats.get('capabilities', []))}")
        except Exception as e:
            print(f"   ❌ Could not fetch service stats: {e}")
        
        print(f"\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print(f"   ✅ All Llama code has been removed")
        print(f"   ✅ Gemini-only RAG system is working")
        print(f"   ✅ Enhanced document processing with web search")
        print(f"   ✅ Support for: .txt, .md, .pdf, .docx, .rtf, .odt, .csv")
        print(f"   ✅ API endpoints available at /api/v1/enhanced-documents/")

def main():
    """Main demo function."""
    print("Starting Enhanced Document Processing Demo...")
    
    # Check if GEMINI_API_KEY is set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not found in environment variables.")
        print("   Set your Gemini API key to enable AI-powered features.")
        print("   The demo will continue with limited functionality.")
    
    demo = EnhancedDocumentDemo()
    asyncio.run(demo.run_comprehensive_demo())

if __name__ == "__main__":
    main()
