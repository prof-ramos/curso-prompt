# Developer Tools for Prompt Course

This directory contains developer tools to assist with managing the prompt course content.

## Python Scraper

A Python script using the FireCrawl API is included to scrape documentation pages from the links provided in the main README and save them as Markdown files, organized by tool.

### Setup

1.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set up environment variables:**
    Create a `.env` file in this directory with your FireCrawl API key:
    ```
    FIRECRAWL_API_KEY=your_api_key_here
    ```

### Usage

1.  Ensure you have a `.env` file with your `FIRECRAWL_API_KEY`.
2.  Run the scraper script:
    ```bash
    python scrape_docs.py
    ```
    This will read the links from the main `README.md`, scrape the content, and save it in the `scraped_docs` subdirectory, organized by tool name.

### Adding New Links

To add new documentation links to be scraped:

1.  Add the link to the appropriate section in the main `../README.md` file.
2.  Re-run the `scrape_docs.py` script. It will automatically discover and scrape the new link.

A new link was recently added for **Gemini-CLI**: `https://goo.gle/gemini-cli-docs-mcp`.