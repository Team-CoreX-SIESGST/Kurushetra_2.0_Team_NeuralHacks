"""
Web search service for OmniSearch AI.
Fetches additional information from the web to enrich search results.
"""

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin, quote
import json
import requests
from app.settings import settings

class WebSearchService:
    """Service for fetching and processing web content."""
    
    def __init__(self):
        self.session = None
        self.max_concurrent_requests = 5
        self.timeout = 10
        self.max_content_length = 10000  # Max characters to extract
    
    async def initialize(self):
        """Initialize the HTTP session."""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=self.max_concurrent_requests)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for relevant information."""
        try:
            await self.initialize()
            
            # For demo purposes, we'll use a simple approach
            # In production, you might want to integrate with search APIs like Google, Bing, etc.
            
            # Simulate web search results
            search_results = await self._simulate_web_search(query, max_results)
            
            # Fetch content for each result
            enriched_results = await self._fetch_web_content(search_results)
            
            return enriched_results
            
        except Exception as e:
            print(f"Web search failed: {e}")
            return []
    
    async def _simulate_web_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Simulate web search results for demonstration."""
        # This is a placeholder - in production, integrate with actual search APIs
        base_urls = [
            "https://example.com",
            "https://wikipedia.org",
            "https://stackoverflow.com",
            "https://github.com",
            "https://docs.python.org"
        ]
        
        results = []
        for i in range(min(max_results, len(base_urls))):
            results.append({
                'url': base_urls[i],
                'title': f"Result {i+1} for: {query}",
                'snippet': f"This is a simulated search result for the query: {query}",
                'rank': i + 1
            })
        
        return results
    
    async def _fetch_web_content(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fetch content from web URLs."""
        try:
            tasks = []
            for result in search_results:
                task = self._fetch_single_url(result)
                tasks.append(task)
            
            # Execute requests with concurrency limit
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            async def limited_fetch(task):
                async with semaphore:
                    return await task
            
            limited_tasks = [limited_fetch(task) for task in tasks]
            results = await asyncio.gather(*limited_tasks, return_exceptions=True)
            
            # Process results
            enriched_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Failed to fetch {search_results[i]['url']}: {result}")
                    # Add result with error info
                    enriched_results.append({
                        **search_results[i],
                        'content': '',
                        'error': str(result),
                        'status': 'error'
                    })
                else:
                    enriched_results.append(result)
            
            return enriched_results
            
        except Exception as e:
            print(f"Web content fetching failed: {e}")
            return search_results
    
    async def _fetch_single_url(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch content from a single URL."""
        try:
            url = result['url']
            
            # Skip certain URL types
            if self._should_skip_url(url):
                return {
                    **result,
                    'content': '',
                    'status': 'skipped'
                }
            
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'text/html' in content_type:
                        html_content = await response.text()
                        extracted_content = self._extract_text_from_html(html_content)
                        
                        return {
                            **result,
                            'content': extracted_content,
                            'status': 'success',
                            'content_type': 'html'
                        }
                    elif 'text/plain' in content_type:
                        text_content = await response.text()
                        return {
                            **result,
                            'content': text_content[:self.max_content_length],
                            'status': 'success',
                            'content_type': 'text'
                        }
                    else:
                        return {
                            **result,
                            'content': '',
                            'status': 'unsupported_content_type',
                            'content_type': content_type
                        }
                else:
                    return {
                        **result,
                        'content': '',
                        'status': f'http_error_{response.status}'
                    }
                    
        except Exception as e:
            return {
                **result,
                'content': '',
                'error': str(e),
                'status': 'fetch_error'
            }
    
    def _should_skip_url(self, url: str) -> bool:
        """Check if URL should be skipped."""
        parsed = urlparse(url)
        
        # Skip certain domains or file types
        skip_domains = ['localhost', '127.0.0.1', '0.0.0.0']
        skip_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar.gz']
        
        if parsed.hostname in skip_domains:
            return True
        
        if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
            return True
        
        return False
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + "..."
            
            return text
            
        except Exception as e:
            print(f"HTML text extraction failed: {e}")
            return ""
    
    async def enrich_search_results(self, query: str, existing_results: List[Dict[str, Any]], include_web: bool = True) -> List[Dict[str, Any]]:
        """Enrich existing search results with web content."""
        if not include_web:
            return existing_results
        
        try:
            # Get web search results
            web_results = await self.search_web(query, max_results=3)
            
            # Combine with existing results
            enriched_results = existing_results.copy()
            
            for web_result in web_results:
                if web_result.get('status') == 'success' and web_result.get('content'):
                    enriched_results.append({
                        'id': f"web_{web_result['rank']}",
                        'text': web_result['content'][:500],  # Limit content length
                        'source': 'web',
                        'url': web_result['url'],
                        'title': web_result['title'],
                        'score': 0.7,  # Default web result score
                        'file_id': None,
                        'filename': web_result['title'],
                        'page': None
                    })
            
            return enriched_results
            
        except Exception as e:
            print(f"Result enrichment failed: {e}")
            return existing_results
    
    async def search_by_tags(self, tags: List[str], max_results_per_tag: int = 3) -> Dict[str, Any]:
        """Search the web using multiple tags and return relevant website URLs."""
        try:
            all_urls = []
            search_results = []
            
            for tag in tags:
                try:
                    # Search for each tag
                    tag_results = await self._search_real_web(tag, max_results_per_tag)
                    
                    for result in tag_results:
                        url_info = {
                            'url': result['url'],
                            'title': result['title'],
                            'snippet': result['snippet'],
                            'search_tag': tag,
                            'relevance_score': result.get('score', 0.5)
                        }
                        all_urls.append(url_info)
                        search_results.append(result)
                        
                except Exception as e:
                    print(f"Search failed for tag '{tag}': {e}")
                    continue
            
            # Remove duplicates based on URL
            unique_urls = []
            seen_urls = set()
            for url_info in all_urls:
                if url_info['url'] not in seen_urls:
                    unique_urls.append(url_info)
                    seen_urls.add(url_info['url'])
            
            return {
                'website_urls': unique_urls,
                'total_urls': len(unique_urls),
                'search_tags': tags,
                'search_results': search_results
            }
            
        except Exception as e:
            print(f"Tag-based search failed: {e}")
            return {
                'website_urls': [],
                'total_urls': 0,
                'search_tags': tags,
                'search_results': [],
                'error': str(e)
            }
    
    async def _search_real_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform actual web search using available APIs or fallback to simulation."""
        try:
            # Try to use a real search API if available
            # For now, we'll use DuckDuckGo as it doesn't require API key
            return await self._search_duckduckgo(query, max_results)
            
        except Exception as e:
            print(f"Real web search failed, using simulation: {e}")
            # Fallback to simulation
            return await self._simulate_enhanced_web_search(query, max_results)
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo (no API key required)."""
        try:
            await self.initialize()
            
            # DuckDuckGo instant answer API (limited but free)
            search_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    # Extract results from DuckDuckGo response
                    if data.get('RelatedTopics'):
                        for i, topic in enumerate(data['RelatedTopics'][:max_results]):
                            if isinstance(topic, dict) and 'FirstURL' in topic:
                                results.append({
                                    'url': topic['FirstURL'],
                                    'title': topic.get('Text', '').split(' - ')[0] if topic.get('Text') else f'Result for {query}',
                                    'snippet': topic.get('Text', ''),
                                    'rank': i + 1,
                                    'score': 0.8 - (i * 0.1)  # Decreasing relevance score
                                })
                    
                    # If no related topics, create a generic result
                    if not results:
                        results.append({
                            'url': f'https://duckduckgo.com/?q={quote(query)}',
                            'title': f'Search results for: {query}',
                            'snippet': f'DuckDuckGo search results for {query}',
                            'rank': 1,
                            'score': 0.7
                        })
                    
                    return results
            
            # Fallback if DuckDuckGo fails
            return await self._simulate_enhanced_web_search(query, max_results)
            
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return await self._simulate_enhanced_web_search(query, max_results)
    
    async def _simulate_enhanced_web_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Enhanced simulation with more realistic URLs based on query."""
        # Create more realistic URLs based on the query
        query_lower = query.lower()
        results = []
        
        # Technology/programming related
        if any(term in query_lower for term in ['programming', 'code', 'software', 'python', 'javascript', 'api']):
            base_urls = [
                f'https://stackoverflow.com/questions/tagged/{query.replace(" ", "-")}',
                f'https://docs.python.org/3/search.html?q={quote(query)}',
                f'https://developer.mozilla.org/en-US/search?q={quote(query)}',
                f'https://github.com/search?q={quote(query)}',
                f'https://medium.com/tag/{query.replace(" ", "-")}/latest'
            ]
        # Academic/research related
        elif any(term in query_lower for term in ['research', 'study', 'analysis', 'paper', 'academic']):
            base_urls = [
                f'https://scholar.google.com/scholar?q={quote(query)}',
                f'https://www.researchgate.net/search?q={quote(query)}',
                f'https://arxiv.org/search/?query={quote(query)}',
                f'https://www.nature.com/search?q={quote(query)}',
                f'https://www.ncbi.nlm.nih.gov/pubmed/?term={quote(query)}'
            ]
        # News/general information
        else:
            base_urls = [
                f'https://en.wikipedia.org/wiki/Special:Search/{quote(query)}',
                f'https://www.bbc.com/search?q={quote(query)}',
                f'https://www.reuters.com/search/news?blob={quote(query)}',
                f'https://www.britannica.com/search?query={quote(query)}',
                f'https://www.nationalgeographic.com/search?q={quote(query)}'
            ]
        
        for i, url in enumerate(base_urls[:max_results]):
            results.append({
                'url': url,
                'title': f'Results for "{query}" - {url.split("//")[1].split("/")[0]}',
                'snippet': f'Relevant information about {query} from {url.split("//")[1].split("/")[0]}',
                'rank': i + 1,
                'score': 0.9 - (i * 0.15)  # Decreasing relevance score
            })
        
        return results
    
    def get_web_stats(self) -> Dict[str, Any]:
        """Get statistics about web search operations."""
        return {
            "max_concurrent_requests": self.max_concurrent_requests,
            "timeout": self.timeout,
            "max_content_length": self.max_content_length,
            "session_active": self.session is not None
        }
