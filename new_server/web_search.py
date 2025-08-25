import os
import asyncio
import aiohttp
import json
import re
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus, urljoin
from datetime import datetime
import hashlib

class WebSearchEngine:
    def __init__(self):
        """Initialize web search engine with multiple search providers"""
        self.search_engines = {
            "duckduckgo": {
                "url": "https://api.duckduckgo.com/",
                "enabled": True
            },
            "google": {
                "url": "https://www.googleapis.com/customsearch/v1",
                "api_key": os.getenv("GOOGLE_SEARCH_API_KEY"),
                "search_engine_id": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
                "enabled": bool(os.getenv("GOOGLE_SEARCH_API_KEY"))
            }
        }
    
    def extract_keywords_from_content(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract relevant keywords from content for search"""
        # Remove common stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
            'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can'
        }
        
        # Extract words and clean them
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Remove stopwords and get word frequency
        word_freq = {}
        for word in words:
            if word not in stopwords and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def generate_search_queries(self, content: str, extracted_data: Dict[str, Any]) -> List[str]:
        """Generate relevant search queries based on content"""
        keywords = self.extract_keywords_from_content(content, max_keywords=5)
        content_type = extracted_data.get("content_type", "")
        
        queries = []
        
        # Primary keyword search
        if keywords:
            primary_query = " ".join(keywords[:3])  # Top 3 keywords
            queries.append(primary_query)
        
        # Content type specific queries
        if content_type == "pdf" or content_type == "docx":
            title_keywords = keywords[:2] if keywords else ["document", "guide"]
            queries.append(" ".join(title_keywords) + " tutorial")
            queries.append(" ".join(title_keywords) + " documentation")
        
        elif content_type == "excel" or content_type == "csv":
            data_keywords = keywords[:2] if keywords else ["data", "analysis"]
            queries.append(" ".join(data_keywords) + " analysis")
            queries.append(" ".join(data_keywords) + " dataset")
        
        elif content_type in ["json", "xml"]:
            queries.append(" ".join(keywords[:2]) + " API documentation")
            queries.append(" ".join(keywords[:2]) + " reference")
        
        # Add general informational queries
        if keywords:
            queries.append(" ".join(keywords[:2]) + " information")
            queries.append(" ".join(keywords[:2]) + " resources")
        
        # Remove duplicates and empty queries
        return list(set([q.strip() for q in queries if q.strip()]))
    
    async def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'q': query,
                    'format': 'json',
                    'no_redirect': '1',
                    'no_html': '1',
                    'skip_disambig': '1'
                }
                
                url = self.search_engines["duckduckgo"]["url"]
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        
                        # Extract from RelatedTopics
                        for topic in data.get('RelatedTopics', [])[:max_results]:
                            if isinstance(topic, dict) and 'FirstURL' in topic:
                                results.append({
                                    'title': topic.get('Text', '').split(' - ')[0][:100],
                                    'url': topic.get('FirstURL', ''),
                                    'description': topic.get('Text', '')[:200],
                                    'source': 'DuckDuckGo'
                                })
                        
                        # Extract from Results if RelatedTopics is empty
                        if not results:
                            for result in data.get('Results', [])[:max_results]:
                                if isinstance(result, dict) and 'FirstURL' in result:
                                    results.append({
                                        'title': result.get('Text', '').split(' - ')[0][:100],
                                        'url': result.get('FirstURL', ''),
                                        'description': result.get('Text', '')[:200],
                                        'source': 'DuckDuckGo'
                                    })
                        
                        return results
                    
                    return []
        except Exception as e:
            print(f"DuckDuckGo search error: {str(e)}")
            return []
    
    async def search_google(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search using Google Custom Search API (if available)"""
        if not self.search_engines["google"]["enabled"]:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': self.search_engines["google"]["api_key"],
                    'cx': self.search_engines["google"]["search_engine_id"],
                    'q': query,
                    'num': min(max_results, 10)
                }
                
                url = self.search_engines["google"]["url"]
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for item in data.get('items', [])[:max_results]:
                            results.append({
                                'title': item.get('title', '')[:100],
                                'url': item.get('link', ''),
                                'description': item.get('snippet', '')[:200],
                                'source': 'Google'
                            })
                        
                        return results
                    
                    return []
        except Exception as e:
            print(f"Google search error: {str(e)}")
            return []
    
    def get_educational_urls(self, keywords: List[str]) -> List[Dict[str, str]]:
        """Get educational and reference URLs based on keywords"""
        educational_sites = {
            "wikipedia": "https://en.wikipedia.org/wiki/",
            "investopedia": "https://www.investopedia.com/search?q=",
            "khan_academy": "https://www.khanacademy.org/search?page_search_query=",
            "coursera": "https://www.coursera.org/search?query=",
            "edx": "https://www.edx.org/search?q="
        }
        
        urls = []
        for keyword in keywords[:3]:  # Top 3 keywords
            for site_name, base_url in educational_sites.items():
                url = base_url + quote_plus(keyword)
                urls.append({
                    'title': f"{keyword.title()} - {site_name.replace('_', ' ').title()}",
                    'url': url,
                    'description': f"Educational content about {keyword} from {site_name.replace('_', ' ').title()}",
                    'source': f"{site_name.replace('_', ' ').title()} (Educational)"
                })
        
        return urls[:5]  # Return top 5 educational URLs
    
    async def find_relevant_urls(self, content: str, extracted_data: Dict[str, Any], max_urls: int = 10) -> Dict[str, Any]:
        """Main function to find relevant URLs for content"""
        try:
            # Generate search queries
            queries = self.generate_search_queries(content, extracted_data)
            keywords = self.extract_keywords_from_content(content)
            
            all_results = []
            
            # Search with each query
            for query in queries[:3]:  # Limit to top 3 queries to avoid too many API calls
                # Try DuckDuckGo first
                ddg_results = await self.search_duckduckgo(query, max_results=3)
                all_results.extend(ddg_results)
                
                # Try Google if available
                if self.search_engines["google"]["enabled"]:
                    google_results = await self.search_google(query, max_results=3)
                    all_results.extend(google_results)
                
                # Small delay between searches to be respectful
                await asyncio.sleep(0.5)
            
            # Add educational URLs
            educational_urls = self.get_educational_urls(keywords)
            all_results.extend(educational_urls)
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_results = []
            for result in all_results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            
            # Sort by relevance (prioritize educational sources and known domains)
            def get_priority(result):
                source = result.get('source', '').lower()
                url = result.get('url', '').lower()
                
                priority = 0
                if 'educational' in source:
                    priority += 10
                if any(edu_site in url for edu_site in ['wikipedia', 'khan', 'coursera', 'edx', 'mit.edu', 'stanford.edu']):
                    priority += 8
                if any(reliable_site in url for reliable_site in ['.edu', '.gov', '.org']):
                    priority += 5
                
                return priority
            
            unique_results.sort(key=get_priority, reverse=True)
            
            return {
                "related_urls": unique_results[:max_urls],
                "search_metadata": {
                    "queries_used": queries,
                    "keywords_extracted": keywords,
                    "total_results_found": len(all_results),
                    "unique_results": len(unique_results),
                    "search_timestamp": datetime.now().isoformat()
                },
                "search_summary": self._generate_search_summary(queries, unique_results[:max_urls])
            }
        
        except Exception as e:
            return {
                "related_urls": [],
                "error": f"Web search failed: {str(e)}",
                "search_metadata": {
                    "search_timestamp": datetime.now().isoformat()
                }
            }
    
    def _generate_search_summary(self, queries: List[str], results: List[Dict[str, str]]) -> str:
        """Generate a summary of the search results"""
        if not results:
            return "No relevant web resources found for the content."
        
        summary_parts = [
            f"Found {len(results)} relevant web resources based on the content analysis.",
            f"Search queries used: {', '.join(queries[:3])}",
            f"Sources include: {', '.join(set(result.get('source', 'Unknown') for result in results[:5]))}"
        ]
        
        return " ".join(summary_parts)


# Example usage and testing function
async def test_web_search():
    """Test function for web search functionality"""
    search_engine = WebSearchEngine()
    
    # Test content
    test_content = "Machine learning algorithms and artificial intelligence applications in data science"
    test_extracted_data = {"content_type": "pdf"}
    
    results = await search_engine.find_relevant_urls(test_content, test_extracted_data)
    
    print("Test Results:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    # Run test
    asyncio.run(test_web_search())
