import requests
from bs4 import BeautifulSoup
import os
import re

# Global variables to store visited links and page titles
visited_links = set()
visited_titles = set()

# Function to sanitize file names
def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Function to scrape data from the website recursively
def scrape_iitkgp_website(url, output_dir):
    global visited_links, visited_titles
    
    # Check if the URL has already been visited
    if not isinstance(url, str):
        print("Invalid URL format.")
        return

    if url in visited_links:
        # print(f"Skipping {url} as it's already scraped.")
        return

    print(f"Scraping {url}...")
    try:
        # Send a GET request to the URL with a timeout of 15 seconds
        response = requests.get(url, timeout=15)
    except Exception as e:
        print(f"Failed to retrieve data from {url}: {e}")
        return

    # Check if request was successful (status code 200)
    if response.status_code == 200:
        print(f"Successfully retrieved data from {url}.")
        # Add the URL to visited links
        visited_links.add(url)

        # Parse HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract page title
        page_title = sanitize_filename(url.split('/')[-1].split('.')[0])
        if page_title is not None and isinstance(page_title, str):
            page_title = page_title.strip()
        else:
            page_title = "Untitled Page"

        # Check if the page title has already been visited
        if not isinstance(page_title, str):
            print("Invalid page title format.")
            return

        if page_title in visited_titles:
            # print(f"Skipping {page_title} as it's already scraped.")
            return
        else:
            visited_titles.add(page_title)

        # Extract text from the page
        page_text = ""
        for element in soup.find_all(text=True):
            if isinstance(element, str) and element.parent is not None and element.parent.name not in ['script', 'style', 'meta', 'head', 'title']:
                page_text += '\n' + element.strip()

        # Sanitize page name for file name
        page_name = sanitize_filename(url.split('/')[-1].split('.')[0])

        # Save the text to a text file
        output_file = os.path.join(output_dir, f"{page_name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(page_text.strip())
        print(f"Saved data from {url} to {output_file}.")

        # Find all links on the page and scrape them recursively
        links = soup.find_all('a', href=True)
        for link in links:
            next_page_url = link['href']
            if isinstance(next_page_url, str) and 'iitkgp.ac.in' in next_page_url and 'ernet' not in next_page_url and 'erp' not in next_page_url and 'linkedin' not in next_page_url:  # Check if URL contains 'iitkgp' and does not contain 'erp'
                # Check if URL contains any disallowed extensions
                disallowed_extensions = ['.rar', '.png', '.pdf', '.jpg', '.jpeg', '.gif', '.svg', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.mp3', '.mp4', '.avi', '.mov', '.exe', '.zip', '.php', 'library.iitkgp.ac.in', '.webm', 'mailto:']
                skip_url = any(ext in next_page_url.lower() for ext in disallowed_extensions)
                if not skip_url:
                    if next_page_url.startswith('http'):
                        scrape_iitkgp_website(next_page_url, output_dir)
                    else:
                        next_page_url = url + next_page_url
                        scrape_iitkgp_website(next_page_url, output_dir)
                else:
                    continue
                    # print(f"Skipping URL with disallowed extension: {next_page_url}")
            else:
                continue
                # print(f"Skipping non-IIT KGP or ERP link: {next_page_url}")

        print(f"Finished processing {url}.")  # Print message after processing all links

    else:
        print(f"Failed to retrieve data from {url}.")

# Define the URL of the website to scrape
starting_url = "https://www.iitkgp.ac.in/sitemap"

# Define the directory to save output files
output_directory = "data/iit-kgp/"

# Create output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Call the function to scrape the website recursively
scrape_iitkgp_website(starting_url, output_directory)
