import asyncio
from playwright.async_api import async_playwright, TimeoutError
import json
import fnmatch
from urllib.parse import urljoin
from config import Config  # Ensure Config class is properly defined and configured

# Function to get the HTML content of a specified page element
async def get_page_html(page, selector):
    try:
        # Wait for the selector to appear, with a maximum wait time of 3 seconds
        await page.wait_for_selector(selector, timeout=3000)
        element = await page.query_selector(selector)
        return await element.inner_text() if element else ""
    except TimeoutError:
        # Return an empty string if the selector times out
        return ""

# Main crawling function
async def crawl(config):
    results = []  # Store results
    queue = [config.url]  # Initialize URL queue
    visited_urls = set()  # Track visited URLs to prevent duplicates
    page_count = 0  # Initialize page counter

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Add a cookie if specified in the configuration
        if config.cookie:
            await page.context.add_cookies([{
                "name": config.cookie['name'],
                "value": config.cookie['value'], "url": config.url}])

        try:
            while queue and len(results) < config.max_pages_to_crawl:
                url = queue.pop(0)
                # Clean the URL to remove the hash and anything after it
                cleaned_url = url.split('#')[0]
                if cleaned_url in visited_urls:
                    continue
                visited_urls.add(cleaned_url)
                page_count += 1  # Increment the page counter each time a new page is visited

                try:
                    # Attempt to access the page, setting a timeout of 3 seconds
                    await page.goto(cleaned_url, timeout=3000)
                    html = await get_page_html(page, config.selector)
                    if html:  # Only add to results if HTML content was successfully retrieved
                        results.append({'url': cleaned_url, 'html': html})
                        print(f"Crawler: Crawling Page {page_count} at {cleaned_url}")
                except TimeoutError:
                    print(f"Timeout while accessing {cleaned_url}")
                    continue

                # Incrementally save results to a file
                with open(config.output_file_name, 'w') as f:
                    json.dump(results, f, indent=2)

                # Extract and clean links from the page
                links = await page.query_selector_all("a")
                for link in links:
                    href = await link.get_attribute("href")
                    if href:
                        full_url = urljoin(cleaned_url, href)
                        # Remove the hash from the URL
                        cleaned_full_url = full_url.split('#')[0]
                        if cleaned_full_url not in visited_urls and fnmatch.fnmatch(cleaned_full_url, config.match):
                            queue.append(cleaned_full_url)

        finally:
            # Ensure the browser is closed after crawling
            await browser.close()

    return results

# Main function to initiate the crawling process
async def main(config):
    results = await crawl(config)
    with open(config.output_file_name, 'w') as f:
        json.dump(results, f, indent=2)

# Running the main function
if __name__ == "__main__":
    config = Config(
        url="https://getbootstrap.com/docs/5.3/getting-started/introduction/",
        match="https://getbootstrap.com/docs/5.3/getting-started/**",
        selector="body",
        max_pages_to_crawl=100,
        output_file_name="output.json"
    )
    asyncio.run(main(config))
