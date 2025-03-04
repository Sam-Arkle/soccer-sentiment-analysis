import requests 
import csv
import time
from bs4 import BeautifulSoup
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0'
# }


def generate_season_urls(base_url, team_id, team_name, start_year, end_year):
    # This function writes out the desired urls
    season_urls = []
    
    for year in range(start_year, end_year + 1):
        # Construct the URL for each season
        season_url = f"{base_url}/{team_id}/{year}-{year+1}/{team_name}-Stats"
        season_urls.append(season_url)
    
    return season_urls

# Function to scrape match report links from a season page
def scrape_match_reports(session, season_urls):
    base_url = "https://fbref.com"
    all_match_report_urls = []
    

    for season_url in season_urls:
        retry_count = 0  # Track the number of retries
        
        while retry_count < 5:  # Try up to 5 times
            response = session.get(season_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                match_report_links = soup.find_all('a', string="Match Report")
                
                for link in match_report_links:
                    match_report_url = link.get('href')
                    if match_report_url and not match_report_url.startswith(('http', 'https')):
                        match_report_url = base_url + match_report_url
                    all_match_report_urls.append(match_report_url)
                
                break  # Successfully scraped, exit retry loop
            
            elif response.status_code == 429:
                print(f"Rate limit hit for {season_url}. Retrying after a delay...")
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff
                print(f"Waiting for {wait_time} seconds...")
                time.sleep(wait_time)  # Wait before retrying
            
            else:
                print(f"Failed to retrieve {season_url}. Status code: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                break  # Stop after 3 failed attempts
        
        if retry_count == 5:
            print(f"Max retries reached for {season_url}. Moving on to next season.")
    
    return all_match_report_urls

base_url = 'https://fbref.com/en/squads'
team_id = '1df6b87e'  # Sheffield United team ID
shu_team_name = 'Sheffield-United'
start_year = 2014
end_year = 2024

season_urls = generate_season_urls(base_url, team_id, shu_team_name, start_year, end_year)
session = requests.session()

match_report_urls = scrape_match_reports(session, season_urls)

for url in match_report_urls[:10]:
    print(url)
print(len(match_report_urls))
