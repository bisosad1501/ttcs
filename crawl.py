from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from scrape import scrape_website

def crawl_website(url, max_pages=5):  
    visited = set()
    to_visit = [url]
    crawled_data = []
    page_count = 0  # Initialize page count

    def fetch_url(current_url):
        try:
            html_content = scrape_website(current_url)
            return html_content, current_url
        except Exception as e:
            print(f"Có lỗi xảy ra khi crawl {current_url}: {e}")
            return None

    while to_visit and page_count < max_pages:  # Check page count condition
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_url, current_url): current_url for current_url in to_visit}
            to_visit = []  # Reset to_visit for the next crawl
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    content, page_url = result
                    crawled_data.append((content, page_url))
                    visited.add(page_url)
                    page_count += 1  # Increment page count

                    if page_count >= max_pages:  # Check again after incrementing
                        break

                    # Use BeautifulSoup to find new links
                    soup = BeautifulSoup(content, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        full_link = urljoin(page_url, link['href'])
                        if full_link not in visited and full_link.startswith(url):
                            to_visit.append(full_link)

    return crawled_data
