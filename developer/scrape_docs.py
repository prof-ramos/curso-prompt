import os
import asyncio
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import re
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Firecrawl
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
if not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment variables.")

app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

# Directory to save scraped documents
OUTPUT_DIR = "scraped_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_links_from_readme(readme_path="../README.md"):
    """
    Extracts links from the main README.md file.
    Returns a list of tuples: (tool_name, url)
    """
    links = []
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to find markdown links: [text](url)
        # We'll assume the text before the list of links for a tool is the tool name
        # A more robust parser could be used, but this is a simple approach.
        
        # Split content by '###' to get sections (assuming each tool section starts with ###)
        sections = re.split(r'\n(### .+?)\n', content)
        
        # Iterate through sections to find tool names and links
        i = 1 # Start from the first actual section title
        while i < len(sections):
            if sections[i].startswith("### "):
                tool_header = sections[i].strip()
                tool_name = tool_header[4:].strip() # Remove '### '
                # The next item in the list should be the content of the section
                section_content = sections[i+1] if i+1 < len(sections) else ""
                
                # Find all links in the section content
                urls = re.findall(r'$[^]]*$$([^)]+)', section_content)
                for url in urls:
                    links.append((tool_name, url.strip()))
            i += 2 # Move to the next section header
            
    except FileNotFoundError:
        logger.error(f"README file not found at {readme_path}")
    except Exception as e:
        logger.error(f"Error reading README: {e}")
        
    return links

async def scrape_and_save(tool_name, url):
    """
    Scrapes a single URL using Firecrawl and saves it as a Markdown file.
    """
    try:
        logger.info(f"Scraping {url} for {tool_name}")
        
        # Scrape the page
        # Using scrape method for single page content
        scrape_result = app.scrape_url(url, params={'formats': ['markdown']})
        
        if not scrape_result or not scrape_result.get('success'):
            logger.error(f"Failed to scrape {url}")
            return
            
        markdown_content = scrape_result.get('markdown', '')
        if not markdown_content:
            logger.warning(f"No markdown content found for {url}")
            return
            
        # Sanitize tool name for filename
        safe_tool_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', tool_name)
        
        # Create tool-specific directory
        tool_dir = os.path.join(OUTPUT_DIR, safe_tool_name)
        os.makedirs(tool_dir, exist_ok=True)
        
        # Generate a filename based on the URL
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        if path_parts:
            filename = path_parts[-1] + ".md"
        else:
            # Fallback filename if path is empty
            filename = "index.md"
            
        # Sanitize filename
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
        file_path = os.path.join(tool_dir, filename)
        
        # Save the markdown content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        logger.info(f"Saved {file_path}")
        
    except Exception as e:
        logger.error(f"Error scraping {url} for {tool_name}: {e}")

async def main():
    """
    Main function to orchestrate the scraping process.
    """
    logger.info("Starting documentation scraping process...")
    
    # Extract links
    links = extract_links_from_readme()
    if not links:
        logger.warning("No links found to scrape.")
        return
        
    logger.info(f"Found {len(links)} links to scrape.")
    
    # Scrape all links concurrently
    tasks = [scrape_and_save(tool_name, url) for tool_name, url in links]
    await asyncio.gather(*tasks)
    
    logger.info("Documentation scraping process completed.")

if __name__ == "__main__":
    asyncio.run(main())