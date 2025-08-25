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
    
    async def search_duckduckgo_html(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search using DuckDuckGo HTML scraping for better results"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use DuckDuckGo lite search
                search_url = "https://lite.duckduckgo.com/lite/"
                
                params = {
                    'q': query,
                    'kl': 'us-en'
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Simple HTML parsing to extract search results
                        results = []
                        import re
                        
                        # Look for result patterns in the HTML
                        # This is a basic pattern - you might need to adjust based on actual HTML structure
                        url_pattern = r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
                        matches = re.findall(url_pattern, html_content)
                        
                        for i, (url, title) in enumerate(matches[:max_results]):
                            if url.startswith('http') and 'duckduckgo' not in url:
                                results.append({
                                    'title': title.strip()[:100],
                                    'url': url,
                                    'description': f'Search result for "{query}"',
                                    'source': 'DuckDuckGo Search'
                                })
                        
                        return results
                    
                    return []
        except Exception as e:
            print(f"DuckDuckGo HTML search error: {str(e)}")
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
    
    def get_specialized_urls(self, keywords: List[str], content: str) -> List[Dict[str, str]]:
        """Get specialized URLs based on content domain and keywords"""
        urls = []
        
        # Detect content domain
        nlp_terms = ['nlp', 'natural language processing', 'text mining', 'sentiment analysis', 'tokenization', 'word embedding', 'transformer']
        ai_ml_terms = ['machine learning', 'artificial intelligence', 'deep learning', 'neural network', 'classification', 'regression']
        data_science_terms = ['data science', 'data analysis', 'statistics', 'visualization', 'pandas', 'numpy']
        programming_terms = ['python', 'programming', 'algorithm', 'code', 'software']
        
        content_lower = content.lower()
        
        # Specialized resources based on content type
        if any(term in content_lower for term in nlp_terms):
            # NLP-specific resources
            specialized_sites = {
                "papers_with_code_nlp": f"https://paperswithcode.com/search?q={quote_plus(' '.join(keywords[:2]))}",
                "huggingface": f"https://huggingface.co/models?search={quote_plus(' '.join(keywords[:2]))}",
                "nltk_book": "https://www.nltk.org/book/",
                "spacy_docs": "https://spacy.io/",
                "stanford_nlp": "https://stanfordnlp.github.io/stanza/"
            }
            
            for site_name, url in specialized_sites.items():
                title = f"{' '.join(keywords[:2]).title()} - {site_name.replace('_', ' ').title()}"
                description = f"NLP resources and tools for {' '.join(keywords[:2])}"
                urls.append({
                    'title': title,
                    'url': url,
                    'description': description,
                    'source': f'{site_name.replace("_", " ").title()} (NLP Specialized)'
                })
        
        elif any(term in content_lower for term in ai_ml_terms):
            # AI/ML-specific resources
            specialized_sites = {
                "papers_with_code": f"https://paperswithcode.com/search?q={quote_plus(' '.join(keywords[:2]))}",
                "towards_data_science": f"https://towardsdatascience.com/search?q={quote_plus(' '.join(keywords[:2]))}",
                "scikit_learn": "https://scikit-learn.org/stable/",
                "tensorflow": "https://www.tensorflow.org/",
                "pytorch": "https://pytorch.org/"
            }
            
            for site_name, url in specialized_sites.items():
                title = f"{' '.join(keywords[:2]).title()} - {site_name.replace('_', ' ').title()}"
                description = f"Machine learning resources for {' '.join(keywords[:2])}"
                urls.append({
                    'title': title,
                    'url': url,
                    'description': description,
                    'source': f'{site_name.replace("_", " ").title()} (ML Specialized)'
                })
        
        elif any(term in content_lower for term in data_science_terms):
            # Data Science resources
            specialized_sites = {
                "kaggle": f"https://www.kaggle.com/search?q={quote_plus(' '.join(keywords[:2]))}",
                "towards_data_science": f"https://towardsdatascience.com/search?q={quote_plus(' '.join(keywords[:2]))}",
                "pandas_docs": "https://pandas.pydata.org/docs/",
                "matplotlib": "https://matplotlib.org/",
                "seaborn": "https://seaborn.pydata.org/"
            }
            
            for site_name, url in specialized_sites.items():
                title = f"{' '.join(keywords[:2]).title()} - {site_name.replace('_', ' ').title()}"
                description = f"Data science resources for {' '.join(keywords[:2])}"
                urls.append({
                    'title': title,
                    'url': url,
                    'description': description,
                    'source': f'{site_name.replace("_", " ").title()} (Data Science)'
                })
        
        elif any(term in content_lower for term in programming_terms):
            # Programming resources
            specialized_sites = {
                "github": f"https://github.com/search?q={quote_plus(' '.join(keywords[:2]))}",
                "stack_overflow": f"https://stackoverflow.com/search?q={quote_plus(' '.join(keywords[:2]))}",
                "python_docs": "https://docs.python.org/3/",
                "real_python": f"https://realpython.com/search/?q={quote_plus(' '.join(keywords[:2]))}"
            }
            
            for site_name, url in specialized_sites.items():
                title = f"{' '.join(keywords[:2]).title()} - {site_name.replace('_', ' ').title()}"
                description = f"Programming resources for {' '.join(keywords[:2])}"
                urls.append({
                    'title': title,
                    'url': url,
                    'description': description,
                    'source': f'{site_name.replace("_", " ").title()} (Programming)'
                })
        
        # Always add some general academic resources
        general_academic = {
            "arxiv": f"https://arxiv.org/search/?query={quote_plus(' '.join(keywords[:3]))}&searchtype=all",
            "google_scholar": f"https://scholar.google.com/scholar?q={quote_plus(' '.join(keywords[:3]))}",
            "wikipedia": f"https://en.wikipedia.org/wiki/{quote_plus(keywords[0])}" if keywords else "https://en.wikipedia.org"
        }
        
        for site_name, url in general_academic.items():
            title = f"{' '.join(keywords[:2]).title()} - {site_name.replace('_', ' ').title()}"
            description = f"Academic resources about {' '.join(keywords[:2])}"
            urls.append({
                'title': title,
                'url': url,
                'description': description,
                'source': f'{site_name.replace("_", " ").title()} (Academic)'
            })
        
        return urls[:8]  # Return top 8 specialized URLs
    
    def get_ai_powered_specialized_urls(self, ai_categories: Dict[str, Any], keywords: List[str]) -> List[Dict[str, str]]:
        """Get specialized URLs based on AI-generated categories"""
        urls = []
        
        try:
            # Extract categories from AI response
            primary_domains = ai_categories.get('primary_domains', [])
            topics = ai_categories.get('topics', [])
            search_terms = ai_categories.get('search_terms', [])
            tools_technologies = ai_categories.get('tools_technologies', [])
            academic_fields = ai_categories.get('academic_fields', [])
            
            # Use AI-generated search terms if available, otherwise fallback to keywords
            effective_terms = search_terms[:3] if search_terms else keywords[:3]
            
            # Domain-specific resource mapping
            domain_resources = {
                'artificial_intelligence': {
                    'papers_with_code': f"https://paperswithcode.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'towards_data_science': f"https://towardsdatascience.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'ai_news': 'https://www.artificialintelligence-news.com/',
                    'openai_blog': 'https://openai.com/blog/',
                    'deepmind_blog': 'https://deepmind.com/blog'
                },
                'machine_learning': {
                    'papers_with_code': f"https://paperswithcode.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'scikit_learn': 'https://scikit-learn.org/stable/',
                    'tensorflow': 'https://www.tensorflow.org/',
                    'pytorch': 'https://pytorch.org/',
                    'kaggle': f"https://www.kaggle.com/search?q={quote_plus(' '.join(effective_terms))}"
                },
                'natural_language_processing': {
                    'huggingface': f"https://huggingface.co/models?search={quote_plus(' '.join(effective_terms))}",
                    'nltk_book': 'https://www.nltk.org/book/',
                    'spacy_docs': 'https://spacy.io/',
                    'stanford_nlp': 'https://stanfordnlp.github.io/stanza/',
                    'papers_with_code_nlp': f"https://paperswithcode.com/search?q={quote_plus(' '.join(effective_terms))}"
                },
                'data_science': {
                    'kaggle': f"https://www.kaggle.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'towards_data_science': f"https://towardsdatascience.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'pandas_docs': 'https://pandas.pydata.org/docs/',
                    'numpy_docs': 'https://numpy.org/doc/',
                    'matplotlib': 'https://matplotlib.org/'
                },
                'software_engineering': {
                    'github': f"https://github.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'stack_overflow': f"https://stackoverflow.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'medium_programming': f"https://medium.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'dev_community': f"https://dev.to/search?q={quote_plus(' '.join(effective_terms))}"
                },
                'cybersecurity': {
                    'owasp': 'https://owasp.org/',
                    'nist_cybersecurity': 'https://www.nist.gov/cyberframework',
                    'sans_institute': 'https://www.sans.org/',
                    'krebs_security': 'https://krebsonsecurity.com/'
                },
                'finance': {
                    'investopedia': f"https://www.investopedia.com/search?q={quote_plus(' '.join(effective_terms))}",
                    'morningstar': 'https://www.morningstar.com/',
                    'sec_gov': 'https://www.sec.gov/',
                    'yahoo_finance': f"https://finance.yahoo.com/quote/{effective_terms[0] if effective_terms else 'SPY'}"
                },
                'healthcare': {
                    'pubmed': f"https://pubmed.ncbi.nlm.nih.gov/?term={quote_plus(' '.join(effective_terms))}",
                    'who': 'https://www.who.int/',
                    'cdc': 'https://www.cdc.gov/',
                    'nih': 'https://www.nih.gov/'
                },
                'blockchain': {
                    'coindesk': 'https://www.coindesk.com/',
                    'ethereum_docs': 'https://ethereum.org/en/developers/docs/',
                    'blockchain_info': 'https://www.blockchain.com/',
                    'github_crypto': f"https://github.com/search?q={quote_plus(' '.join(effective_terms) + ' blockchain')}"
                }
            }
            
            # Add URLs based on identified domains
            for domain in primary_domains:
                domain_key = domain.lower().replace(' ', '_')
                if domain_key in domain_resources:
                    resources = domain_resources[domain_key]
                    for resource_name, resource_url in resources.items():
                        title = f"{domain.replace('_', ' ').title()} - {resource_name.replace('_', ' ').title()}"
                        description = f"Specialized {domain.replace('_', ' ')} resources and tools"
                        urls.append({
                            'title': title,
                            'url': resource_url,
                            'description': description,
                            'source': f'{resource_name.replace("_", " ").title()} (AI-Categorized)'
                        })
            
            # Add academic resources based on identified fields
            for field in academic_fields:
                field_query = quote_plus(f"{field} {' '.join(effective_terms[:2])}")
                academic_resources = {
                    'google_scholar': f"https://scholar.google.com/scholar?q={field_query}",
                    'arxiv': f"https://arxiv.org/search/?query={field_query}&searchtype=all",
                    'researchgate': f"https://www.researchgate.net/search?q={field_query}"
                }
                
                for resource_name, resource_url in academic_resources.items():
                    title = f"{field.title()} Research - {resource_name.replace('_', ' ').title()}"
                    description = f"Academic resources for {field} research"
                    urls.append({
                        'title': title,
                        'url': resource_url,
                        'description': description,
                        'source': f'{resource_name.replace("_", " ").title()} (Academic)'
                    })
            
            # Add tool-specific resources
            for tool in tools_technologies:
                tool_query = quote_plus(f"{tool} documentation tutorial")
                tool_resources = {
                    'official_docs': f"https://www.google.com/search?q={tool_query}+site:docs",
                    'github_search': f"https://github.com/search?q={quote_plus(tool)}",
                    'stack_overflow': f"https://stackoverflow.com/search?q={quote_plus(tool)}"
                }
                
                for resource_name, resource_url in tool_resources.items():
                    title = f"{tool.title()} - {resource_name.replace('_', ' ').title()}"
                    description = f"Resources and documentation for {tool}"
                    urls.append({
                        'title': title,
                        'url': resource_url,
                        'description': description,
                        'source': f'{resource_name.replace("_", " ").title()} (Tool-Specific)'
                    })
            
            # Always add some general academic resources with AI terms
            if effective_terms:
                general_query = quote_plus(' '.join(effective_terms[:3]))
                general_academic = {
                    'arxiv': f"https://arxiv.org/search/?query={general_query}&searchtype=all",
                    'google_scholar': f"https://scholar.google.com/scholar?q={general_query}",
                    'wikipedia': f"https://en.wikipedia.org/wiki/{quote_plus(effective_terms[0])}"
                }
                
                for site_name, url in general_academic.items():
                    title = f"{' '.join(effective_terms[:2]).title()} - {site_name.replace('_', ' ').title()}"
                    description = f"Academic resources about {' '.join(effective_terms[:2])}"
                    urls.append({
                        'title': title,
                        'url': url,
                        'description': description,
                        'source': f'{site_name.replace("_", " ").title()} (Academic)'
                    })
            
            return urls[:10]  # Return top 10 AI-powered URLs
            
        except Exception as e:
            print(f"Error in AI-powered URL generation: {str(e)}")
            # Fallback to basic approach
            return self.get_specialized_urls(keywords, ' '.join(topics) if topics else '')
    
    async def find_relevant_urls(self, content: str, extracted_data: Dict[str, Any], max_urls: int = 10, ai_categories: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
            
            # Add specialized URLs based on AI categories or content domain
            if ai_categories:
                specialized_urls = self.get_ai_powered_specialized_urls(ai_categories, keywords)
            else:
                specialized_urls = self.get_specialized_urls(keywords, content)
            all_results.extend(specialized_urls)
            
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
