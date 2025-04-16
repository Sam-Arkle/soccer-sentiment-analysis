import requests 
import csv
import time
from bs4 import BeautifulSoup
from scraper_fbref_match_page import get_fbref_match_data

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def generate_season_urls(base_url, team_id, team_name, start_year, end_year):
    season_urls = []
    for year in range(start_year, end_year + 1):
        season_url = f"{base_url}/{team_id}/{year}-{year+1}/{team_name}-Stats"
        season_urls.append(season_url)
    return season_urls

def scrape_match_reports(session, season_urls):
    base_url = "https://fbref.com"
    all_match_report_urls = []
    for season_url in season_urls:
        retry_count = 0
        while retry_count < 5:
            response = session.get(season_url, headers=headers, timeout=50)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                match_report_links = soup.find_all('a', string="Match Report")
                for link in match_report_links:
                    match_report_url = link.get('href')
                    if match_report_url and not match_report_url.startswith(('http', 'https')):
                        match_report_url = base_url + match_report_url
                    all_match_report_urls.append(match_report_url)
                break
            elif response.status_code == 429:
                print(f"Rate limit hit for {season_url}. Retrying after a delay...")
                retry_count += 1
                wait_time = 2 ** retry_count
                print(f"Waiting for {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed to retrieve {season_url}. Status code: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                break
        if retry_count == 5:
            print(f"Max retries reached for {season_url}. Moving on to next season.")
    return all_match_report_urls

def extract_match_details(url):
    match_details = url.rstrip('/').split('/')[-1]
    return match_details

def save_to_csv(data, filename="match_statistics_v2.csv"):
    if not data:
        print("No data to write to CSV.")
        return
    keys = data[0].keys()
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
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

match_data = []
for url in match_report_urls:
    print(f"Scraping the data from {url}")
    time.sleep(10)  # For rate limiting
    match_details = extract_match_details(url)
    match_stats = get_fbref_match_data(url, session=session)
    if match_stats:
        sheff = match_stats['sheffield_united']
        opp = match_stats['opponent']
        winner = "Won" if match_stats.get('winner', '').lower() == "sheffield united" else "Lost"
        entry = {
            'Match Details': match_details,
            'Opponent': opp.get('team', 'N/A'),
            'Winner': winner,
            'Sheffield United Goals': sheff.get('goals', 'N/A'),
            'Sheffield United Fouls Committed': sheff.get('Fouls Committed', 'N/A'),
            'Sheffield United Yellow Cards': sheff.get('Yellow Cards', 'N/A'),
            'Sheffield United Red Cards': sheff.get('Red Cards', 'N/A'),
            'Sheffield United Tackles Won': sheff.get('Tackles Won', 'N/A'),
            'Sheffield United Penalties Conceded': sheff.get('Penalties Conceded', 'N/A'),
            'Opponent Goals': opp.get('goals', 'N/A'),
            'Opponent Fouls Committed': opp.get('Fouls Committed', 'N/A'),
            'Opponent Yellow Cards': opp.get('Yellow Cards', 'N/A'),
            'Opponent Red Cards': opp.get('Red Cards', 'N/A'),
            'Opponent Tackles Won': opp.get('Tackles Won', 'N/A'),
            'Opponent Penalties Conceded': opp.get('Penalties Conceded', 'N/A')
        }
        match_data.append(entry)

save_to_csv(match_data)
