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
    # This function writes out the desired urls for the seasons
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
            response = session.get(season_url, headers=headers, timeout=50)
            
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

# Function to extract match details from URL
def extract_match_details(url):
    match_details = url.rstrip('/').split('/')[-1]  # The final component of the URL contains the match details
    return match_details

# Function to scrape match statistics
def scrape_match_statistics(session, url):
   
    response = session.get(url, headers=headers, timeout=50)
    if response.status_code != 200:
        print(f"Failed to retrieve {url} with status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table with the caption "Sheffield Utd Player Stats Table"
    table = soup.find('caption', string="Sheffield Utd Player Stats Table") #TODO make this team generic
    if not table:
        print(f"Table 'Sheffield Utd Player Stats Table' not found in {url}")
        return None

    # The parent of the caption is the table element
    table = table.find_parent('table')

    # Extract data from the summary row (tfoot)
    tfoot = table.find('tfoot')
    if not tfoot:
        print(f"No summary row found in the table for {url}")
        return None

    summary_row = tfoot.find('tr')

    # Define the statistics to extract
    stats = {
        'Fouls Committed': summary_row.find('td', {'data-stat': 'fouls'}).get_text(strip=True) if summary_row.find('td', {'data-stat': 'fouls'}) else None,
        'Yellow Cards': summary_row.find('td', {'data-stat': 'cards_yellow'}).get_text(strip=True) if summary_row.find('td', {'data-stat': 'cards_yellow'}) else None,
        'Red Cards': summary_row.find('td', {'data-stat': 'cards_red'}).get_text(strip=True) if summary_row.find('td', {'data-stat': 'cards_red'}) else None,
        'Tackles Won': summary_row.find('td', {'data-stat': 'tackles_won'}).get_text(strip=True) if summary_row.find('td', {'data-stat': 'tackles_won'}) else None,
        'Penalties Conceded': summary_row.find('td', {'data-stat': 'pens_conceded'}).get_text(strip=True) if summary_row.find('td', {'data-stat': 'pens_conceded'}) else None
    }


    return stats

def save_to_csv(data, filename="match_statistics.csv"):
    """Save match statistics data to a CSV file."""
    if not data:
        print("No data to write to CSV.")
        return
    
    keys = data[0].keys()  # Extract column names from the first entry
    
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()  # Write column headers
        writer.writerows(data)  # Write match data
    
    print(f"Data successfully saved to {filename}")

base_url = 'https://fbref.com/en/squads'
team_id = '1df6b87e'  # Sheffield United team ID
shu_team_name = 'Sheffield-United'
start_year = 2014
end_year = 2024

season_urls = generate_season_urls(base_url, team_id, shu_team_name, start_year, end_year)
session = requests.session()

match_report_urls = scrape_match_reports(session, season_urls)
print("Obtained the match urls")
# match_report_urls = ["https://fbref.com/en/matches/a54d05f3/Sheffield-United-Brentford-August-5-2017-Championship"]
match_data = []
for url in match_report_urls:
    print(f"Scraping the data from {url}")
    time.sleep(10) # For sake of rate limiting. Max is ten per minute
    match_details = extract_match_details(url)
    stats = scrape_match_statistics(session, url)
    
    if stats:
        match_entry = {
            'Match Details': match_details,
            'Fouls Committed': stats['Fouls Committed'],
            'Yellow Cards': stats['Yellow Cards'],
            'Red Cards': stats['Red Cards'],
            'Tackles Won': stats['Tackles Won'],
            'Penalties Conceded': stats['Penalties Conceded']
        }
        match_data.append(match_entry)
        
save_to_csv(match_data)
