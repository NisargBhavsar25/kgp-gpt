import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re

visited_urls = set()
visited_titles = set()
base_url = "https://wiki.metakgp.org"

# Function to sanitize filename
def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Function to check if a URL has already been visited
def is_visited_url(url, visited_urls):
    return url in visited_urls

# Function to fetch webpage content
def fetch_webpage_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    return None

# Function to extract title from webpage
def extract_title(soup):
    title_tag = soup.find('h1')
    return title_tag.text.strip() if title_tag else None

# Function to extract content from webpage
def extract_content(soup):
    content_div = soup.find('div', class_='mw-parser-output')
    return content_div.get_text() if content_div else None

# Function to check if the title contains "User"
def is_user_title(title):
    return ("User" in title) or ("Template" in title)

# Function to process a page and scrape its content
def process_page(url, output_dir):
    visited_urls.add(url)
    soup = fetch_webpage_content(url)
    if not soup:
        print(f"Failed to fetch content for URL: {url}")
        return

    title = extract_title(soup)

    if not title:
        print(f"Title not found for URL: {url}")
        return
    
    if is_user_title(title):
        print(f"Skipping page with 'User' in the title: {url}")
        return
    
    if title in visited_titles:
        print(f"Skipping already visited page: {url}")
        return    
    
    visited_titles.add(title)


    content = extract_content(soup)
    if not content:
        print(f"No content found for URL: {url}")
        return

    title = sanitize_filename(title)
    output_filename = os.path.join(output_dir, f"{title}.txt")
    with open(output_filename, "w", encoding="utf-8") as text_file:
        text_file.write(content)
    print(f"Scraped and saved: {title}.txt")

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith("/") and not any((ext in href) for ext in ['jpg', 'jpeg', 'png', 'gif', "File:", "Template", "&action=edit", "Special:", "User", "action=history", "veaction=edit", "oldid=", "action=info"]) and href not in visited_urls:
            new_url = urljoin(url, href)
            if not is_visited_url(new_url, visited_urls) and base_url in new_url:
                process_page(new_url, output_dir)

# Function to scrape a webpage and create a text file
def scrape_and_create_text_file(url, output_dir):
    if is_visited_url(url, visited_urls):
        return

    process_page(url, output_dir)

# Main function
def main():
    start_url = base_url + "/w/Main_Page"
    output_dir = "data/meta-kgp"  # Output directory for text files

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    scrape_and_create_text_file(start_url, output_dir)

if __name__ == "__main__":
    main()
