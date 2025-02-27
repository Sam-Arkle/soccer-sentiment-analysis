# For scraping the comments from roysviewfrom

import requests 
import csv
from bs4 import BeautifulSoup
# 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0'
}

def extract_pre_match_urls(sitemap_url):
    response = requests.get(sitemap_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve sitemap: {sitemap_url}")
        return []

    soup = BeautifulSoup(response.content, 'xml')
    loc_tags = soup.find_all('loc')

    # Filter URLs containing 'pre-match-view'
    filtered_links = [tag.text for tag in loc_tags if 'pre-match-view' in tag.text]
    
    return filtered_links

# Function to scrape data from a match page
def scrape_comments(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}") 
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract team name from the <title> tag
    title_tag = soup.find("title")
    if title_tag:
        title_text = title_tag.get_text()
        team_name = title_text.split("from ")[-1].split(" —")[0].strip()
    else:
        team_name = "Unknown"

    # Extract published date from meta tag
    date_tag = soup.find("meta", {"property": "article:published_time"})
    published_date = date_tag["content"].split("T")[0] if date_tag else "Unknown"

    # Find the article containing the comments
    article = soup.find("article", class_="page-content-single small single")
    
    # Extract comments only from this article
    if article:
        comment_paragraphs = article.find_all("p")
        # Possible will need to do more comment clean up here for unusual characters. 
        comments = [p.get_text(strip=True).replace("\xa0", " ") for p in comment_paragraphs if p.get_text(strip=True)]
    else:
        comments = []  # If article is not found, return an empty list
        
    # Structure the extracted data
    data_entries = []
    for comment in comments:
        data_entries.append({
            "team": team_name,
            "url": url,
            "published_date": published_date,
            "comment": comment
        })

    return data_entries

# Example URL (replace with actual URLs you want to scrape)
# example_url = "https://roysviewfrom.com/2015/01/22/pre-match-view-from-preston/"

def get_comments_from_url(urls):
        comments_data = []
        for i, url in enumerate(urls):
                try:
                        comments = scrape_comments(url)  # Ensure this returns a list of comments
                        if comments:
                                comments_data.extend(comments)  # Extend instead of append to avoid nested lists
                                print(f"Processed {i+1}/{len(urls)}: {url}")
                except Exception as e:
                        print(f"Failed to scrape {url}: {e}")
        print(f"Collected {len(comments_data)} comments.")
        return comments_data


def save_comments_to_csv(comments_data, filename="comments.csv"):
    # Define the CSV column headers
    fieldnames = ["team", "url", "published_date", "comment"]
    
    # Open the file in write mode ('w'), which overwrites the file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header (this will happen every time since we're using 'w')
        writer.writeheader()
        
        # Write each comment data as a row
        for comment in comments_data:
            writer.writerow(comment)

sitemap1_url = "https://roysviewfrom.com/post-sitemap.xml"
sitemap2_url = "https://roysviewfrom.com/post-sitemap2.xml"

# sm2urls = extract_pre_match_urls(sitemap2_url)
urls = extract_pre_match_urls(sitemap1_url) + extract_pre_match_urls(sitemap2_url)
comments_data = get_comments_from_url(urls)
save_comments_to_csv(comments_data)

