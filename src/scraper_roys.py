# For scraping the comments from roysviewfrom

import requests 
import csv
from bs4 import BeautifulSoup

# sitemap2_url = "https://roysviewfrom.com/post-sitemap2.xml"

# sitemap2_response = requests.get(sitemap2_url)

# old_soup = BeautifulSoup(sitemap2_response.content, 'xml')

# # Find all <loc> tags (URLs in a sitemap are typically in <loc> tags)
# loc_tags = old_soup.find_all('loc')

# # Filter the URLs that contain 'pre-' in the text content
# old_links = [tag.text for tag in loc_tags if 'pre-match-view' in tag.text]

# sitemap_url = "https://roysviewfrom.com/post-sitemap.xml"
# sitemap_response = requests.get(sitemap_url)
# new_soup = BeautifulSoup(sitemap_response.content, "xml")
# new_loc_tags = new_soup.find_all('loc')
# new_links = [tag.text for tag in new_loc_tags if 'pre-match-view' in tag.text]

# I'll keep the urls stored as python lists for now. It will make the project easier to update as new data comes out. 
# But csvs would be a good solution for a bigger project. 
 
# Now just testing the concept before running for all the old links
# example = "https://roysviewfrom.com/2015/01/22/pre-match-view-from-preston/"
# ex_res = requests.get(example)
# soup = BeautifulSoup(ex_res.content, 'html5lib')
# comment_strongs = soup.find_all('strong')
# comments = [strong.get_text(strip=True) for strong in comment_strongs]

def extract_pre_match_urls(sitemap_url):
    response = requests.get(sitemap_url)
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
    response = requests.get(url)
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
                        comments = scrape_comments(urls)  # Ensure this returns a list of comments
                        if comments:
                                comments_data.extend(comments)  # Extend instead of append to avoid nested lists
                                print(f"Processed {i+1}/{len(urls)}: {url}")
                except Exception as e:
                        print(f"Failed to scrape {url}: {e}")
        print(f"Collected {len(comments_data)} comments.")
        return comments_data


def save_comments_to_csv(comments_data, filename="comments.csv"):
    # Define the CSV column headers
    fieldnames = ["team", "url", "date", "comments"]
    
    # Open the file in append mode, creating it if it doesn't exist
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header if the file is empty
        if file.tell() == 0:  # Check if the file is empty
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

